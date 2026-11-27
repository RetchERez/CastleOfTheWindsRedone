BITS 16
CPU 286
org BLOB_ORIGIN
dw ordinary_selection

ordinary_selection:
    ; The ordinary spawn call site changes its unused random-ID argument
    ; from -1 to -2. Scripts, summons and direct placements keep their calls.
    cmp word [bp + 6], -2
    jne .native
    push ax
    push bx
    push cx
    push si
    mov bx, [0x96]             ; map index, separate from difficulty depth
    cmp bx, MAP_COUNT
    jae .unchanged
    xor cx, cx
    mov cl, [cs:floor_policy + bx]
    or cx, cx
    jz .unchanged
    mov ax, [RNG_STATE]       ; sample low PRNG bits without an extra game roll
    xor al, ah
    cmp al, cl
    jae .unchanged
    ; Only replace an ordinary actor of comparable threat. Script and boss
    ; callers are unmarked and bypass this entire path.
    cmp di, CANDIDATE_LIMIT
    jae .unchanged
    mov bx, di
    mov cl, [cs:candidate_policy + bx]
    test al, 1
    jnz .beetle
    cmp word [0x96], BEETLE_ONLY_FLOOR
    je .beetle
    test cl, 1
    jz .unchanged
    mov ax, CENTIPEDE_ID
    jmp short .check_count
.beetle:
    test cl, 2
    jz .unchanged
    mov ax, BEETLE_ID
.check_count:
    ; The native actor list holds handles to living actors on this floor.
    ; Keep at most one live member of each new species.
    mov si, [ACTOR_LIST]
    test si, si
    jz .try
    mov bx, [si]
    test bx, bx
    jz .try
    mov cx, [bx]
    jcxz .try
    add bx, 4
.live:
    mov si, [bx]
    test si, si
    jz .next
    mov si, [si]
    test si, si
    jz .next
    cmp byte [si + 1], al
    je .unchanged
.next:
    add bx, 2
    loop .live
.try:
    push ax
    push cs
    call near 0
    test ax, ax
    jz .unchanged
    ; Retain the native copper generator for a minority of these creatures.
    ; The ordinary native loot check and the death/drop path remain in use.
    cmp byte [RNG_STATE + 3], 96
    jb .generated
    mov bx, ax
    mov bx, [bx]
    mov word [bx + 8], 0
.generated:
    pop si
    pop cx
    pop bx
    add sp, 2
    jmp near FACTORY_CONTINUE
.unchanged:
    pop si
    pop cx
    pop bx
    pop ax
.native:
    push di
    push cs
    call near 0
    jmp near FACTORY_CONTINUE
