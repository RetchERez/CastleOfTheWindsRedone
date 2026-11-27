"""Install or restore an optional interface theme using verified game files."""

from hashlib import sha256
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory

CLASSIC_FILE = 'Classic.bin'
THEME_NAMES = {'warm': 'Warm Stone', 'dark': 'Dark Slate', 'classic': 'Classic'}
THEME_INDEX = 'interface.json'


def digest(data):
    return sha256(data).hexdigest()


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
    patch = (assets / entry['patch']).read_bytes()
    if digest(patch) != entry['patch_sha256']:
        raise ValueError('The interface patch is damaged. Download Setup again')
    result = apply_delta(original, patch)
    if digest(result) != entry['sha256']:
        raise ValueError('The themed game failed its integrity check')
    return result


def set_theme(installation, theme, assets, apply_delta):
    """Switch an existing install's game files, rolling back on a write failure."""
    if theme not in THEME_NAMES:
        raise ValueError('Choose Warm Stone, Dark Slate or Classic')
    index = json.loads((assets / THEME_INDEX).read_bytes())
    files = []
    for chapter in (1, 2):
        name = f'CASTLE{chapter}.EXE'
        candidates = [path for path in (installation / name, *installation.glob(f'Part {chapter} - */{name}'))
                      if path.is_file()]
        if len(candidates) != 1:
            raise ValueError('Choose the folder that contains both chapters')
        executable, = candidates
        if executable.is_symlink():
            raise ValueError('Choose an installation with ordinary game files')
        backup = executable.with_name(f'CASTLE{chapter} ' + CLASSIC_FILE)
        previous = executable.read_bytes()
        original = backup.read_bytes() if backup.is_file() else previous
        classic_hash = digest(original)
        if classic_hash not in index['bases']:
            raise ValueError(f'{name} does not match a supported Classic build')
        known = {classic_hash} | {variant['sha256'] for variant in index['bases'][classic_hash].values()}
        if digest(previous) not in known:
            raise ValueError(f'{name} was changed after installation')
        target = theme_output(original, theme, assets, apply_delta)
        files.append((executable, previous, target, backup, original))

    lock = installation / '.redone-theme-installing'
    receipt = installation / 'Interface Theme.txt'
    with lock.open('xb'):
        pass
    try:
        with TemporaryDirectory(prefix='.redone-theme-', dir=installation) as temp:
            staging = Path(temp)
            changed = []
            try:
                for path, previous, target, backup, original in files:
                    if path.read_bytes() != previous:
                        raise ValueError(f'{path.name} changed during theme setup')
                    if not backup.exists() and theme != 'classic':
                        with backup.open('xb') as handle:
                            handle.write(original)
                    if previous != target:
                        pending = staging / path.name
                        pending.write_bytes(target)
                        os.replace(pending, path)
                        changed.append((path, previous))
                pending = staging / receipt.name
                pending.write_text(THEME_NAMES[theme] + '\n', encoding='utf-8')
                os.replace(pending, receipt)
            except (ValueError, OSError):
                for path, original in reversed(changed):
                    rollback = staging / path.name
                    rollback.write_bytes(original)
                    os.replace(rollback, path)
                raise
    finally:
        lock.unlink()
