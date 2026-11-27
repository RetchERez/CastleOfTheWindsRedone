bits 16
org ORIGIN

%macro import 1
    db 0x9a
%1: dw 0xffff, 0
%endmacro

%macro color 1
    push word (%1) >> 16
    push word (%1) & 0xffff
%endmacro

%macro args 1
    %assign arg %1 + 4
    %rep %1 / 2
        push word [bp + arg]
        %assign arg arg - 2
    %endrep
%endmacro

%if HAS_DIALOG
    dw dialog_open
%endif
%if HAS_FILL
    dw panel_fill
%endif
%if HAS_DRAWTEXT
    dw panel_drawtext
%endif
%if HAS_TEXTOUT
    dw panel_textout
%endif
%if HAS_TABBED
    dw status_text
%endif
%if HAS_DIALOG
    dw dialog_box_param, free_dialog_panel, free_dialog_well
    dw set_dialog_storage, get_dialog_storage, dialog_enabled
    dw dialog_move_ink, dialog_back_color, dialog_create_brush
%endif
%if HAS_FILL
    dw fill_create_brush, fill_original, fill_delete_brush
%endif
%if HAS_DRAWTEXT
    dw drawtext_original
%endif
%if HAS_TEXTOUT
    dw textout_original
%endif
%if HAS_TABBED
    dw status_old_ink, status_use_ink, status_use_back, status_native, status_restore_back, status_restore_ink
%endif
%if HAS_DRAWTEXT || HAS_TEXTOUT
    dw text_set_mode, text_set_color, text_restore_color, text_restore_mode
%endif
    dw caps_bits, caps_planes

%if HAS_DIALOG
%define DIALOG_USER 8
%define MSG_INITDIALOG 0x110
%define MSG_CTLCOLOR 0x19

; This frame remains alive for the entire modal dialog, including nested ones.
; struct DialogState { far original; HBRUSH panel; HBRUSH well; }
dialog_open:
    push bp
    mov bp, sp
    sub sp, 10
    mov ax, [bp + 6]
    mov [bp - 10], ax
    mov ax, [bp + 8]
    mov [bp - 8], ax
    mov word [bp - 6], 0
    mov word [bp - 4], 0
    push word [bp + 16]          ; hInstance
    push word [bp + 14]          ; template pointer, or MAKEINTRESOURCE
    push word [bp + 12]
    push word [bp + 10]          ; owner
    push cs
    push word dialog_proc
    push ss
    lea ax, [bp - 10]
    push ax
    import dialog_box_param
    mov [bp - 2], ax
    cmp word [bp - 6], 0
    je dialog_no_panel
    push word [bp - 6]
    import free_dialog_panel
dialog_no_panel:
    cmp word [bp - 4], 0
    je dialog_no_well
    push word [bp - 4]
    import free_dialog_well
dialog_no_well:
    mov ax, [bp - 2]
    mov sp, bp
    pop bp
    retf 12

dialog_proc:
    push bp
    mov bp, sp
    sub sp, 8
    push si
    push es
    cmp word [bp + 12], MSG_INITDIALOG
    jne dialog_read_state
    push word [bp + 14]
    push word DIALOG_USER
    push word [bp + 8]
    push word [bp + 6]
    import set_dialog_storage
    mov ax, [bp + 6]
    mov dx, [bp + 8]
    mov word [bp + 6], 0         ; Stock DialogBox passes a zero init param.
    mov word [bp + 8], 0
    jmp dialog_state
dialog_read_state:
    push word [bp + 14]
    push word DIALOG_USER
    import get_dialog_storage
dialog_state:
    test dx, dx
    jz dialog_default
    mov [bp - 8], ax
    mov [bp - 6], dx
    les si, [bp - 8]
    args 10
    call far [es:si]
    test ax, ax
    jnz dialog_return
    cmp word [bp + 12], MSG_CTLCOLOR
    jne dialog_return
    cmp word [bp + 8], 1         ; Edit
    je dialog_well_color
    cmp word [bp + 8], 2         ; List box
    je dialog_well_color
    cmp word [bp + 8], 4         ; Dialog
    je dialog_panel_color
    cmp word [bp + 8], 6         ; Static text
    jne dialog_default
dialog_panel_color:
    mov word [bp - 4], 4
    jmp dialog_colors
dialog_well_color:
    mov word [bp - 4], 6
dialog_colors:
    push word [bp + 10]
    call limited
    mov [bp - 2], ax
    push word [bp + 10]
    test ax, ax
    jnz dialog_limited_ink
    push word [bp + 6]
    import dialog_enabled
    test ax, ax
    jz dialog_muted_ink
    color INK
    jmp dialog_apply_ink
dialog_muted_ink:
    color SECONDARY
    jmp dialog_apply_ink
dialog_limited_ink:
    color INK_LOW
dialog_apply_ink:
    import dialog_move_ink
    push word [bp + 10]
    call dialog_color_value
    import dialog_back_color
    les si, [bp - 8]
    add si, [bp - 4]
    mov ax, es:[si]
    test ax, ax
    jnz dialog_return
    call dialog_color_value
    import dialog_create_brush
    les si, [bp - 8]
    add si, [bp - 4]
    mov es:[si], ax
    jmp dialog_return
dialog_default:
    xor ax, ax
dialog_return:
    pop es
    pop si
    mov sp, bp
    pop bp
    retf 10

dialog_color_value:
    pop cx
    cmp word [bp - 4], 4
    jne dialog_well_value
    cmp word [bp - 2], 0
    jne dialog_panel_low
    color PANEL
    jmp cx
dialog_panel_low:
    color PANEL_LOW
    jmp cx
dialog_well_value:
    cmp word [bp - 2], 0
    jne dialog_well_low
    color WELL
    jmp cx
dialog_well_low:
    color WELL_LOW
    jmp cx
%endif

%if HAS_FILL
panel_fill:
    push bp
    mov bp, sp
    sub sp, 4
    mov word [bp - 2], 0
    mov ax, [bp + 6]
    cmp ax, [WHITE_BRUSH]
    jne panel_fill_original
    push word [bp + 12]
    call limited
    test ax, ax
    jnz panel_fill_low
    color PANEL
    jmp panel_fill_create
panel_fill_low:
    color PANEL_LOW
panel_fill_create:
    import fill_create_brush
    test ax, ax
    jz panel_fill_original
    mov [bp - 2], ax
    mov [bp + 6], ax
panel_fill_original:
    args 8
    import fill_original
    cmp word [bp - 2], 0
    je panel_fill_return
    mov [bp - 4], ax
    push word [bp - 2]
    import fill_delete_brush
    mov ax, [bp - 4]
panel_fill_return:
    mov sp, bp
    pop bp
    retf 8
%endif

%if HAS_DRAWTEXT
panel_drawtext:
    push bp
    mov bp, sp
    sub sp, 10
    mov ax, [bp + 18]
    mov [bp - 10], ax
    call use_ink
    args 14
    import drawtext_original
    call restore_ink
    mov sp, bp
    pop bp
    retf 14
%endif

%if HAS_TEXTOUT
panel_textout:
    push bp
    mov bp, sp
    sub sp, 10
    mov ax, [bp + 16]
    mov [bp - 10], ax
    call use_ink
    args 12
    import textout_original
    call restore_ink
    mov sp, bp
    pop bp
    retf 12
%endif

%if HAS_DRAWTEXT || HAS_TEXTOUT
use_ink:
    push word [bp - 10]
    push word 1
    import text_set_mode
    mov [bp - 2], ax
    push word [bp - 10]
    call limited
    push word [bp - 10]
    test ax, ax
    jnz text_ink_low
    color INK
    jmp text_ink_apply
text_ink_low:
    color INK_LOW
text_ink_apply:
    import text_set_color
    mov [bp - 4], ax
    mov [bp - 6], dx
    ret
restore_ink:
    mov [bp - 8], ax
    push dx
    push word [bp - 10]
    push word [bp - 6]
    push word [bp - 4]
    import text_restore_color
    push word [bp - 10]
    push word [bp - 2]
    import text_restore_mode
    pop dx
    mov ax, [bp - 8]
    ret
%endif

%if HAS_TABBED
status_text:
    push bp
    mov bp, sp
    sub sp, 14
    push word [bp + 24]
    import status_old_ink
    mov [bp - 2], ax
    mov [bp - 4], dx
    push word [bp + 24]
    call limited
    mov [bp - 10], ax
    push word [bp + 24]
    test ax, ax
    jnz status_low_ink
    cmp word [bp - 2], 0xff
    je status_warning
    cmp word [bp - 2], 0xff00
    je status_boost
    color INK
    jmp status_set_ink
status_warning:
    color WARNING
    jmp status_set_ink
status_boost:
    color MAGIC
    jmp status_set_ink
status_low_ink:
    color INK_LOW
status_set_ink:
    import status_use_ink
    push word [bp + 24]
    cmp word [bp - 10], 0
    jne status_low_back
    color PANEL
    jmp status_set_back
status_low_back:
    color PANEL_LOW
status_set_back:
    import status_use_back
    mov [bp - 6], ax
    mov [bp - 8], dx
    args 20
    import status_native
    mov [bp - 12], ax
    mov [bp - 14], dx
    push word [bp + 24]
    push word [bp - 8]
    push word [bp - 6]
    import status_restore_back
    push word [bp + 24]
    push word [bp - 4]
    push word [bp - 2]
    import status_restore_ink
    mov ax, [bp - 12]
    mov dx, [bp - 14]
    mov sp, bp
    pop bp
    retf 20
%endif

limited:
    push bp
    mov bp, sp
    push si
    push word [bp + 4]
    push word 12
    import caps_bits
    mov si, ax
    push word [bp + 4]
    push word 14
    import caps_planes
    mul si
    cmp ax, 16
    mov ax, 0
    jae limited_done
    inc ax
limited_done:
    pop si
    pop bp
    ret 2
