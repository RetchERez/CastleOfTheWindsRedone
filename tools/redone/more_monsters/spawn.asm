BITS 16
CPU 286
org BLOB_ORIGIN
dw ordinary_selection

; Private locals inside a frame built after PUSHA. The caller's saved DI
; is the vanilla selector result. The saved AX cell carries a new handle.
%define FLOOR_ROW     [bp - 2]
%define NATIVE_XP     [bp - 4]
%define WEIGHT_TOTAL  [bp - 6]
%define TOTAL_LIMIT   [bp - 8]
%define RISK_LIMIT    [bp - 9]
%define NEW_COUNT     [bp - 10]
%define RISK_COUNT    [bp - 11]
%define CASTER_COUNT  [bp - 12]
%define REGEN_COUNT   [bp - 13]
%define PICKED_INDEX  [bp - 16]
%define WEIGHTS       [bp + si - 64]

ordinary_selection:
    cmp word [bp + 6], -2      ; ordinary picker marker, never used by scripts
    jne .native
    pusha
    mov bp, sp
    sub sp, 64
    mov bx, [0x96]
    cmp bx, MAP_COUNT
    jae .unchanged
    call room_protected
    jc .unchanged
%if PRISONER_FLAG
    cmp bx, 6                  ; Castle 4, including timed repopulation
    jne .gate
    cmp byte [PRISONER_FLAG], 1 ; native successful rescue is persisted
    jne .unchanged
%endif
.gate:
    mov ax, [RNG_STATE]
    xor al, ah
    cmp al, [cs:floor_probability + bx]
    jae .unchanged
    mov al, [cs:floor_total + bx]
    mov TOTAL_LIMIT, al
    mov al, [cs:floor_risk + bx]
    mov RISK_LIMIT, al
    mov al, SPECIES_COUNT
    mul bl
    add ax, floor_weights
    mov FLOOR_ROW, ax

    mov bx, [bp]               ; original DI from PUSHA
    cmp bx, FIRST_ID
    jae .unchanged
    shl bx, 1
    mov ax, [cs:stock_xp + bx]
    mov NATIVE_XP, ax
    mov word WEIGHT_TOTAL, 0
    mov byte NEW_COUNT, 0
    mov byte RISK_COUNT, 0
    mov byte CASTER_COUNT, 0
    mov byte REGEN_COUNT, 0
    xor si, si
.clear:
    mov byte WEIGHTS, 0
    inc si
    cmp si, SPECIES_COUNT
    jb .clear

    mov bx, [ACTOR_LIST]
    test bx, bx
    jz .counted
    mov bx, [bx]
    test bx, bx
    jz .counted
    mov cx, [bx]
    cmp cx, [bx + 2]            ; native actor list capacity
    ja .unchanged
    jcxz .counted
    add bx, 4
.live:
    mov si, [bx]
    test si, si
    jz .next
    mov si, [si]
    test si, si
    jz .next
    cmp word [si + 2], 0
    je .next
    xor ax, ax
    mov al, [si + 1]
    sub ax, FIRST_ID
    cmp ax, SPECIES_COUNT
    jae .next
    mov si, ax
    mov byte WEIGHTS, 0xff
    inc byte NEW_COUNT
    mov al, [cs:species_flags + si]
    test al, 1
    jz .caster
    inc byte RISK_COUNT
.caster:
    test al, 2
    jz .regen
    inc byte CASTER_COUNT
.regen:
    test al, 4
    jz .next
    inc byte REGEN_COUNT
.next:
    add bx, 2
    loop .live
.counted:
    mov al, NEW_COUNT
    cmp al, TOTAL_LIMIT
    jae .unchanged
    xor si, si
    mov bx, FLOOR_ROW
.weigh:
    cmp byte WEIGHTS, 0xff
    je .omit
    mov dl, [cs:bx + si]
    test dl, dl
    jz .omit
    mov ax, NATIVE_XP
    cmp al, [cs:species_min_xp + si]
    jb .omit
    cmp al, [cs:species_max_xp + si]
    ja .omit
    test ah, ah
    jnz .omit
    mov al, [cs:species_flags + si]
    test al, 1
    jz .check_caster
    mov ah, RISK_COUNT
    cmp ah, RISK_LIMIT
    jae .omit
.check_caster:
    test al, 2
    jz .check_regen
    cmp byte CASTER_COUNT, 1
    jae .omit
.check_regen:
    test al, 4
    jz .keep
    cmp byte REGEN_COUNT, 2
    jae .omit
.keep:
    mov WEIGHTS, dl
    xor dh, dh
    add WEIGHT_TOTAL, dx
    jmp short .next_weight
.omit:
    mov byte WEIGHTS, 0
.next_weight:
    inc si
    cmp si, SPECIES_COUNT
    jb .weigh
    mov ax, WEIGHT_TOTAL
    test ax, ax
    jz .unchanged
    xor bx, bx
    mov bl, [RNG_STATE + 2]
    mul bx                     ; range a sampled RNG byte across the weights
    mov al, ah
    mov ah, dl
    xor si, si
    xor dx, dx
.select:
    mov dl, WEIGHTS
    sub ax, dx
    jb .selected
    inc si
    cmp si, SPECIES_COUNT
    jb .select
    jmp short .unchanged
.selected:
    mov PICKED_INDEX, si
    lea ax, [si + FIRST_ID]
    push ax
    push cs
    call near 0
    test ax, ax
    jz .unchanged
    mov si, PICKED_INDEX
    mov dl, [RNG_STATE + 3]
    cmp dl, [cs:species_copper + si]
    jb .generated
    mov bx, ax
    mov bx, [bx]
    mov word [bx + 8], 0       ; skip the native chance for a low-value pocket
.generated:
    mov [bp + 14], ax
    mov sp, bp
    popa
    jmp near FACTORY_CONTINUE
.unchanged:
    mov sp, bp
    popa
.native:
    push di
    push cs
    call near 0
    jmp near FACTORY_CONTINUE
