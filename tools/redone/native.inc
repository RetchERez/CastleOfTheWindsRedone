BITS 16
CPU 286

%macro call_dgroup 2
    db 0x9a
    dw %2
    dw 0xda00 + %1
%endmacro

%macro call_kernel 1
    db 0x9a
    dw 0xffff
    dw 0xe100 + %1
%endmacro

%macro current_depth 0
    mov ax, word [0x96]
    mov bx, 0x24
    mul bx
    mov bx, ax
    mov ax, word [bx + DEPTH_TABLE]
    test ax, ax
    jg %%positive
    mov ax, 1
%%positive:
%endmacro
