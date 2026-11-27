BITS 16
CPU 286
org BLOB_ORIGIN
dw capture_begin, capture_outcome

capture_begin:
    mov ax, 0x24
    imul word [0x96]
    mov bx, ax
    mov word [bx + ROOM_FIELD], 0xc000
    jmp near ROOM_BEGIN + 9

; Values are grouped into eight-tile buckets after expanding one tile past
; the actual native room rectangle. This leaves four 3-bit fields in a word.
%macro coordinate 3
    mov cx, [bp - %1]
%if %2 = 0
    jcxz %%edge
    dec cx
%else
    cmp cx, 63
    jbe %%edge
    mov cx, 63
%endif
%%edge:
    shr cx, 3
%if %3 > 0
    shl cx, %3
%endif
    or ax, cx
%endmacro

%macro merge_bound 2
    mov cx, ax
    mov si, dx
    and cx, %1
    and si, %1
    cmp cx, si
    %2 %%keep
    and ax, (0xffff ^ %1)
    or ax, si
%%keep:
%endmacro

capture_outcome:
    or ax, ax
    jz .missing
    push ax
    push bx
    push cx
    push dx
    push si
    mov bx, [0x96]
    imul bx, 0x24
    mov dx, [bx + ROOM_FIELD]
    cmp dx, 0xb000
    je .complete

    mov ax, 0xa000
    coordinate 0x0a, 0, 0
    coordinate 0x14, 1, 3
    coordinate 0x0c, 0, 6
    coordinate 0x16, 1, 9

    mov cx, dx
    and cx, 0xf000
    cmp cx, 0xa000
    jne .store
    merge_bound 0x0007, jbe
    merge_bound 0x0038, jae
    merge_bound 0x01c0, jbe
    merge_bound 0x0e00, jae
.store:
    mov [bx + ROOM_FIELD], ax
.complete:
    pop si
    pop dx
    pop cx
    pop bx
    pop ax
    or ax, ax
    jmp near ROOM_OUTCOME + 4
.missing:
    push bx
    mov bx, [0x96]
    imul bx, 0x24
    mov word [bx + ROOM_FIELD], 0xb000
    pop bx
    or ax, ax
    jmp near ROOM_FAILURE
