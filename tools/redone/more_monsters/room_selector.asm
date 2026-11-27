; Input BX is the validated current floor ID. All registers are preserved.
; Set CF when ordinary substitution would be inside a protected room, or when
; the native script metadata is missing or incomplete on a scripted floor.
room_protected:
    cmp byte [cs:scripted_floors + bx], 0
    je .allow_plain
    push ax
    push bx
    push cx
    push dx
    push si
    imul bx, 0x24
    mov dx, [bx + ROOM_FIELD]
    mov ax, dx
    and ax, 0xf000
    cmp ax, 0xa000
    jne .block

    ; PUSHA preserved the native selector frame pointer at BP+4. Its saved
    ; BP was increased by one before being pushed by the native prologue.
    mov si, [bp + 4]
    mov si, [ss:si]
    dec si
    mov ax, [ss:si + 0x0e]
    cmp ax, 63
    ja .block
    shr ax, 3
    mov cx, dx
    and cx, 7
    cmp ax, cx
    jb .allow
    shl ax, 3
    mov cx, dx
    and cx, 0x0038
    cmp ax, cx
    ja .allow

    mov ax, [ss:si + 0x0c]
    cmp ax, 63
    ja .block
    shr ax, 3
    shl ax, 6
    mov cx, dx
    and cx, 0x01c0
    cmp ax, cx
    jb .allow
    shl ax, 3
    and dx, 0x0e00
    cmp ax, dx
    ja .allow
.block:
    stc
    jmp short .complete
.allow:
    clc
.complete:
    pop si
    pop dx
    pop cx
    pop bx
    pop ax
    ret
.allow_plain:
    clc
    ret
