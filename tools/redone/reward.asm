%include 'native.inc'

org BLOB_ORIGIN
dw enemy_reward

enemy_reward:
    cmp word [bp + 2], LETHAL_RETURN
    jne .replay

    pusha
    push ds
    push es
    cmp byte [di + 0x16], 64
    jae .finish
    cmp byte [di + 0x17], 64
    jae .finish

    push word 100
    call_dgroup RNG_SEGMENT, RNG_OFFSET
    cmp ax, 70
    jae .finish

    current_depth
    cmp ax, 24
    jbe .depth_ok
    mov ax, 24
.depth_ok:
    push ax
    push word 2
    call_dgroup RNG_SEGMENT, RNG_OFFSET
    add ax, 6                     ; 6 weapon, 7 body armor
    push ax
    push word 0                   ; native subtype selection
    push word 0                   ; stock random enchantment and curse behavior
    call_dgroup ITEM_SEGMENT, ITEM_FACTORY
    test ax, ax
    jz .finish
    mov bx, ax
    mov bx, [bx]
    cmp byte [bx + 1], 0
    jne .enhance
    push ax                       ; discard the stock broken subtype
    call_dgroup ITEM_SEGMENT, 0x66
    jmp .finish
.enhance:
    push ax
    call_dgroup SHOP_SEGMENT, ENHANCE_OFFSET

    push ax                       ; native append takes ownership
    xor ax, ax
    mov al, byte [di + 0x16]
    push ax
    mov al, byte [di + 0x17]
    push ax
    push cs
    call near FLOOR_APPEND

.finish:
    pop es
    pop ds
    popa
.replay:
    mov al, byte [di + 0x16]
    sub ah, ah
    jmp near REWARD_CONTINUE
