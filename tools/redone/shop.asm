%include 'native.inc'

org BLOB_ORIGIN
dw initial_stock, replacement_stock, enhance

initial_stock:
    push ax
    push cs
    call near enhance
    mov si, ax
    or si, si
    jmp near STOCK_INIT_CONTINUE

replacement_stock:
    push ax
    push cs
    call near enhance
    mov si, ax
    or si, si
    jmp near STOCK_RESTOCK_CONTINUE

; Pascal one-argument far call. Returns the same item handle in AX.
enhance:
    push bp
    mov bp, sp
    sub sp, 0x110
    pusha
    push ds
    push es
    cld

    mov si, [bp + 6]
    test si, si
    jz .return
    mov bx, [si]
    test bx, bx
    jz .return
    cmp byte [bx], 6
    je .eligible
    cmp byte [bx], 7
    jne .return
.eligible:
    cmp byte [bx + 1], 0            ; never promote intentionally broken stock
    je .return
    cmp word [bx + 6], 0            ; preserve named and scripted gear
    jne .return
    mov al, [bx + 9]
    and al, 6
    mov [bp - 18], al              ; conditions remain separate from rarity
    cmp al, 6                       ; preserve previously uncursed stock
    je .return
    mov al, [bx + 0x0a]
    and al, 15
    cmp al, 12                      ; leave room for two possible attributes
    ja .return
    mov al, [bx]
    mov [bp - 12], al

    current_depth
    mov di, .early
    cmp ax, 5
    jl .roll_tier
    mov di, .middle
    cmp ax, 12
    jl .roll_tier
    mov di, .deep
.roll_tier:
    push word 100
    call_dgroup RNG_SEGMENT, RNG_OFFSET
    xor bx, bx
.threshold:
    cmp al, [cs:di + bx]
    jb .got_tier
    inc bx
    jmp short .threshold
.got_tier:
    test bx, bx
    jz .return
    mov [bp - 2], bx
    cmp byte [bp - 18], 4
    jne .roll_affix

    ; Cursed gear keeps its native name, stats and value. Its tier is
    ; drawn only after the game's validated equipment operation.
    mov ax, bx
    shl al, 3
    or al, 0x60
    mov bx, [si]
    and byte [bx + 0xb], 7
    or byte [bx + 0xb], al
    jmp .return

.roll_affix:
    push word 2
    call_dgroup RNG_SEGMENT, RNG_OFFSET
    mov [bp - 14], ax               ; first affix variant
    mov dx, [bp - 2]
    add dx, ax                      ; weapon modifier in the range 1–4
    mov bx, ax
    inc bx                         ; native to-hit or to-damage attribute
    cmp byte [bp - 12], 7
    jne .got_stat
    mov bx, 3                      ; armor value with native tooltip text
    shl dx, 1
.got_stat:
    mov [bp - 4], bx
    mov [bp - 6], dx

    ; Ask stock formatting for its localized base name without its prefix.
    mov bx, [si]
    mov al, [bx + 9]
    mov [bp - 10], al
    and byte [bx + 9], 0xf9
    or byte [bx + 9], 1
    lea ax, [bp - 0x90]
    push si
    push ax
    push word 1
    push word 1
    call_dgroup NAME_SEGMENT, NAME_FORMATTER
    mov si, [bp + 6]
    mov bx, [si]
    mov al, [bp - 10]
    mov [bx + 9], al

    lea si, [bp - 0x90]
    cmp word [ss:si], 'No'
    jne .strip_armor
    cmp word [ss:si + 2], 'rm'
    jne .strip_armor
    cmp word [ss:si + 4], 'al'
    jne .strip_armor
    cmp byte [ss:si + 6], ' '
    jne .strip_armor
    add si, 7
.strip_armor:
    cmp byte [bp - 12], 7
    jne .store_base
    cmp word [ss:si], 'Su'
    jne .store_base
    cmp word [ss:si + 2], 'it'
    jne .store_base
    cmp word [ss:si + 4], ' o'
    jne .store_base
    cmp word [ss:si + 6], 'f '
    jne .store_base
    add si, 8
.store_base:
    mov [bp - 16], si
    cld
    push ss
    pop es
    lea di, [bp - 0x110]
    mov bx, [bp - 2]
    shl bx, 1
    mov si, [cs:prefixes + bx]
    call .append_prefix

    ; Keep long original base names readable in the native inventory tile.
    mov si, [bp - 16]
    mov bx, si
    add bx, 13
.measure:
    cmp byte [ss:si], 0
    je .use_affix
    inc si
    cmp si, bx
    jb .measure
    jmp short .append_base
.use_affix:
    mov bx, [bp - 14]
    cmp byte [bp - 12], 6
    je .select_affix
    add bx, 2
.select_affix:
    shl bx, 1
    mov si, [cs:affixes + bx]
    call .append_prefix
.append_base:
    mov si, [bp - 16]
    mov cx, 36
.copy_base:
    ss lodsb
    test al, al
    jz .end_name
    stosb
    loop .copy_base
.end_name:
    mov byte [es:di], 0
    lea ax, [bp - 0x110]
    push ax
    call_dgroup STRING_SEGMENT, MAKE_NAME
    test ax, ax
    jz .return
    mov [bp - 8], ax

    mov ax, [bp - 4]
    mov dx, [bp - 6]
    call .add_attribute
    test ax, ax
    jz .release_name

    cmp word [bp - 2], 1
    je .commit
    mov ax, 1
    cmp word [bp - 4], 1
    jne .second_stat
    mov ax, 2
.second_stat:
    mov dx, [bp - 2]
    dec dx
    call .add_attribute

.commit:
    mov si, [bp + 6]
    mov bx, [si]
    mov ax, [bp - 8]
    mov [bx + 6], ax
    and byte [bx + 9], 0xf9
    or byte [bx + 9], 3             ; identified and native enchanted palette
    mov ax, [bp - 2]
    shl al, 3
    or al, 0xe0                    ; DiabloLoot tag plus visible flag
    and byte [bx + 0xb], 7
    or byte [bx + 0xb], al
    mov ax, [bp - 2]
    mov dx, 140
    mul dx
    add [bx + 2], ax
    adc word [bx + 4], 0
    jmp short .return

.release_name:
    push word [bp - 8]
    call_kernel 7
.return:
    pop es
    pop ds
    popa
    mov ax, [bp + 6]
    mov sp, bp
    pop bp
    retf 2

.append_prefix:
    cs lodsb
    test al, al
    jz .prefix_done
    stosb
    jmp short .append_prefix
.prefix_done:
    ret

.add_attribute:
    push word [bp + 6]
    push word 3                    ; apply when equipped, remove on unequip
    push ax
    push dx
    push word 0
    push word 0
    push word 0
    call_dgroup ITEM_SEGMENT, ADD_ATTRIBUTE
    ret

.early:  db 61, 92, 100, 100       ; common, enchanted, rare, legendary
.middle: db 47, 82, 97, 100
.deep:   db 31, 70, 93, 100

prefixes: dw 0, enchanted, rare, legendary
affixes:  dw keen, vicious, stout, warded
enchanted: db 'Enchanted ', 0
rare:      db 'Rare ', 0
legendary: db 'Legendary ', 0
keen:      db 'Keen ', 0
vicious:   db 'Vicious ', 0
stout:     db 'Stout ', 0
warded:    db 'Warded ', 0
