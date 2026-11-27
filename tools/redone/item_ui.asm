%include 'native.inc'

org BLOB_ORIGIN
dw choose_icon, reveal_on_equip

; The original selector has already computed CX. SI is the raw item.
choose_icon:
    push ax
    push bx
    push di
    cmp byte [si], 6
    je .eligible
    cmp byte [si], 7
    jne .resume
.eligible:
    mov al, [si + 0xb]
    mov ah, al
    and al, 0x60
    cmp al, 0x60
    jne .legacy
    test ah, 0x80                   ; a curse can hide both the text and icon
    jz .resume
    mov al, ah
    shr al, 3
    and ax, 3
    jmp .lookup

.legacy:                            ; v1.0 used native saved custom names
    mov al, [si + 9]
    and al, 7
    cmp al, 3
    jne .resume
    mov bx, [si + 6]
    test bx, bx
    jz .resume
    mov bx, [bx]
    test bx, bx
    jz .resume
    mov ax, 2
    cmp word [bx], 'Ra'
    jne .try_legendary
    cmp word [bx + 2], 're'
    jne .resume
    cmp byte [bx + 4], ' '
    je .lookup
    jmp short .resume
.try_legendary:
    mov ax, 3
    cmp word [bx], 'Le'
    jne .try_enchanted
    cmp word [bx + 2], 'ge'
    jne .resume
    cmp word [bx + 4], 'nd'
    jne .resume
    cmp word [bx + 6], 'ar'
    jne .resume
    cmp word [bx + 8], 'y '
    je .lookup
    jmp short .resume
.try_enchanted:
    mov ax, 1
    cmp word [bx], 'En'
    jne .resume
    cmp word [bx + 2], 'ch'
    jne .resume
    cmp word [bx + 4], 'an'
    jne .resume
    cmp word [bx + 6], 'te'
    jne .resume
    cmp word [bx + 8], 'd '
    jne .resume

.lookup:
    test ax, ax
    jz .resume
    mov di, ax
    shl di, 1
    mov bx, rarity_icons
.next:
    cmp word [cs:bx], 0
    je .resume
    cmp cx, [cs:bx]
    je .matched
    add bx, 8
    jmp short .next
.matched:
    mov cx, [cs:bx + di]
.resume:
    pop di
    pop bx
    pop ax
    push word [HINSTANCE_CELL]
    jmp near ICON_CONTINUE

; Never changes the native identification, condition or item effects.
reveal_on_equip:
    push ax
    cmp byte [si], 6
    je .eligible
    cmp byte [si], 7
    jne .done
.eligible:
    mov al, [si + 0xb]
    and al, 0x60
    cmp al, 0x60
    jne .done
    or byte [si + 0xb], 0x80
.done:
    pop ax
    test byte [si + 9], 1
    jmp near EQUIP_CONTINUE
