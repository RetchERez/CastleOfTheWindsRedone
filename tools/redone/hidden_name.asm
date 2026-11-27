%include 'native.inc'

org BLOB_ORIGIN
dw format_revealed_curse, compact_armor_name

; A cursed item's stock name field never contains its DiabloLoot tier.
; Prefix the native name only after the validated native equip operation.
format_revealed_curse:
    pusha
    push es
    cmp byte [bx], 6
    je .eligible
    cmp byte [bx], 7
    jne .done
.eligible:
    test byte [bx + 9], 4           ; cursed or uncursed, retain that native label
    jz .done
    mov al, [bx + 0xb]
    mov ah, al
    and al, 0xe0
    cmp al, 0xe0
    jne .done
    mov al, ah
    shr al, 3
    and ax, 3
    test ax, ax
    jz .done
    shl ax, 1
    mov si, ax
    mov si, [cs:prefixes + si]
    push ds
    pop es
    mov di, [bp + 0xa]
    cld
.copy:
    cs lodsb
    test al, al
    jz .advance
    stosb
    jmp short .copy
.advance:
    mov [bp + 0xa], di
.done:
    pop es
    popa
    test byte [bx + 9], 1
    jmp near NAME_CONTINUE

; Fit the revealed name and icon in the native paper-doll cell. The game's
; formatter has already advanced the output pointer past the curse label.
compact_armor_name:
    pusha
    push es
    mov bx, [bp - 6]
    cmp byte [bx], 7
    jne .done
    test byte [bx + 9], 4
    jz .done
    mov al, [bx + 0x0b]
    and al, 0xf8
    cmp al, 0xe8
    jb .done
    mov di, [bp + 0xa]
    cmp word [di], 'Su'
    jne .done
    cmp word [di + 2], 'it'
    jne .done
    cmp word [di + 4], ' o'
    jne .done
    cmp word [di + 6], 'f '
    jne .done
    lea si, [di + 8]
    push ds
    pop es
    cld
.copy:
    lodsb
    stosb
    test al, al
    jnz .copy
.done:
    pop es
    popa
    pop si
    pop di
    dec bp
    dec bp
    jmp near NAME_EPILOGUE

prefixes: dw 0, enchanted, rare, legendary
enchanted: db 'Enchanted ', 0
rare:      db 'Rare ', 0
legendary: db 'Legendary ', 0
