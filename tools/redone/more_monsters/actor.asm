BITS 16
CPU 286
org BLOB_ORIGIN
dw choose_turn, finish_ranged, choose_melee_slot

choose_turn:
    push bp
    mov bp, sp
    push ax
    push bx
    mov bx, [bp + 0x0e]
    mov bx, [bx]               ; native actor handle
    xor ax, ax
    mov al, [bx + 1]
    sub ax, FIRST_ID
    cmp ax, SPECIES_COUNT
    jae .ordinary
    mov bx, ax
    test byte [cs:turn_behavior + bx], 2
    jz .regen
    mov bx, [bp + 0x0e]
    mov bx, [bx]
    cmp byte [bx + 0x20], 0
    jne .ordinary
    mov byte [bx + 0x12], 1
    mov byte [bx + 0x13], 0
    jmp short .ordinary
.regen:
    test byte [cs:turn_behavior + bx], 4
    jz .ordinary
    pop bx
    pop ax
    pop bp
    jmp near NATIVE_REGEN
.ordinary:
    pop bx
    pop ax
    pop bp
    jmp near NATIVE_TURN

finish_ranged:
    push ax
    push bx
    xor ax, ax
    mov al, [di + 1]
    sub ax, FIRST_ID
    cmp ax, SPECIES_COUNT
    jae .replay
    mov bx, ax
    test byte [cs:turn_behavior + bx], 2
    jz .replay
    mov bx, [bp - 0x0a]       ; the native chosen ranged descriptor
    test byte [bx + 1], 1
    jz .replay
    cmp byte [di + 0x20], 0
    je .replay
    dec byte [di + 0x20]
    jnz .slow
    and byte [bx + 1], 0xfe   ; exhausted, unavailable for later ranged actions
    mov byte [bx + 3], 0
.slow:
%if SLOW_TYPE >= 0
    cmp byte [di + 1], SLOW_TYPE
    jne .replay
    cmp byte [di + 0x21], 0
    je .replay
    cmp word [PLAYER_SLOW], 0
    jne .replay
    pusha
    push es
    push word SLOW_QUEUE
    push word SLOW_OVERFLOW
    push word 6
    push word 0x40
    push word -20
    push word 0
    push word 0
    db 0x9a
    dw 0, 0xfffe             ; relocated to the native timed effect segment
    or ax, ax
    jz .status_done
    push word 0x40
    push word 20
    push word 0
    push word 0
    push word 0
    push word 1
    db 0x9a
    dw 0x070a, 0xfffe
.status_done:
    pop es
    popa
    ; A successfully queued Slow is now visible in the native player stat.
    cmp word [PLAYER_SLOW], 0
    je .replay
    mov byte [di + 0x21], 0
%endif
.replay:
    pop bx
    pop ax
    cmp word [bp - 0x0c], 0
    ret

choose_melee_slot:
    push bx
    mov al, [si + 0x13]       ; native rotation for ordinary creatures
    xor bh, bh
    mov bl, [si + 1]
    sub bx, FIRST_ID
    cmp bx, SPECIES_COUNT
    jae .selected
    test byte [cs:turn_behavior + bx], 2
    jz .selected
    xor al, al               ; casters reserve their second slot for ranged turns
.selected:
    pop bx
    ret
