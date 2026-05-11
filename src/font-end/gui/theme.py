# gui/theme.py  –  shared palette, fonts, widget factories
from __future__ import annotations
import datetime as _dt
import tkinter as tk
from tkinter import ttk
from typing import Any

# ── Palette: Modern Indigo / Slate ──────────────────────────────────────────
# ── Palette: Modern Indigo / Slate ──────────────────────────────────────────
C_DARK       = "#0f172a"
C_PRIMARY    = "#4f46e5"
C_PRIMARY_H  = "#4338ca"
C_ACCENT     = "#6366f1"
C_LIGHT      = "#818cf8"
C_BG         = "#f8fafc"
C_SURFACE    = "#ffffff"
C_BORDER     = "#f1f5f9"
C_SHADOW     = "#e2e8f0"
C_TEXT       = "#1e293b"
C_MUTED      = "#64748b"
C_SUCCESS    = "#16a34a"
C_SUCCESS_BG = "#dcfce7"
C_WARNING    = "#b45309"
C_WARNING_BG = "#fef3c7"
C_DANGER     = "#db2777"
C_DANGER_BG  = "#fdf2f8"
C_INFO_BG    = "#eef2ff"
ROW_ODD      = "#f1f5f9"
ROW_EVEN     = "#f8fafc"

# ── Typography Scale (8pt base, 4px grid) ────────────────────────────────────
# Heading  : 20 bold  → page titles
# SubHead  : 14 bold  → section headers / dialog titles
# Body     : 10 reg   → content, labels
# BodyBold : 10 bold  → emphasis
# Small    :  9 reg   → captions, hints
# Input    : 11 reg   → form entries
# Button   : 10 bold  → CTAs
F_TITLE   = ("Segoe UI", 20, "bold")
F_SECTION = ("Segoe UI", 14, "bold")
F_BODY    = ("Segoe UI", 10)
F_BODY_B  = ("Segoe UI", 10, "bold")
F_SMALL   = ("Segoe UI",  9)
F_INPUT   = ("Segoe UI", 11)
F_BTN     = ("Segoe UI", 10, "bold")


def apply_theme(style: ttk.Style) -> None:
    """Call once at app start to configure all ttk styles."""
    style.theme_use("clam")

    # ── Treeview ──────────────────────────────────────────────────────────────
    style.configure("TV.Treeview.Heading",
                    background=C_PRIMARY, foreground="white",
                    font=F_BODY_B, relief="flat", padding=11)
    style.map("TV.Treeview.Heading",
              background=[("active", C_PRIMARY_H)])
    style.configure("TV.Treeview",
                    rowheight=36, font=F_BODY,
                    fieldbackground=C_BG, background=C_BG,
                    borderwidth=0, relief="flat")
    style.map("TV.Treeview",
              background=[("selected", "#e0e7ff")],
              foreground=[("selected", "#3730a3")])

    # ── Scrollbar (thin, minimal) ─────────────────────────────────────────────
    style.configure("Vertical.TScrollbar",
                    background=C_BORDER, troughcolor=C_BG,
                    arrowcolor=C_MUTED, borderwidth=0,
                    relief="flat", width=6)
    style.map("Vertical.TScrollbar",
              background=[("active", C_MUTED), ("!active", C_BORDER)])
    style.configure("Horizontal.TScrollbar",
                    background=C_BORDER, troughcolor=C_BG,
                    arrowcolor=C_MUTED, borderwidth=0,
                    relief="flat", width=6)

    # ── Combobox ──────────────────────────────────────────────────────────────
    style.configure("TCombobox",
                    background=C_SURFACE, fieldbackground=C_SURFACE,
                    foreground=C_TEXT, bordercolor=C_BORDER,
                    arrowcolor=C_PRIMARY, relief="flat", padding=4)
    style.map("TCombobox",
              fieldbackground=[("readonly", C_SURFACE)],
              bordercolor=[("focus", C_PRIMARY), ("!focus", C_BORDER)])

    # ── Button (ttk) ─────────────────────────────────────────────────────────
    style.configure("TButton",
                    background=C_PRIMARY, foreground="white",
                    font=F_BODY_B, relief="flat", padding=(12, 6))
    style.map("TButton",
              background=[("active", "#4338ca"), ("pressed", "#4338ca")])


def btn(parent: tk.Misc, text: str, command: Any, variant: str = "primary",
    icon: str = "", **kw: Any) -> tk.Button:
    """Themed button with smooth hover + press transitions."""
    label = f"{icon} {text}" if icon else text
    colours = {
        "primary": (C_PRIMARY,    C_PRIMARY_H,  "white"),
        "success": ("#16a34a",    "#15803d",    "white"),
        "danger":  (C_DANGER,     "#be185d",    "white"),
        "ghost":   ("#f1f5f9",    "#e2e8f0",    C_TEXT),
        "outline": (C_SURFACE,    C_INFO_BG,    C_PRIMARY),
        "accent":  (C_ACCENT,     C_PRIMARY_H,  "white"),
    }
    bg, bg_h, fg = colours.get(variant, colours["primary"])
    # Set default font if not provided in kw
    if "font" not in kw:
        kw["font"] = F_BTN
    
    b = tk.Button(parent, text=label, bg=bg, fg=fg,
                  relief="flat", cursor="hand2",
                  padx=16, pady=7, bd=0, command=command,
                  activebackground=bg_h, activeforeground=fg, **kw)
    b.bind("<Enter>",           lambda *_: b.config(bg=bg_h))
    b.bind("<Leave>",           lambda *_: b.config(bg=bg))
    b.bind("<ButtonPress-1>",   lambda *_: b.config(bg=bg_h))
    b.bind("<ButtonRelease-1>", lambda *_: b.config(bg=bg_h))
    return b


def search_box(parent: tk.Misc, var: tk.StringVar, width: int = 22,
               command: Any = None, placeholder: str = "",
               on_type: Any = None) -> tk.Frame:
    outer = tk.Frame(parent, bg=C_SURFACE, highlightthickness=1,
                     highlightbackground=C_BORDER)
    tk.Label(outer, text="🔍", bg=C_SURFACE,
             font=("Segoe UI", 10)).pack(side="left", padx=(8, 2))
    e = tk.Entry(outer, textvariable=var, relief="flat",
                 font=("Segoe UI", 11), width=width,
                 bg=C_SURFACE, fg=C_TEXT)
    e.pack(side="left", ipady=6, padx=(0, 8))

    # Placeholder logic
    if placeholder and not var.get():
        var.set(placeholder)
        e.config(fg=C_MUTED)
        def _clear(_: Any):
            if var.get() == placeholder:
                var.set("")
                e.config(fg=C_TEXT)
        def _restore(_: Any):
            if not var.get():
                var.set(placeholder)
                e.config(fg=C_MUTED)
        e.bind("<FocusIn>", _clear, add="+")
        e.bind("<FocusOut>", _restore, add="+")

    def _in(_: Any) -> None:
        outer.config(highlightbackground=C_PRIMARY, highlightthickness=2)
    def _out(_: Any) -> None:
        outer.config(highlightbackground=C_BORDER, highlightthickness=1)
    e.bind("<FocusIn>",  _in, add="+")
    e.bind("<FocusOut>", _out, add="+")

    if command is not None:
        e.bind("<Return>", lambda *_: command())

    if on_type is not None:
        _timer_id: list[str | None] = [None]
        def _handle_type(_e: Any):
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


def page_header(parent: tk.Misc, text: str, icon: str = "") -> tk.Frame:
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
    tk.Label(row, text=text, bg=C_BG, fg=C_DARK,
             font=("Segoe UI", 16, "bold")).pack(side="left")

    tk.Frame(frm, bg=C_BORDER, height=1).pack(fill="x", padx=20, pady=(0, 6))
    return frm


def make_card(parent: tk.Widget, padx: int = 20, pady: int = 16,
              shadow: bool = True, variant: str = "standard", **kw: Any) -> tuple[tk.Frame, tk.Frame]:
    """Returns (outer_frame, content_frame)."""
    # Use a simpler, more stable shadow approach for Tkinter
    if shadow:
        outer = tk.Frame(parent, bg="#e2e8f0", padx=0, pady=0)
        content = tk.Frame(outer, bg=C_SURFACE, padx=padx, pady=pady, **kw)
        content.pack(fill="both", expand=True, padx=(0, 1), pady=(0, 1))
        return outer, content
    else:
        outer = tk.Frame(parent, bg=C_SURFACE, highlightthickness=1, 
                         highlightbackground=C_BORDER, padx=padx, pady=pady, **kw)
        return outer, outer


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
    tree.tag_configure("Da duyet",  background=C_SUCCESS_BG, foreground=C_SUCCESS)
    tree.tag_configure("Cho duyet", background=C_WARNING_BG, foreground=C_WARNING)
    tree.tag_configure("Tu choi",   background=C_DANGER_BG,  foreground=C_DANGER)
    tree.tag_configure("Hoat dong", background=C_SUCCESS_BG, foreground=C_SUCCESS)
    tree.tag_configure("Bao tri",   background=C_WARNING_BG, foreground=C_WARNING)
    tree.tag_configure("Khoa",      background=C_DANGER_BG,  foreground=C_DANGER)


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
        if status in ("Da duyet", "Cho duyet", "Tu choi",
                      "Hoat dong", "Bao tri", "Khoa"):
            tags.append(status)
        tree.insert("", "end", values=values, tags=tags)


def with_scrollbar(parent: tk.Misc, tree: ttk.Treeview) -> None:
    vsb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)  # type: ignore[arg-type]
    tree.configure(yscrollcommand=vsb.set)
    tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")


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

def labeled_entry(parent: tk.Misc, label: str, var: tk.StringVar,
                  icon: str = "", show: str = "",
                  width: int = 32, padx: int | tuple[int, int] = 0) -> tuple[tk.Frame, tk.Entry]:
    """Labeled, focus-bordered entry with icon and crisp focus ring."""
    tk.Label(parent, text=label, bg=C_SURFACE, fg=C_MUTED,
             font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(12, 0), padx=padx)
    outer = tk.Frame(parent, bg=C_BORDER, padx=1, pady=1)  # border via padding
    outer.pack(fill="x", pady=(3, 0), padx=padx)
    inner_bg = tk.Frame(outer, bg=C_SURFACE)
    inner_bg.pack(fill="both", expand=True)
    inner = tk.Frame(inner_bg, bg=C_SURFACE)
    inner.pack(fill="x")
    if icon:
        tk.Label(inner, text=icon, bg=C_SURFACE,
                 font=("Segoe UI", 13)).pack(side="left", padx=(10, 4), pady=8)
    e = tk.Entry(inner, textvariable=var, width=width, show=show,
                 font=F_INPUT, relief="flat", bg=C_SURFACE, fg=C_TEXT,
                 insertbackground=C_PRIMARY)
    e.pack(side="left", padx=(0 if icon else 12, 10), pady=9,
           fill="x", expand=True)

    def _in(_: Any) -> None:
        outer.config(bg=C_PRIMARY)          # 1px indigo ring on focus
    def _out(_: Any) -> None:
        outer.config(bg=C_BORDER)
    e.bind("<FocusIn>",  _in)   # type: ignore[arg-type]
    e.bind("<FocusOut>", _out)  # type: ignore[arg-type]
    return outer, e


def status_badge(parent: tk.Misc, text: str, bg: str = C_SURFACE) -> tk.Label:
    """Pill-shaped status chip with soft Indigo-tuned colors."""
    PRESETS: dict[str, tuple[str, str]] = {
        "Hoat dong": ("#dcfce7", "#15803d"),
        "Da duyet":  ("#dcfce7", "#15803d"),
        "Cho duyet": ("#fef3c7", "#b45309"),
        "Bao tri":   ("#fef3c7", "#b45309"),
        "Tu choi":   ("#fdf2f8", "#db2777"),
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
    """Titanium-styled custom modal dialog for confirmations or alerts."""
    from typing import Any
    dlg = tk.Toplevel(root)
    dlg.title(title)
    dlg.resizable(False, False)
    dlg.transient(root)
    dlg.grab_set()
    
    # Palette based on kind
    themes = {
        "primary": {"bg": "#eef2ff", "fg": "#4f46e5", "icon": "ℹ️"},
        "warning": {"bg": "#fffbeb", "fg": "#d97706", "icon": "⚠️"},
        "danger":  {"bg": "#fef2f2", "fg": "#dc2626", "icon": "🚨"},
    }
    th = themes.get(kind, themes["primary"])
    bg, fg, icon = th["bg"], th["fg"], th["icon"]
    
    dlg.configure(bg=C_SURFACE)
    result = [False]

    # Header
    hdr = tk.Frame(dlg, bg=fg, height=4)
    hdr.pack(fill="x")
    
    body = tk.Frame(dlg, bg=C_SURFACE, padx=24, pady=20)
    body.pack(fill="both", expand=True)

    content_row = tk.Frame(body, bg=C_SURFACE)
    content_row.pack(fill="x", pady=(0, 16))
    
    tk.Label(content_row, text=icon, bg=C_SURFACE, font=("Segoe UI", 24)).pack(side="left", padx=(0, 12))
    
    text_f = tk.Frame(content_row, bg=C_SURFACE)
    text_f.pack(side="left", fill="both", expand=True)
    
    tk.Label(text_f, text=title, bg=C_SURFACE, fg=fg,
             font=("Segoe UI", 12, "bold"), anchor="w").pack(fill="x")
    tk.Label(text_f, text=message, bg=C_SURFACE, fg="#475569",
             font=("Segoe UI", 10), wraplength=300,
             justify="left", anchor="w").pack(fill="x", pady=(4, 0))

    btn_row = tk.Frame(body, bg=C_SURFACE)
    btn_row.pack(fill="x", pady=(10, 0))

    def _ok() -> None:
        result[0] = True
        dlg.destroy()

    def _cancel() -> None:
        dlg.destroy()

    btn(btn_row, ok_text, _ok,
        variant="danger" if kind == "danger" else "primary").pack(side="right")
    btn(btn_row, cancel_text, _cancel,
        variant="ghost").pack(side="right", padx=8)

    dlg.update_idletasks()
    rx = root.winfo_x() + root.winfo_width() // 2
    ry = root.winfo_y() + root.winfo_height() // 2
    dlg.geometry(f"+{rx - dlg.winfo_width() // 2}+{ry - dlg.winfo_height() // 2}")
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
