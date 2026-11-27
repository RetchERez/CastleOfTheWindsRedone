bits 16
org ORIGIN

%define INV_CLASS 0xe2
%define ITEMS_CLASS 0xec
%define STATUS_CLASS 0xc0
%define LOG_CLASS 0xc8
%define TOOLBAR_CLASS 0xf4

%macro far_import 1
    db 0x9a
%1: dw 0xffff, 0
%endmacro

%macro role_color 3
    push word [bp + %3]
    call low_color_display
    test ax, ax
    jnz %%limited
    color %1
    jmp %%done
%%limited:
    color %2
%%done:
%endmacro

%macro color 1
    push word ((%1) >> 16)
    push word ((%1) & 0xffff)
%endmacro

%macro arguments 1
    %assign arg %1 + 4
    %rep %1 / 2
        push word [bp + arg]
        %assign arg arg - 2
    %endrep
%endmacro

%if CLASS_HOOK
    dw register_class, create_brush_class, register_original, delete_class_brush
    dw class_get_dc, class_release_dc, device_caps

register_class:
    push bp
    mov bp, sp
    sub sp, 4
    push si
    push es
    mov word [bp - 2], 0
    les si, [bp + 6]
    mov ax, es:[si + 22]
    cmp ax, INV_CLASS
    je register_panel
    cmp ax, ITEMS_CLASS
    je register_items
    cmp ax, STATUS_CLASS
    je register_panel
    cmp ax, LOG_CLASS
    je register_panel
    cmp ax, TOOLBAR_CLASS
    jne register_call
    call desktop_is_limited
    test ax, ax
    jnz register_panel_low
    color MAIN
    jmp register_create
register_panel:
    call desktop_is_limited
    test ax, ax
    jnz register_panel_low
    color PANEL
    jmp register_create
register_panel_low:
    color PANEL_LOW
    jmp register_create
register_items:
    call desktop_is_limited
    test ax, ax
    jnz register_items_low
    color WELL
    jmp register_create
register_items_low:
    color WELL_LOW
register_create:
    far_import create_brush_class
    test ax, ax
    jz register_call
    mov [bp - 2], ax
    les si, [bp + 6]
    xchg ax, es:[si + 16]
    mov [bp - 4], ax
register_call:
    arguments 4
    far_import register_original
    cmp word [bp - 2], 0
    je register_done
    les si, [bp + 6]
    mov dx, [bp - 4]
    mov es:[si + 16], dx
    test ax, ax
    jnz register_done
    push ax
    push word [bp - 2]
    far_import delete_class_brush
    pop ax
register_done:
    pop es
    pop si
    mov sp, bp
    pop bp
    retf 4

desktop_is_limited:
    push word 0
    far_import class_get_dc
    test ax, ax
    jz desktop_return
    push ax
    push ax
    call low_color_display
    pop dx
    push ax
    push word 0
    push dx
    far_import class_release_dc
    pop ax
desktop_return:
    ret

%else
    dw draw_text, rectangle, draw_icon
%if DOLL_HOOK
    dw doll_metafile
%endif
    dw set_mode, set_ink, text_original, restore_ink, restore_mode
    dw create_brush, select_brush, get_white_brush, restore_special_brush
    dw create_pen, select_pen, rectangle_original, restore_pen, delete_pen
    dw restore_brush, delete_brush, icon_original, create_icon_brush
    dw fill_icon_underlay, delete_icon_brush
    dw device_caps
%if DOLL_HOOK
    dw doll_save_dc, doll_enum, doll_restore_dc, doll_original, doll_play_record
%endif

draw_text:
    push bp
    mov bp, sp
    sub sp, 10
    test word [bp + 6], 0x0400     ; Skip the measurement-only DrawText calls.
    jnz draw_calculation
    push word [bp + 18]
    push word 1                  ; TRANSPARENT
    far_import set_mode
    mov [bp - 2], ax
    push word [bp + 18]
    role_color INK, INK_LOW, 18
    far_import set_ink
    mov [bp - 4], ax
    mov [bp - 6], dx
draw_calculation:
    arguments 14
    far_import text_original
    test word [bp + 6], 0x0400
    jnz draw_return
    mov [bp - 8], ax
    push dx
    push word [bp + 18]
    push word [bp - 6]
    push word [bp - 4]
    far_import restore_ink
    push word [bp + 18]
    push word [bp - 2]
    far_import restore_mode
    pop dx
    mov ax, [bp - 8]
draw_return:
    mov sp, bp
    pop bp
    retf 14

rectangle:
    push bp
    mov bp, sp
    sub sp, 12
    xor ax, ax
    mov [bp - 2], ax
    mov [bp - 4], ax
    mov [bp - 6], ax
    role_color WELL, WELL_LOW, 14
    far_import create_brush
    test ax, ax
    jz rectangle_draw
    mov [bp - 2], ax
    push word [bp + 14]
    push ax
    far_import select_brush
    test ax, ax
    jz rectangle_draw
    mov [bp - 4], ax
    push word 0
    far_import get_white_brush
    cmp ax, [bp - 4]
    je rectangle_border
    ; Preserve the game's selected-slot brush when it overrides the default.
    push word [bp + 14]
    push word [bp - 4]
    far_import restore_special_brush
    mov word [bp - 4], 0
    jmp rectangle_draw
rectangle_border:
    push word 0
    push word 1
    role_color BORDER, BORDER_LOW, 14
    far_import create_pen
    mov [bp - 6], ax
    test ax, ax
    jz rectangle_draw
    push word [bp + 14]
    push ax
    far_import select_pen
    mov [bp - 8], ax
rectangle_draw:
    arguments 10
    far_import rectangle_original
    mov [bp - 10], ax
    mov [bp - 12], dx
    cmp word [bp - 6], 0
    je rectangle_brush
    cmp word [bp - 8], 0
    je rectangle_delete_pen
    push word [bp + 14]
    push word [bp - 8]
    far_import restore_pen
rectangle_delete_pen:
    push word [bp - 6]
    far_import delete_pen
rectangle_brush:
    cmp word [bp - 4], 0
    je rectangle_delete_brush
    push word [bp + 14]
    push word [bp - 4]
    far_import restore_brush
rectangle_delete_brush:
    cmp word [bp - 2], 0
    je rectangle_done
    push word [bp - 2]
    far_import delete_brush
rectangle_done:
    mov ax, [bp - 10]
    mov dx, [bp - 12]
    mov sp, bp
    pop bp
    retf 10

draw_icon:
    push bp
    mov bp, sp
    sub sp, 10
%if ICON_BACKING
    cmp word [bp + 6], 0
    je draw_icon_original
    role_color 0xb5b5b5, BACKING_LOW, 12
    far_import create_icon_brush
    test ax, ax
    jz draw_icon_original
    mov [bp - 10], ax
    mov ax, [bp + 10]
    mov [bp - 8], ax
    add ax, 32
    mov [bp - 4], ax
    mov ax, [bp + 8]
    mov [bp - 6], ax
    add ax, 32
    mov [bp - 2], ax
    push word [bp + 12]
    push ss
    lea ax, [bp - 8]
    push ax
    push word [bp - 10]
    far_import fill_icon_underlay
    push word [bp - 10]
    far_import delete_icon_brush
%else
create_icon_brush equ 0
fill_icon_underlay equ 0
delete_icon_brush equ 0
%endif
draw_icon_original:
    arguments 8
    far_import icon_original
    mov sp, bp
    pop bp
    retf 8

%if DOLL_HOOK
doll_metafile:
    push bp
    mov bp, sp
    sub sp, 6
    push word [bp + 8]
    far_import doll_save_dc
    test ax, ax
    jz doll_stock
    mov [bp - 2], ax
    push word [bp + 8]
    call low_color_display
    push word [bp + 8]
    push word [bp + 6]
    push cs
    push word doll_record
    push word 0
    push ax                      ; limited-display flag carried to the callback
    far_import doll_enum
    mov [bp - 4], ax
    mov [bp - 6], dx
    push word [bp + 8]
    push word [bp - 2]
    far_import doll_restore_dc
    mov ax, [bp - 4]
    mov dx, [bp - 6]
    test ax, ax
    jnz doll_done
doll_stock:
    arguments 4
    far_import doll_original
doll_done:
    mov sp, bp
    pop bp
    retf 4

; Replay the native WMF commands. When a pen needs recoloring, copy just that
; record to the stack so the game's resource, geometry and masks stay intact.
doll_record:
    push bp
    mov bp, sp
    sub sp, 16
    push si
    push di
    push ds
    push es
    les si, [bp + 12]
    cmp word es:[si + 4], 0x02fa ; META_CREATEPENINDIRECT, fixed LOGPEN record
    jne doll_record_original
    cmp word es:[si], 8
    jne doll_record_original
    cmp word [bp + 6], 0
    jne doll_record_original
    cmp word es:[si + 14], 0
    jne doll_record_original
    cmp word es:[si + 12], 0
    je doll_record_outline
    cmp word es:[si + 12], 0x00ff
    jne doll_record_original
    cmp word es:[si + 6], 2     ; Native decorative dotted equipment guides.
    jne doll_record_original
    mov ax, DOLL_GUIDES & 0xffff
    mov dx, DOLL_GUIDES >> 16
    jmp doll_record_copy
doll_record_outline:
    mov ax, INK & 0xffff
    mov dx, INK >> 16
doll_record_copy:
    push es
    pop ds
    push ss
    pop es
    lea di, [bp - 16]
    mov cx, 8
    cld
    rep movsw
    mov [bp - 4], ax
    mov [bp - 2], dx
    push word [bp + 20]
    push word [bp + 18]
    push word [bp + 16]
    push ss
    lea ax, [bp - 16]
    push ax
    push word [bp + 10]
    jmp doll_record_draw
doll_record_original:
    push word [bp + 20]
    push word [bp + 18]
    push word [bp + 16]
    push word [bp + 14]
    push word [bp + 12]
    push word [bp + 10]
doll_record_draw:
    far_import doll_play_record
    pop es
    pop ds
    pop di
    pop si
    mov ax, 1
    mov sp, bp
    pop bp
    retf 16
%endif
%endif

; Near Pascal helper. The only caller-supplied value is a display DC.
low_color_display:
    push bp
    mov bp, sp
    push si
    push word [bp + 4]
    push word 12                 ; BITSPIXEL
    call get_device_caps
    mov si, ax
    push word [bp + 4]
    push word 14                 ; PLANES
    call get_device_caps
    mul si
    cmp ax, 16
    mov ax, 0
    jae low_color_return
    inc ax
low_color_return:
    pop si
    mov sp, bp
    pop bp
    ret 2

get_device_caps:
    push bp
    mov bp, sp
    push word [bp + 6]
    push word [bp + 4]
    far_import device_caps
    pop bp
    ret 4
