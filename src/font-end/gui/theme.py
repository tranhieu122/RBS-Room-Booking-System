# gui/theme.py  –  Bảng màu dùng chung, phông chữ và các hàm tạo widget
from __future__ import annotations
import datetime as _dt
import tkinter as tk
from tkinter import ttk
from typing import Any, Optional, Callable

# ── Bảng màu: Giao diện trắng sạch sẽ ───────────────────────────────────────
C_DARK       = "#111827"
C_PRIMARY    = "#2563eb"
C_PRIMARY_H  = "#1d4ed8"
C_ACCENT     = "#3b82f6"
C_LIGHT      = "#93c5fd"
C_BG         = "#ffffff"
C_SURFACE    = "#ffffff"
C_BORDER     = "#e5e7eb"
C_SHADOW     = "#e5e7eb"
C_TEXT       = "#111827"
C_MUTED      = "#6b7280"
C_SUCCESS    = "#16a34a"
C_SUCCESS_BG = "#dcfce7"
C_WARNING    = "#b45309"
C_WARNING_BG = "#fef3c7"
C_DANGER     = "#db2777"
C_DANGER_BG  = "#fdf2f8"
C_INFO_BG    = "#eff6ff"
ROW_ODD      = "#ffffff"
ROW_EVEN     = "#f9fafb"


# ── Tỷ lệ Typography (Cơ sở 8pt, lưới 4px) ───────────────────────────────────
# Tiêu đề lớn : 20 bold  → Tiêu đề trang
# Phân đoạn   : 14 bold  → Tiêu đề phần / Tiêu đề hộp thoại
# Nội dung    : 10 reg   → Nội dung chính, nhãn (label)
# Nội dung đậm: 10 bold  → Nhấn mạnh
# Nhỏ         :  9 reg   → Chú thích, gợi ý
# Nhập liệu   : 11 reg   → Các ô nhập liệu
# Nút bấm     : 10 bold  → Các nút kêu gọi hành động (CTA)
F_TITLE   = ("Segoe UI", 20, "bold")
F_SECTION = ("Segoe UI", 14, "bold")
F_BODY    = ("Segoe UI", 10)
F_BODY_B  = ("Segoe UI", 10, "bold")
F_SMALL   = ("Segoe UI",  9)
F_INPUT   = ("Segoe UI", 11)
F_BTN     = ("Segoe UI", 10, "bold")


def apply_theme(style: ttk.Style) -> None:
    """Phiên bản cải tiến với kiểu dáng bảng tốt hơn."""
    style.theme_use("clam")

    # ── Cải tiến Treeview ───────────────────────────────────────────────────
    style.configure(
        "TV.Treeview.Heading",
        background="#f9fafb",
        foreground=C_TEXT,
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        padding=11,
        borderwidth=1,
    )
    style.map("TV.Treeview.Heading",
              background=[("active", "#eff6ff")],
              foreground=[("active", C_PRIMARY_H)])

    # CẢI TIẾN CHÍNH: Chiều cao hàng tốt hơn và màu sắc xen kẽ
    style.configure(
        "TV.Treeview",
        rowheight=44,  # TĂNG từ 36 - Dễ đọc hơn rất nhiều!
        font=F_BODY,
        foreground=C_TEXT,
        fieldbackground=C_SURFACE,
        background=C_SURFACE,
        borderwidth=0,
        relief="flat"
    )

    # CẢI TIẾN: Trạng thái di chuột (hover) và chọn (selection) tốt hơn
    style.map(
        "TV.Treeview",
        background=[
            ("selected", "#eff6ff"),
            ("focus", "#eff6ff")
        ],
        foreground=[
            ("selected", C_PRIMARY_H)
        ]
    )

    # ── Scrollbar ──────────────────────────────────────────────────────────
    style.configure("Vertical.TScrollbar",
                    background="#d1d5db",
                    troughcolor="#f9fafb",
                    arrowcolor=C_MUTED,
                    borderwidth=0,
                    relief="flat",
                    width=6)
    style.map("Vertical.TScrollbar",
              background=[("active", "#9ca3af"), ("!active", "#d1d5db")])

    # ── Combobox ───────────────────────────────────────────────────────────
    style.configure("TCombobox",
                    background=C_SURFACE,
                    fieldbackground=C_SURFACE,
                    foreground=C_TEXT,
                    bordercolor=C_BORDER,
                    arrowcolor=C_PRIMARY,
                    relief="flat",
                    padding=6)  # Increased padding
    style.map("TCombobox",
              fieldbackground=[("readonly", C_SURFACE)],
              bordercolor=[("focus", C_PRIMARY), ("!focus", C_BORDER)])


def btn(
    parent: tk.Misc,
    text: str,
    command: Any,
    variant: str = "primary",
    icon: str = "",
    **kw: Any
) -> tk.Button:
    """White-theme button wrapper with a crisp 1px border."""

    # Prepare label with icon
    # Color schemes
    colours = {
        "primary":  (C_PRIMARY,     C_PRIMARY_H,    "white"),
        "success":  ("#16a34a",     "#15803d",      "white"),
        "danger":   (C_DANGER,      "#be185d",      "white"),
        "ghost":    ("#ffffff",     "#f9fafb",      C_TEXT),
        "outline":  (C_SURFACE,     "#eff6ff",      C_PRIMARY),
        "accent":   (C_ACCENT,      C_PRIMARY_H,    "white"),
    }
    bg, bg_h, fg = colours.get(variant, colours["primary"])
    
    # Extra space for better visual balance
    label = f" {icon}  {text} " if icon else f" {text} "



    # Use default font if not provided
    if "font" not in kw:
        kw["font"] = F_BTN

    try:
        p_bg = parent.cget("bg")
    except Exception:
        p_bg = C_BG
    shadow_wrapper = tk.Frame(parent, bg=p_bg)

    shadow_layer = tk.Frame(shadow_wrapper, bg=C_BORDER, padx=1, pady=1)
    shadow_layer.pack(fill="both", expand=True)


    # Main button
    b = tk.Button(
        shadow_layer,
        text=label,
        bg=bg,
        fg=fg,
        relief="flat",
        cursor="hand2",
        padx=16,
        pady=9,
        bd=0,
        command=command,
        activebackground=bg_h,
        activeforeground=fg,
        **kw
    )
    b.pack(fill="both", expand=True)

    # Mouse event handlers for press animation
    def _press(_: Any) -> None:
        b.config(bg=bg_h)

    def _release(_: Any) -> None:
        b.config(bg=bg_h)

    def _leave(_: Any) -> None:
        b.config(bg=bg)


    b.bind("<ButtonPress-1>", _press)
    b.bind("<ButtonRelease-1>", _release)
    b.bind("<Leave>", _leave)

    # Attach the internal button to the wrapper for external control (like state="disabled")
    setattr(shadow_wrapper, "inner_btn", b)
    
    # Return the shadow wrapper (contains button inside)
    return shadow_wrapper


def search_box(
    parent: tk.Misc,
    var: tk.StringVar,
    width: int = 22,
    command: Any = None,
    placeholder: str = "",
    on_type: Any = None
) -> tk.Frame:
    """Improved search box with better focus state."""

    outer = tk.Frame(parent, bg=C_SURFACE, highlightthickness=2,
                     highlightbackground=C_BORDER)

    tk.Label(outer, text="🔍", bg=C_SURFACE,
             font=("Segoe UI", 10)).pack(side="left", padx=(8, 4))

    e = tk.Entry(outer, textvariable=var, relief="flat",
                 font=F_INPUT, width=width,
                 bg=C_SURFACE, fg=C_TEXT, insertbackground=C_PRIMARY)
    e.pack(side="left", ipady=6, padx=(0, 8), fill="x", expand=True)

    # Placeholder logic
    if placeholder and not var.get():
        var.set(placeholder)
        e.config(fg=C_MUTED)

        def _clear(_: Any) -> None:
            if var.get() == placeholder:
                var.set("")
                e.config(fg=C_TEXT)

        def _restore(_: Any) -> None:
            if not var.get():
                var.set(placeholder)
                e.config(fg=C_MUTED)

        e.bind("<FocusIn>", _clear, add="+")
        e.bind("<FocusOut>", _restore, add="+")

    # Focus handlers - IMPROVED
    def _in(_: Any) -> None:
        outer.config(highlightbackground=C_PRIMARY, highlightthickness=2)
        # Removed e.config(bg="#eef2ff") to prevent text disappearance
    
    def _out(_: Any) -> None:
        outer.config(highlightbackground=C_BORDER, highlightthickness=2)
        # Removed e.config(bg=C_SURFACE)
    
    e.bind("<FocusIn>", _in, add="+")
    e.bind("<FocusOut>", _out, add="+")

    if command is not None:
        e.bind("<Return>", lambda *_: command())

    if on_type is not None:
        _timer_id: list[str | None] = [None]

        def _handle_type(_e: Any) -> None:
            if _timer_id[0]:
                e.after_cancel(_timer_id[0])
            _timer_id[0] = e.after(300, on_type)

        e.bind("<KeyRelease>", _handle_type)

    return outer


def get_q(var: tk.StringVar, placeholder: str = "") -> str:
    """Returns sanitized search text, ignoring placeholder (case/strip robust)."""
    val = var.get().strip()
    p = placeholder.strip()
    if p and val.lower() == p.lower():
        return ""
    return val.lower()


def page_header(parent: tk.Misc, text: str, icon: str = "", subtitle: str = "") -> tk.Frame:
    frm = tk.Frame(parent, bg=C_BG)

    # Simple premium accent
    tk.Frame(frm, bg=C_PRIMARY, height=3).pack(fill="x")

    row = tk.Frame(frm, bg=C_BG)
    row.pack(fill="x", padx=20, pady=(12, 6))

    if icon:
        ic_bg = tk.Frame(row, bg="#eef2ff", padx=6, pady=2)
        ic_bg.pack(side="left", padx=(0, 10))
        tk.Label(ic_bg, text=icon, bg="#eef2ff",
                 font=("Segoe UI", 14)).pack()
    
    txt_f = tk.Frame(row, bg=C_BG)
    txt_f.pack(side="left")
    
    tk.Label(txt_f, text=text, bg=C_BG, fg=C_DARK,
             font=("Segoe UI", 16, "bold")).pack(anchor="w")
    
    if subtitle:
        tk.Label(txt_f, text=subtitle, bg=C_BG, fg=C_MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w")

    tk.Frame(frm, bg=C_BORDER, height=1).pack(fill="x", padx=20, pady=(0, 6))
    return frm

def dialog_header(parent: tk.Misc, title: str, subtitle: str = "", variant: str = "primary", icon: str = "") -> tk.Frame:
    """Clean white dialog header with variant accent color."""
    themes = {
        "primary": {"accent": C_PRIMARY},
        "success": {"accent": "#16a34a"},
        "danger":  {"accent": C_DANGER},
        "warning": {"accent": "#b45309"},
    }
    th = themes.get(variant, themes["primary"])
    
    hdr = tk.Frame(parent, bg=C_SURFACE, padx=24, pady=18,
                   highlightthickness=1, highlightbackground=C_BORDER)
    tk.Frame(hdr, bg=th["accent"], height=3).pack(fill="x", side="top", pady=(0, 15))
    
    content = tk.Frame(hdr, bg=C_SURFACE)
    content.pack(fill="x")
    
    if icon:
        ic_bg = tk.Frame(content, bg="#eff6ff", padx=8, pady=8)
        ic_bg.pack(side="left", padx=(0, 15))
        tk.Label(ic_bg, text=icon, bg="#eff6ff", fg=th["accent"], font=("Segoe UI", 16)).pack()
    
    txt_f = tk.Frame(content, bg=C_SURFACE)
    txt_f.pack(side="left", fill="both")
    
    tk.Label(txt_f, text=title.upper(), bg=C_SURFACE, fg=C_TEXT,
             font=("Segoe UI", 12, "bold")).pack(anchor="w")
    if subtitle:
        tk.Label(txt_f, text=subtitle, bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w")
                 
    return hdr


def make_card(
    parent: tk.Widget,
    padx: int = 20,
    pady: int = 16,
    shadow: bool = True,
    variant: str = "standard",
    clickable: bool = False,
    bg: str | None = None,
    **kw: Any
) -> tuple[tk.Frame, tk.Frame]:
    """White card with a stable border. Shadow is ignored to avoid fuzzy edges."""

    card_bg = bg if bg is not None else C_SURFACE
    outer = tk.Frame(parent, bg=card_bg, highlightthickness=1,
                     highlightbackground=C_BORDER)
    content = tk.Frame(outer, bg=card_bg, padx=padx, pady=pady, **kw)
    content.pack(fill="both", expand=True)

    if clickable:
        def _on_enter(_: Any) -> None:
            outer.config(highlightbackground="#bfdbfe")
            content.config(cursor="hand2")

        def _on_leave(_: Any) -> None:
            outer.config(highlightbackground=C_BORDER)
            content.config(cursor="arrow")

        content.bind("<Enter>", _on_enter)
        content.bind("<Leave>", _on_leave)
        outer.bind("<Enter>", _on_enter)
        outer.bind("<Leave>", _on_leave)

    return outer, content


def form_grid(parent: tk.Frame, fields: list[tuple[str, tk.StringVar, str, bool, str]]) -> tk.Frame:
    """
    Helper to layout forms in a consistent 2-column grid.
    fields = [("Label", var, icon, required, help_text), ...]
    """
    grid = tk.Frame(parent, bg=parent.cget("bg"))
    grid.pack(fill="both", expand=True, padx=10, pady=10)
    
    grid.columnconfigure(0, weight=1)
    grid.columnconfigure(1, weight=1)
    
    for i, (label, var, icon, req, help_txt) in enumerate(fields):
        row, col = divmod(i, 2)
        outer, _ = labeled_entry(grid, label, var, icon=icon, required=req, help_text=help_txt)
        outer.grid(row=row, column=col, sticky="ew", padx=15, pady=5)
        
    return grid



def make_tree(parent: tk.Misc, columns: tuple[str, ...] | list[str],
              headers: tuple[str, ...] | list[str],
              widths: tuple[int, ...] | list[int],
              height: int = 0) -> ttk.Treeview:
    if height:
        tree = ttk.Treeview(parent, style="TV.Treeview", columns=columns,
                            show="headings", height=height)
    else:
        tree = ttk.Treeview(parent, style="TV.Treeview", columns=columns,
                            show="headings")
    for col, hdr, w in zip(columns, headers, widths):
        tree.heading(col, text=hdr)
        tree.column(col, width=w, anchor="center", minwidth=40)
    _tag_cfg(tree)
    return tree


def _tag_cfg(tree: ttk.Treeview) -> None:
    tree.tag_configure("odd",       background=ROW_ODD)
    tree.tag_configure("even",      background=ROW_EVEN)
    tree.tag_configure("empty",     foreground=C_MUTED, font=("Segoe UI", 10, "italic"))
    tree.tag_configure("Da duyet",  background=C_SUCCESS_BG, foreground=C_TEXT)
    tree.tag_configure("Cho duyet", background=C_WARNING_BG, foreground=C_TEXT)
    tree.tag_configure("Tu choi",   background=C_DANGER_BG,  foreground=C_TEXT)
    tree.tag_configure("Da huy",    background="#f1f5f9",   foreground=C_TEXT)
    tree.tag_configure("Hoat dong", background=ROW_ODD, foreground=C_TEXT)
    tree.tag_configure("Bao tri",   background=C_WARNING_BG, foreground=C_TEXT)
    tree.tag_configure("Khoa",      background=C_DANGER_BG,  foreground=C_TEXT)


def fill_tree(tree: ttk.Treeview, rows: list[tuple[object, ...]],
              empty_msg: str = " Khong co du lieu") -> None:
    for item in tree.get_children():
        tree.delete(item)
    if not rows:
        cols = tree["columns"]
        placeholder = tuple([empty_msg] + [""] * (len(cols) - 1))
        tree.insert("", "end", values=placeholder, tags=["empty"])
        return
    for i, values in enumerate(rows):
        tags = ["odd" if i % 2 == 0 else "even"]
        status = str(values[-1]) if values else ""
        if status in ("Da duyet", "Cho duyet", "Tu choi", "Da huy",
                      "Hoat dong", "Bao tri", "Khoa"):
            tags.append(status)
        tree.insert("", "end", values=values, tags=tags)


def with_scrollbar(parent: tk.Misc, tree: ttk.Treeview) -> None:
    vsb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)  # type: ignore[arg-type]
    tree.configure(yscrollcommand=vsb.set)
    tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")

    # Mousewheel support for Treeview
    def _on_mousewheel(event: tk.Event) -> None:
        tree.yview_scroll(int(-1 * (event.delta / 120)), "units")

    tree.bind("<Enter>", lambda _: tree.bind_all("<MouseWheel>", _on_mousewheel))
    tree.bind("<Leave>", lambda _: tree.unbind_all("<MouseWheel>"))


class MiniProgressBar(tk.Canvas):
    """Thin horizontal progress bar drawn on Canvas."""
    def __init__(self, parent: tk.Widget, value: float, total: float,
                 color: str = C_PRIMARY, height: int = 5,
                 width: int = 160, bg: str | None = None) -> None:
        bg_color = bg if bg is not None else parent.cget("bg")
        super().__init__(parent, width=width, height=height,
                         bg=bg_color, highlightthickness=0)
        self._color  = color
        self._h      = height
        self._value  = value
        self._total  = total
        self.bind("<Configure>", lambda *_: self._draw())
        self.after(10, self._draw)

    def _draw(self) -> None:
        self.delete("all")
        w = self.winfo_width() or 160
        # Track (rounded appearance via rectangle)
        self.create_rectangle(0, 0, w, self._h, fill="#e2e8f0", outline="")
        if self._total > 0:
            fill_w = int(w * min(self._value / self._total, 1.0))
            if fill_w > 0:
                self.create_rectangle(0, 0, fill_w, self._h,
                                      fill=self._color, outline="")


# ── Shared UI helpers used by multiple screens ─────────────────────────────

def labeled_entry(
    parent: tk.Misc,
    label: str,
    var: tk.StringVar,
    icon: str = "",
    show: str = "",
    width: int = 32,
    required: bool = False,
    help_text: str = "",
    padx: int | tuple[int, int] = 0
) -> tuple[tk.Frame, tk.Entry]:
    """
    Enhanced version with:
    - Better focus visual feedback (background glow)
    - Optional required indicator
    - Optional help text
    """

    # Container for label + input
    outer_frame = tk.Frame(parent, bg=C_BG)
    outer_frame.pack(fill="x", pady=(8, 0), padx=padx)

    # Label with optional required indicator
    if label:
        label_text = label + (" *" if required else "")
        lbl = tk.Label(
            outer_frame,
            text=label_text,
            bg=C_BG,
            fg=C_MUTED,
            font=("Segoe UI", 8, "bold")
        )
        lbl.pack(anchor="w", pady=(0, 4))

    # Input frame with crisp 1px border
    border_frame = tk.Frame(outer_frame, bg=C_BORDER, padx=1, pady=1)
    border_frame.pack(fill="x")


    inner = tk.Frame(border_frame, bg=C_SURFACE, highlightthickness=1,
                     highlightbackground=C_BORDER)
    inner.pack(fill="both", expand=True)

    # Icon (optional)
    if icon:
        ic_frame = tk.Frame(inner, bg="#f8fafc", width=40)
        ic_frame.pack(side="left", fill="y")
        ic_frame.pack_propagate(False)
        tk.Label(ic_frame, text=icon, bg="#f8fafc",
                 font=("Segoe UI", 11), fg=C_PRIMARY).pack(expand=True)

    # Entry field
    entry = tk.Entry(
        inner,
        textvariable=var,
        width=width,
        show=show,
        font=F_INPUT,
        relief="flat",
        bg=C_SURFACE,
        fg=C_TEXT,
        insertbackground=C_PRIMARY,
        bd=0
    )
    entry.pack(
        side="left",
        padx=(8 if icon else 12, 12),
        pady=7,
        fill="x",
        expand=True
    )

    # Focus event handlers - KEY IMPROVEMENT
    def _focus_in(_: Any) -> None:
        # Change border color to primary + light background glow
        border_frame.config(bg=C_PRIMARY)
        inner.config(bg="#eef2ff", highlightbackground=C_PRIMARY)
        entry.config(bg="#eef2ff")
        if icon:
            ic_frame.config(bg="#eef2ff")

    def _focus_out(_: Any) -> None:
        # Reset to normal
        border_frame.config(bg=C_BORDER)
        inner.config(bg=C_SURFACE, highlightbackground=C_BORDER)
        entry.config(bg=C_SURFACE)
        if icon:
            ic_frame.config(bg="#f8fafc")


    entry.bind("<FocusIn>", _focus_in, add="+")
    entry.bind("<FocusOut>", _focus_out, add="+")

    # Help text (optional)
    if help_text:
        hint = tk.Label(
            outer_frame,
            text=help_text,
            bg=C_BG,
            fg="#94a3b8",
            font=F_SMALL
        )
        hint.pack(anchor="w", pady=(2, 0))

    return outer_frame, entry

def search_box(parent: tk.Misc, var: tk.StringVar, placeholder: str = "Search...", 
               width: int = 30, on_type: Optional[Callable] = None) -> tk.Frame:
    """Standardized search input with icon and focus effects."""
    outer = tk.Frame(parent, bg=C_BG)
    
    border = tk.Frame(outer, bg=C_BORDER, padx=1, pady=1)
    border.pack(fill="x")
    
    inner = tk.Frame(border, bg=C_SURFACE)
    inner.pack(fill="both", expand=True)
    
    tk.Label(inner, text="🔍", bg=C_SURFACE, fg=C_MUTED, font=("Segoe UI", 10)).pack(side="left", padx=(10, 5))
    
    ent = tk.Entry(inner, textvariable=var, width=width, font=("Segoe UI", 10),
                   relief="flat", bg=C_SURFACE, fg=C_TEXT, bd=0)
    ent.pack(side="left", padx=5, pady=8, fill="x", expand=True)
    
    if placeholder:
        def _on_focus_in(_: Any) -> None:
            border.config(bg=C_PRIMARY)
            inner.config(bg="#eef2ff")
            ent.config(bg="#eef2ff")
            if var.get() == placeholder:
                var.set("")
        
        def _on_focus_out(_: Any) -> None:
            border.config(bg=C_BORDER)
            inner.config(bg=C_SURFACE)
            ent.config(bg=C_SURFACE)
            if not var.get():
                var.set(placeholder)
                
        ent.bind("<FocusIn>", _on_focus_in)
        ent.bind("<FocusOut>", _on_focus_out)
        if not var.get():
            var.set(placeholder)

    if on_type:
        var.trace_add("write", lambda *_: on_type())

    return outer

def status_badge(parent: tk.Misc, text: str, bg: str = C_SURFACE) -> tk.Label:
    """Pill-shaped status chip with soft Indigo-tuned colors."""
    PRESETS: dict[str, tuple[str, str]] = {
        "Hoat dong": ("#dcfce7", "#15803d"),
        "Da duyet":  ("#dcfce7", "#15803d"),
        "Cho duyet": ("#fef3c7", "#b45309"),
        "Da huy":    ("#f1f5f9", "#64748b"),
        "Bao tri":   ("#fef3c7", "#b45309"),
        "Tu choi":   ("#fdf2f8", "#db2777"),
        "Huy":       ("#f1f5f9", "#64748b"),
        "Du kien":   ("#eef2ff", "#4f46e5"),
        "Lich day":  ("#dcfce7", "#15803d"),
        "Khoa":      ("#fdf2f8", "#db2777"),
        "Hong":      ("#fdf2f8", "#db2777"),
        "Admin":     ("#eef2ff", "#4f46e5"),   # Indigo chip for Admin
        "Giang vien":("#dcfce7", "#15803d"),
        "Sinh vien": ("#fef9c3", "#854d0e"),
    }
    chip_bg, chip_fg = PRESETS.get(text, ("#f1f5f9", C_MUTED))
    return tk.Label(parent, text=f" {text} ",
                    bg=chip_bg, fg=chip_fg,
                    font=("Segoe UI", 8, "bold"),
                    padx=2, pady=2)


def pw_strength_bar(parent: tk.Misc, var: tk.StringVar,
                    bg: str = C_SURFACE) -> tk.Frame:
    """Returns a frame containing a live password-strength indicator."""
    frame = tk.Frame(parent, bg=bg)
    bar_bg = tk.Frame(frame, bg="#e2e8f0", height=5)
    bar_bg.pack(fill="x", pady=(3, 0))
    bar_fill = tk.Frame(bar_bg, bg="#e2e8f0", height=5)
    bar_fill.place(x=0, y=0, relheight=1.0, relwidth=0)
    lbl = tk.Label(frame, text="", bg=bg, fg=C_MUTED,
                   font=("Segoe UI", 8))
    lbl.pack(anchor="w")

    def _update(*_: Any) -> None:
        pw = var.get()
        length = len(pw)
        score = 0
        if length >= 6:  score += 1
        if length >= 10: score += 1
        import re
        if re.search(r"[A-Z]", pw): score += 1
        if re.search(r"[0-9]", pw): score += 1
        if re.search(r"[^A-Za-z0-9]", pw): score += 1
        levels = [
            (0,  0.0,  "#e2e8f0", ""),
            (1,  0.2,  "#ec4899", "Rat yeu"),
            (2,  0.4,  "#f97316", "Yeu"),
            (3,  0.6,  "#eab308", "Trung binh"),
            (4,  0.8,  "#22c55e", "Manh"),
            (5,  1.0,  "#16a34a", "Rat manh"),
        ]
        _, rel, color, text = levels[min(score, 5)] # type: ignore
        bar_fill.place(relwidth=rel)
        bar_fill.config(bg=color)
        lbl.config(text=text, fg=color if text else C_MUTED)

    var.trace_add("write", _update)
    return frame


def eye_toggle(parent: tk.Misc, entry: tk.Entry,
               bg: str = C_SURFACE) -> tk.Label:
    """Eye icon that toggles password visibility. Place it inside entry's row."""
    _shown = [False]
    lbl = tk.Label(parent, text="👁", bg=bg, fg=C_MUTED,
                   font=("Segoe UI", 11), cursor="hand2")

    def _toggle(_: Any = None) -> None:
        _shown[0] = not _shown[0]
        entry.config(show="" if _shown[0] else "*")
        lbl.config(fg=C_PRIMARY if _shown[0] else C_MUTED)

    lbl.bind("<Button-1>", _toggle)
    return lbl


def toast(master: tk.Misc, message: str, kind: str = "success",
          duration_ms: int = 2800) -> None:
    """Show a short non-blocking toast notification at the bottom-right.
    kind: "success" | "error" | "info" | "warning"
    """
    COLORS = {
        "success": ("#dcfce7", "#15803d", "✔"),
        "error":   ("#fdf2f8", "#db2777", "✖"),
        "info":    ("#dbeafe", "#1d4ed8", "ℹ"),
        "warning": ("#fef3c7", "#b45309", "⚠"),
    }
    bg, fg, icon = COLORS.get(kind, COLORS["info"])

    # Find the root window
    root = master.winfo_toplevel()  # type: ignore[union-attr]

    popup = tk.Toplevel(root)
    popup.overrideredirect(True)
    popup.attributes("-topmost", True) # type: ignore
    popup.configure(bg=bg)

    frame = tk.Frame(popup, bg=bg, padx=14, pady=10,
                     highlightthickness=1, highlightbackground=fg)
    frame.pack()
    tk.Label(frame, text=icon, bg=bg, fg=fg,
             font=("Segoe UI", 12)).pack(side="left", padx=(0, 8))
    tk.Label(frame, text=message, bg=bg, fg=fg,
             font=("Segoe UI", 10, "bold"), wraplength=320).pack(side="left")

    def _place() -> None:
        popup.update_idletasks()
        rx = root.winfo_x() + root.winfo_width()
        ry = root.winfo_y() + root.winfo_height()
        pw, ph = popup.winfo_width(), popup.winfo_height()
        popup.geometry(f"+{rx - pw - 20}+{ry - ph - 40}")

    popup.after(10, _place)
    popup.after(duration_ms, popup.destroy)


def tooltip(widget: tk.Widget, text: str) -> None:
    """Attach a lightweight hover tooltip to a widget."""
    tip: list[tk.Toplevel | None] = [None]

    def _show(_: Any = None) -> None:
        if tip[0] or not widget.winfo_exists():
            return
        x = widget.winfo_rootx() + widget.winfo_width() // 2
        y = widget.winfo_rooty() + widget.winfo_height() + 6
        popup = tk.Toplevel(widget)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)  # type: ignore[arg-type]
        frame = tk.Frame(popup, bg="#1e1b4b", padx=9, pady=5,
                         highlightthickness=1, highlightbackground="#4f46e5")
        frame.pack()
        tk.Label(frame, text=text, bg="#1e1b4b", fg="#e0e7ff",
                 font=("Segoe UI", 8)).pack()
        popup.update_idletasks()
        pw = popup.winfo_width()
        popup.geometry(f"+{x - pw // 2}+{y}")
        tip[0] = popup

    def _hide(_: Any = None) -> None:
        if tip[0]:
            try:
                tip[0].destroy()
            except Exception:
                pass
            tip[0] = None

    widget.bind("<Enter>", _show, add="+")
    widget.bind("<Leave>", _hide, add="+")


def confirm_dialog(root: tk.Misc, title: str, message: str,
                   kind: str = "primary",
                   ok_text: str = "Đồng ý", cancel_text: str | None = "Hủy") -> bool:
    """Titanium-styled custom modal dialog with scrim overlay."""
    dlg = ScrimmedDialog(root, title=title)
    
    # Palette based on kind
    themes = {
        "primary": {"variant": "primary", "icon": "ℹ️"},
        "warning": {"variant": "warning", "icon": "⚠️"},
        "danger":  {"variant": "danger",  "icon": "🚨"},
    }
    th = themes.get(kind, themes["primary"])
    
    dlg.configure(bg=C_SURFACE)
    result = [False]

    # Header
    hdr = dialog_header(dlg, title=title, variant=th["variant"], icon=th["icon"])
    hdr.pack(fill="x")
    
    body = tk.Frame(dlg, bg=C_SURFACE, padx=24, pady=25)
    body.pack(fill="both", expand=True)

    tk.Label(body, text=message, bg=C_SURFACE, fg="#475569",
             font=("Segoe UI", 10), wraplength=350,
             justify="left", anchor="w").pack(fill="x", pady=(0, 20))

    btn_row = tk.Frame(body, bg=C_SURFACE)
    btn_row.pack(fill="x")

    def _ok() -> None:
        result[0] = True
        dlg.destroy()

    def _cancel() -> None:
        dlg.destroy()

    btn(btn_row, ok_text, _ok,
        variant="danger" if kind == "danger" else "primary").pack(side="right")
    if cancel_text:
        btn(btn_row, cancel_text, _cancel,
            variant="ghost").pack(side="right", padx=8)

    dlg.center_on_parent()
    dlg.bind("<Return>", lambda _: _ok())
    dlg.bind("<Escape>", lambda _: _cancel())
    dlg.wait_window()
    return result[0]



# ── Utility helpers ────────────────────────────────────────────────────────

def relative_time(dt_str: str) -> str:
    """Convert ISO datetime string to Vietnamese relative time.
    E.g. '2 phut truoc', '3 gio truoc', '1 ngay truoc'.
    """
    try:
        then = _dt.datetime.fromisoformat(str(dt_str))
        now  = _dt.datetime.now()
        secs = int((now - then).total_seconds())
        if secs < 60:
            return "Vua xong"
        elif secs < 3600:
            m = secs // 60
            return f"{m} phut truoc"
        elif secs < 86400:
            h = secs // 3600
            return f"{h} gio truoc"
        elif secs < 604800:
            d = secs // 86400
            return f"{d} ngay truoc"
        else:
            return then.strftime("%d/%m/%Y")
    except Exception:
        return str(dt_str)
class ScrimmedDialog(tk.Toplevel):
    """
    A Toplevel dialog with a nearly transparent white overlay.
    """
    def __init__(self, master: tk.Misc, title: str = "Dialog", **kwargs: Any) -> None:
        # Create the scrim (overlay)
        self.root = master.winfo_toplevel()
        self.scrim = tk.Toplevel(self.root)
        self.scrim.overrideredirect(True)
        self.scrim.attributes("-alpha", 0.08)
        self.scrim.configure(bg="#ffffff")
        
        # Position scrim to cover the root window
        self._reposition_scrim()
        
        # Create the actual dialog
        super().__init__(self.root, **kwargs)
        self.title(title)
        self.resizable(False, False)
        self.transient(self.root)
        self.grab_set()
        
        # Bind events to clean up scrim
        self.bind("<Destroy>", self._on_destroy)
        self._configure_bind_id = self.root.bind(
            "<Configure>",
            lambda _: self._reposition_scrim(),
            add="+",
        )

    def _reposition_scrim(self) -> None:
        try:
            if not self.root.winfo_exists() or not self.scrim.winfo_exists():
                return
            x = self.root.winfo_rootx()
            y = self.root.winfo_rooty()
            w = self.root.winfo_width()
            h = self.root.winfo_height()
            self.scrim.geometry(f"{w}x{h}+{x}+{y}")
            self.scrim.lift()
        except tk.TclError:
            return

    def _on_destroy(self, event: tk.Event) -> None:
        if event.widget == self:
            try:
                if self._configure_bind_id:
                    self.root.unbind("<Configure>", self._configure_bind_id)
                    self._configure_bind_id = None
                if self.scrim.winfo_exists():
                    self.scrim.destroy()
            except tk.TclError:
                pass

    def center_on_parent(self) -> None:
        self.update_idletasks()
        rx = self.root.winfo_rootx() + self.root.winfo_width() // 2
        ry = self.root.winfo_rooty() + self.root.winfo_height() // 2
        self.geometry(f"+{rx - self.winfo_width() // 2}+{ry - self.winfo_height() // 2}")


def animate_count(label: tk.Label, end_value: int,
                  duration_ms: int = 700, steps: int = 24) -> None:
    """Animate a label's text from 0 up to end_value over duration_ms."""
    if end_value <= 0:
        label.config(text="0")
        return
    interval = max(1, duration_ms // steps)
    step_size = max(1, end_value // steps)

    def _tick(current: int) -> None:
        if not label.winfo_exists():
            return
        label.config(text=str(current))
        if current < end_value:
            nxt = min(current + step_size, end_value)
            label.after(interval, lambda: _tick(nxt))

    label.after(60, lambda: _tick(0))


def section_label(parent: tk.Misc, text: str, bg: str = C_BG) -> tk.Label:
    """Small section separator label styled like a tab header."""
    return tk.Label(parent, text=text, bg=bg, fg=C_MUTED,
                    font=("Segoe UI", 8, "bold"), anchor="w")


def tooltip(widget: tk.Widget, text: str) -> None:
    """Attach a simple hover tooltip to any widget."""
    tip: list[Optional[tk.Toplevel]] = [None]

    def _show(_: Any = None) -> None:
        if tip[0] or not widget.winfo_exists():
            return
        # Calculate position
        x = widget.winfo_rootx() + widget.winfo_width() // 2
        y = widget.winfo_rooty() + widget.winfo_height() + 5

        tw = tk.Toplevel(widget)
        tw.overrideredirect(True)
        tw.attributes("-topmost", True)
        tw.configure(bg="#1e293b", padx=1, pady=1)

        inner = tk.Frame(tw, bg="#1e293b", padx=8, pady=4)
        inner.pack()
        tk.Label(inner, text=text, bg="#1e293b", fg="white",
                 font=("Segoe UI", 9)).pack()

        tw.update_idletasks()
        # Adjust x to center the tooltip
        tx = x - (tw.winfo_width() // 2)
        tw.geometry(f"+{tx}+{y}")
        tip[0] = tw

    def _hide(_: Any = None) -> None:
        if tip[0]:
            try:
                tip[0].destroy()
            except Exception:
                pass
            tip[0] = None

    widget.bind("<Enter>", _show, add="+")
    widget.bind("<Leave>", _hide, add="+")
    widget.bind("<Destroy>", _hide, add="+")


def MiniProgressBar(parent: tk.Misc, value: float, color: str = C_PRIMARY) -> tk.Frame:
    """A very small progress bar for dashboard stats."""
    bg = tk.Frame(parent, bg="#e2e8f0", height=4)
    fill = tk.Frame(bg, bg=color, height=4)
    fill.place(relx=0, rely=0, relwidth=min(value, 1.0), relheight=1.0)
    return bg


def toast(parent: tk.Widget, message: str, kind: str = "primary") -> None:
    """Show a brief animated message overlay at the bottom right."""
    root = parent.winfo_toplevel()
    tw = tk.Toplevel(root)
    tw.overrideredirect(True)
    tw.attributes("-topmost", True)

    colors = {
        "primary": ("#eef2ff", "#4f46e5"),
        "success": ("#dcfce7", "#15803d"),
        "danger":  ("#fef2f2", "#b91c1c")
    }
    bg, fg = colors.get(kind, colors["primary"])

    f = tk.Frame(tw, bg=fg, padx=1, pady=1)
    f.pack()
    inner = tk.Frame(f, bg=bg, padx=15, pady=8)
    inner.pack()

    tk.Label(inner, text=message, bg=bg, fg=fg, font=("Segoe UI", 10, "bold")).pack()

    tw.update_idletasks()
    x = root.winfo_rootx() + root.winfo_width() - tw.winfo_width() - 20
    y = root.winfo_rooty() + root.winfo_height() - tw.winfo_height() - 20
    tw.geometry(f"+{x}+{y}")

    tw.after(3000, tw.destroy)
