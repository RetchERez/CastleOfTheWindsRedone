"""Install or restore an optional interface theme using verified game files."""

from hashlib import sha256
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory

CLASSIC_FILE = 'Classic.bak'
LEGACY_CLASSIC_FILE = 'Classic.bin'
THEME_NAMES = {'warm': 'Warm Stone', 'dark': 'Dark Slate', 'classic': 'Classic'}
THEME_INDEX = 'interface.json'


def digest(data):
    return sha256(data).hexdigest()


def apply_checked_patch(original, entry, assets, apply_delta):
    patch = (assets / entry['patch']).read_bytes()
    if digest(patch) != entry['patch_sha256']:
        raise ValueError('The interface patch is damaged. Download Setup again')
    result = apply_delta(original, patch)
    if digest(result) != entry['sha256']:
        raise ValueError('The themed game failed its integrity check')
    return result


def theme_output(original, theme, assets, apply_delta):
    """Return the verified theme bytes from an exact, supported Classic image."""
    if theme == 'classic':
        return original
    index = json.loads((assets / THEME_INDEX).read_bytes())
    identity = digest(original)
    try:
        entry = index['bases'][identity][theme]
    except KeyError as error:
        raise ValueError('The selected game build does not support this interface theme') from error
    return apply_checked_patch(original, entry, assets, apply_delta)


def set_theme(installation, theme, assets, apply_delta):
    """Switch an existing install's game files, rolling back on a write failure."""
    if theme not in THEME_NAMES:
        raise ValueError('Choose Warm Stone, Dark Slate or Classic')
    index = json.loads((assets / THEME_INDEX).read_bytes())
    changes = []
    for chapter in (1, 2):
        name = f'CASTLE{chapter}.EXE'
        directory = f'Castle{chapter}'
        repack = installation / 'Castle of the Winds 1+2' / 'Win3.1'
        candidates = [path for path in (installation / name, *installation.glob(f'Part {chapter} - */{name}'),
                      installation / directory / name, installation / 'Win3.1' / directory / name,
                      repack / directory / name) if path.is_file()]
        if len(candidates) != 1:
            raise ValueError('Choose the folder that contains both chapters')
        executable, = candidates
        if executable.is_symlink():
            raise ValueError('Choose an installation with ordinary game files')
        backup = executable.with_name(f'CASTLE{chapter} ' + CLASSIC_FILE)
        legacy = executable.with_name(f'CASTLE{chapter} ' + LEGACY_CLASSIC_FILE)
        if backup.is_symlink() or legacy.is_symlink():
            raise ValueError('Choose an installation with ordinary theme backups')
        backup_data = backup.read_bytes() if backup.is_file() else None
        legacy_data = legacy.read_bytes() if backup_data is None and legacy.is_file() else None
        previous = executable.read_bytes()
        original = next((data for data in (backup_data, legacy_data, previous) if data is not None))
        classic_hash = digest(original)
        if classic_hash not in index['bases']:
            raise ValueError(f'{name} does not match a supported Classic build')
        known = {classic_hash} | {variant['sha256'] for variant in index['bases'][classic_hash].values()}
        if upgrade := index.get('classic_upgrades', {}).get(classic_hash):
            original = apply_checked_patch(original, upgrade, assets, apply_delta)
            identity = digest(original)
            known.update((identity, *(variant['sha256'] for variant in index['bases'][identity].values())))
        if digest(previous) not in known:
            raise ValueError(f'{name} was changed after installation')
        target = theme_output(original, theme, assets, apply_delta)
        if target != previous:
            changes.append((executable, previous, target))
        if (theme != 'classic' or backup_data is not None or legacy_data is not None) and backup_data != original:
            changes.append((backup, backup_data, original))
        if legacy_data is not None:
            changes.append((legacy, legacy_data, None))

    lock = installation / '.redone-theme-installing'
    receipt = installation / 'Interface Theme.txt'
    with lock.open('xb'):
        pass
    try:
        with TemporaryDirectory(prefix='.redone-theme-', dir=installation) as temp:
            staging = Path(temp)
            changed = []
            try:
                for number, (path, previous, target) in enumerate(changes):
                    current = path.read_bytes() if path.exists() else None
                    if current != previous:
                        raise ValueError(f'{path.name} changed during theme setup')
                    pending = staging / str(number)
                    if target is None:
                        os.replace(path, pending)
                    else:
                        pending.write_bytes(target)
                        os.replace(pending, path)
                    changed.append((path, previous))
                pending = staging / receipt.name
                pending.write_text(THEME_NAMES[theme] + '\n', encoding='utf-8')
                os.replace(pending, receipt)
            except (ValueError, OSError):
                for path, original in reversed(changed):
                    if original is None:
                        path.unlink()
                    else:
                        rollback = staging / 'rollback'
                        rollback.write_bytes(original)
                        os.replace(rollback, path)
                raise
    finally:
        lock.unlink()
