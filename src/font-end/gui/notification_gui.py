# notification_gui.py — Internal notification screen
from __future__ import annotations
import datetime as dt
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

from gui.theme import (C_BG, C_BORDER, C_DARK, C_MUTED, C_SURFACE, C_TEXT, C_PRIMARY,
                       F_BODY, F_BODY_B, F_SECTION,
                       page_header, btn, relative_time, search_box, get_q, confirm_dialog)

# ── Category detection helpers ────────────────────────────────────────────────
_CATEGORY_RULES: list[tuple[list[str], str, str, str]] = [
    # keywords,              icon, badge_bg,  badge_fg
    (["dat phong", "booking", "phong"], "📅", "#eef2ff", "#4f46e5"),
    (["duyet", "phe duyet"],             "✅", "#dcfce7", "#15803d"),
    (["tu choi", "huy"],                 "❌", "#fdf2f8", "#db2777"),
    (["thiet bi", "equipment"],          "🔧", "#ede9fe", "#6d28d9"),
    (["bao tri", "sua chua"],            "🛠", "#fef3c7", "#b45309"),
    (["he thong", "system"],             "⚙",  "#f1f5f9", "#475569"),
]

def _categorise(title: str, message: str) -> tuple[str, str, str]:
    """Return (icon, badge_bg, badge_fg) for a notification."""
    combined = (title + " " + message).lower()
    for keywords, icon, bg, fg in _CATEGORY_RULES:
        if any(k in combined for k in keywords):
            return icon, bg, fg
    return "🔔", "#eef2ff", "#4f46e5"


class NotificationFrame(tk.Frame):
    def __init__(self, master: tk.Misc, notif_controller: Any,
                 current_user: Any, user_controller: Any = None) -> None:
        super().__init__(master, bg=C_BG)
        self.notif_ctrl = notif_controller
        self.user_ctrl = user_controller
        self.current_user = current_user
        self._canvas: tk.Canvas | None = None
        self._list_frame: tk.Frame | None = None
        self._filter_var = tk.StringVar(value="All")
        self._search_var = tk.StringVar()
        self._auto_refresh_id: str | None = None
        self._build()
        self.refresh()
        self._start_auto_refresh()

    def _start_auto_refresh(self) -> None:
        """Refresh notifications every 60 seconds."""
        if self._auto_refresh_id:
            self.after_cancel(self._auto_refresh_id)
        self._auto_refresh_id = self.after(60000, self._auto_refresh)

    def _auto_refresh(self) -> None:
        self.refresh()
        self._start_auto_refresh()

    def destroy(self) -> None:
        if self._auto_refresh_id:
            self.after_cancel(self._auto_refresh_id)
        super().destroy()

    def _build(self) -> None:
        self._header_frame = page_header(self, "Thong bao noi bo", "🔔")
        self._header_frame.pack(fill="x")
        # Unread badge (appended to header after first refresh)
        self._badge_lbl: tk.Label | None = None

        body = tk.Frame(self, bg=C_BG)
        body.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        # ── Admin compose panel ───────────────────────────────────────────────
        if self.current_user.role == "Admin":
            self._build_compose(body)
            tk.Frame(body, bg=C_BORDER, height=1).pack(fill="x", pady=(0, 12))

        # ── Toolbar: Search & Filter ──────────────────────────────────────────
        toolbar = tk.Frame(body, bg=C_BG)
        toolbar.pack(fill="x", pady=(0, 12))

        search_box(toolbar, self._search_var, placeholder="Tim kiem thong bao...",
                   on_type=self.refresh, width=30).pack(side="left")

        filter_f = tk.Frame(toolbar, bg=C_BG)
        filter_f.pack(side="left", padx=20)
        
        filters = [("Tat ca", "All"), ("Chua doc", "Unread"), 
                   ("Dat phong", "Booking"), ("Thiet bi", "Equipment")]
        for lbl, val in filters:
            b = tk.Radiobutton(filter_f, text=lbl, variable=self._filter_var,
                               value=val, indicatoron=0, padx=12, pady=4,
                               font=("Segoe UI", 9), bg=C_SURFACE, selectcolor="#eef2ff",
                               command=self.refresh, relief="flat", borderwidth=1)
            b.pack(side="left", padx=2)

        actions_f = tk.Frame(toolbar, bg=C_BG)
        actions_f.pack(side="right")
        
        btn(actions_f, "Danh dau tat ca", self._mark_all_read,
            variant="ghost", icon="✅").pack(side="left", padx=2)
        btn(actions_f, "Don dep", self._clear_read,
            variant="ghost", icon="🗑️").pack(side="left", padx=2)

        # ── Scrollable notification list ──────────────────────────────────────
        outer = tk.Frame(body, bg=C_SURFACE, highlightthickness=1,
                         highlightbackground=C_BORDER)
        outer.pack(fill="both", expand=True)

        self._canvas = tk.Canvas(outer, bg=C_SURFACE, highlightthickness=0)
        vsb = ttk.Scrollbar(outer, orient="vertical",
                            command=self._canvas.yview)  # type: ignore[arg-type]
        self._list_frame = tk.Frame(self._canvas, bg=C_SURFACE)
        self._list_frame.bind(
            "<Configure>",
            lambda _: self._canvas.configure(  # type: ignore[union-attr]
                scrollregion=self._canvas.bbox("all")))  # type: ignore[union-attr]
        self._canvas.create_window((0, 0), window=self._list_frame, anchor="nw")
        self._canvas.configure(yscrollcommand=vsb.set)
        self._canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self._canvas.bind(
            "<MouseWheel>",
            lambda e: self._canvas.yview_scroll(-1 * (e.delta // 120), "units"))  # type: ignore[union-attr]

    def _build_compose(self, parent: tk.Frame) -> None:
        frm = tk.Frame(parent, bg=C_SURFACE, highlightthickness=1,
                       highlightbackground=C_BORDER, padx=18, pady=14)
        frm.pack(fill="x", pady=(0, 4))

        tk.Label(frm, text="✉ Gui thong bao moi",
                 bg=C_SURFACE, fg="#1e1b4b",
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 10))

        # Target row
        r1 = tk.Frame(frm, bg=C_SURFACE)
        r1.pack(fill="x", pady=(0, 6))
        tk.Label(r1, text="Gui den:", bg=C_SURFACE, fg=C_TEXT,
                 font=F_BODY_B, width=10, anchor="w").pack(side="left")
        self._target_var = tk.StringVar(value="Tat ca")
        ttk.Combobox(r1, textvariable=self._target_var,
                     values=["Tat ca", "Giang vien", "Sinh vien"],
                     state="readonly", width=18,
                     font=("Segoe UI", 10)).pack(side="left", padx=(4, 0))

        # Title row
        r2 = tk.Frame(frm, bg=C_SURFACE)
        r2.pack(fill="x", pady=(0, 6))
        tk.Label(r2, text="Tieu de:", bg=C_SURFACE, fg=C_TEXT,
                 font=F_BODY_B, width=10, anchor="w").pack(side="left")
        self._title_var = tk.StringVar()
        tk.Entry(r2, textvariable=self._title_var, font=("Segoe UI", 10),
                 relief="flat", bg="#f8fafc", fg=C_TEXT,
                 width=52).pack(side="left", padx=(4, 0), ipady=4)

        # Message row
        r3 = tk.Frame(frm, bg=C_SURFACE)
        r3.pack(fill="x", pady=(0, 8))
        tk.Label(r3, text="Noi dung:", bg=C_SURFACE, fg=C_TEXT,
                 font=F_BODY_B, width=10, anchor="nw").pack(
            side="left", pady=(4, 0))
        self._msg_text = tk.Text(r3, font=("Segoe UI", 10), height=3,
                                  relief="flat", bg="#f8fafc", fg=C_TEXT,
                                  width=52, wrap="word")
        self._msg_text.pack(side="left", padx=(4, 0), pady=(4, 0))

        btn(frm, "Gui thong bao", self._send,
            variant="primary", icon="📨").pack(anchor="e", pady=(4, 0))

    def _send(self) -> None:
        title = self._title_var.get().strip()
        message = self._msg_text.get("1.0", "end").strip()
        target = self._target_var.get()
        try:
            if not self.user_ctrl:
                raise ValueError("Khong co user controller.")
            all_users = self.user_ctrl.list_users()
            if target == "Tat ca":
                count = self.notif_ctrl.send_to_all(
                    self.current_user, title, message, all_users)
            else:
                count = self.notif_ctrl.send_to_role(
                    self.current_user, target, title, message, all_users)
            self._title_var.set("")
            self._msg_text.delete("1.0", "end")
            confirm_dialog(self, "Thành công", f"Da gui {count} thong bao.", 
                           kind="primary", cancel_text=None)
            self.refresh()
        except ValueError as e:
            confirm_dialog(self, "Lỗi", str(e), kind="danger", cancel_text=None)

    def _mark_all_read(self) -> None:
        self.notif_ctrl.mark_all_read(self.current_user.user_id)
        self.refresh()

    def _clear_read(self) -> None:
        if confirm_dialog(self, "Xac nhan", "Ban co muon xoa tat ca thong bao da doc?", kind="danger"):
            count = self.notif_ctrl.delete_all_read(self.current_user.user_id)
            self.refresh()
            if count > 0:
                from gui.theme import toast
                toast(self, f"Da xoa {count} thong bao.", kind="info")

    def refresh(self) -> None:
        if self._list_frame is None:
            return
        for w in self._list_frame.winfo_children():
            w.destroy()

        notifs = self.notif_ctrl.get_notifications(self.current_user.user_id)
        
        # Filtering logic
        f_val = self._filter_var.get()
        q = get_q(self._search_var, "Tim kiem thong bao...")
        
        if f_val == "Unread":
            notifs = [n for n in notifs if not n["is_read"]]
        elif f_val == "Booking":
            notifs = [n for n in notifs if any(k in (n["title"]+n["message"]).lower() 
                                             for k in ["dat phong", "booking"])]
        elif f_val == "Equipment":
            notifs = [n for n in notifs if any(k in (n["title"]+n["message"]).lower() 
                                             for k in ["thiet bi", "equipment", "bao tri"])]

        if q:
            notifs = [n for n in notifs if q in n["title"].lower() or q in n["message"].lower()]

        # ── Update unread badge in header ─────────────────────────────────
        unread_count = sum(1 for n in notifs if not n["is_read"])
        if self._badge_lbl is not None:
            self._badge_lbl.destroy()
            self._badge_lbl = None
        if unread_count > 0:
            self._badge_lbl = tk.Label(
                self._header_frame,
                text=f" {unread_count} chua doc ",
                bg="#db2777", fg="white",
                font=("Segoe UI", 9, "bold"),
                padx=4, pady=2)
            self._badge_lbl.pack(side="right", padx=16, pady=10)

        if not notifs:
            empty_frame = tk.Frame(self._list_frame, bg=C_SURFACE, pady=40)
            empty_frame.pack(fill="x")
            tk.Label(empty_frame, text="🔔", bg=C_SURFACE,
                     font=("Segoe UI", 36)).pack()
            tk.Label(empty_frame,
                     text="Khong co thong bao nao",
                     bg=C_SURFACE, fg=C_DARK,
                     font=("Segoe UI", 12, "bold")).pack(pady=(8, 2))
            tk.Label(empty_frame,
                     text="Cac thong bao moi se hien thi o day",
                     bg=C_SURFACE, fg=C_MUTED,
                     font=("Segoe UI", 10)).pack()
            return

        for n in notifs:
            self._draw_row(n) # type: ignore

    def _draw_row(self, n: dict) -> None: # type: ignore
        is_unread = not n["is_read"]
        row_bg    = "#eef2ff" if is_unread else C_SURFACE
        icon, cat_bg, cat_fg = _categorise(n.get("title", ""), n.get("message", "")) # type: ignore

        # ── Outer card wrapper ────────────────────────────────────────────────
        card_wrap = tk.Frame(self._list_frame, bg=C_BG, padx=8, pady=4)
        card_wrap.pack(fill="x")

        card = tk.Frame(card_wrap, bg=row_bg, padx=14, pady=12,
                        highlightthickness=1,
                        highlightbackground="#c7d2fe" if is_unread else C_BORDER,
                        cursor="hand2")
        card.pack(fill="x")

        # Hover effect
        def _enter(_: Any, c=card, bg=row_bg) -> None: # type: ignore
            darken = "#dde6ff" if bg == "#eef2ff" else "#f8fafc"
            c.config(bg=darken)
            for ch in c.winfo_children():
                try:
                    ch.config(bg=darken) # type: ignore
                except Exception:
                    pass

        def _leave(_: Any, c=card, bg=row_bg) -> None: # type: ignore
            c.config(bg=bg)
            for ch in c.winfo_children():
                try:
                    ch.config(bg=bg) # type: ignore
                except Exception:
                    pass

        card.bind("<Enter>", _enter)
        card.bind("<Leave>", _leave)

        # ── Left accent bar (unread = indigo, read = transparent) ────────────
        accent_color = "#4f46e5" if is_unread else row_bg
        accent = tk.Frame(card, bg=accent_color, width=3)
        accent.pack(side="left", fill="y", padx=(0, 10))

        # ── Icon bubble ───────────────────────────────────────────────────────
        ic_frame = tk.Frame(card, bg=cat_bg, padx=6, pady=6)
        ic_frame.pack(side="left", padx=(0, 12))
        tk.Label(ic_frame, text=icon, bg=cat_bg,
                 font=("Segoe UI", 16)).pack()

        # ── Main content ──────────────────────────────────────────────────────
        content = tk.Frame(card, bg=row_bg)
        content.pack(side="left", fill="both", expand=True)

        # Delete button (Top right of content area)
        del_btn = tk.Label(card, text="✕", bg=row_bg, fg="#94a3b8",
                           font=("Segoe UI", 10), cursor="hand2", padx=4)
        del_btn.pack(side="right", anchor="ne")
        
        def _on_del_enter(_): del_btn.config(fg="#ef4444")
        def _on_del_leave(_): del_btn.config(fg="#94a3b8")
        def _do_delete(event: Any = None, nid: int = n["id"]) -> str:
            if confirm_dialog(self, "Xoa thong bao", "Ban co chac muon xoa thong bao nay?", kind="danger"):
                self.notif_ctrl.delete(nid)
                self.refresh()
            return "break"

        del_btn.bind("<Enter>", _on_del_enter)
        del_btn.bind("<Leave>", _on_del_leave)
        del_btn.bind("<Button-1>", _do_delete)

        # Top row: title + relative time + unread dot
        top = tk.Frame(content, bg=row_bg)
        top.pack(fill="x")

        if is_unread:
            tk.Label(top, text="●", bg=row_bg, fg="#4f46e5",
                     font=("Segoe UI", 8)).pack(side="left", padx=(0, 4))

        tk.Label(top, text=n.get("title", "Thong bao"), # type: ignore
                 bg=row_bg, fg=C_DARK,
                 font=("Segoe UI", 10, "bold")).pack(side="left")

        rel = relative_time(n.get("created_at", "")) # type: ignore
        tk.Label(top, text=rel, bg=row_bg, fg=C_MUTED,
                 font=("Segoe UI", 8, "italic")).pack(side="right")

        # Message preview (max 2 lines)
        msg = n.get("message", "") # type: ignore
        tk.Label(content, text=msg, bg=row_bg, fg=C_TEXT, # type: ignore
                 font=F_BODY, wraplength=700,
                 justify="left", anchor="w").pack(fill="x", pady=(3, 0))

        # Bottom row: sender chip + "Danh dau da doc" action
        bottom = tk.Frame(content, bg=row_bg)
        bottom.pack(fill="x", pady=(5, 0))

        sender = n.get("sender_name", "He thong") # type: ignore
        sender_chip = tk.Frame(bottom, bg=cat_bg, padx=6, pady=2)
        sender_chip.pack(side="left")
        tk.Label(sender_chip, text=f"Tu: {sender}",
                 bg=cat_bg, fg=cat_fg,
                 font=("Segoe UI", 8, "bold")).pack()

        if is_unread:
            def _mark_read(event: Any = None, nid: int = n["id"]) -> str:
                self.notif_ctrl.mark_read(nid)
                self.refresh()
                return "break"  # Stop event propagating to card click handler

            read_btn = tk.Label(bottom, text="✓ Danh dau da doc",
                                bg=row_bg, fg="#4f46e5",
                                font=("Segoe UI", 8, "underline"),
                                cursor="hand2")
            read_btn.pack(side="right")
            read_btn.bind("<Button-1>", _mark_read)

        # ── Click to view detail ──────────────────────────────────────────────
        def _on_click(_: Any = None, nid: int = n["id"], item: dict = n) -> None: # type: ignore
            if not n["is_read"]:
                self.notif_ctrl.mark_read(nid)
            self._show_notification_detail(item)
            self.refresh()

        for widget in (card, content, top, bottom):
            widget.bind("<Button-1>", _on_click) # pyright: ignore[reportUnknownArgumentType]


    def _show_notification_detail(self, n: dict) -> None: # type: ignore
        """Show full notification content in a large, premium modal."""
        dlg = tk.Toplevel(self)
        dlg.title("Chi tiet thong bao")
        dlg.configure(bg=C_SURFACE)
        dlg.resizable(True, True)
        dlg.minsize(600, 450)
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()

        icon, cat_bg, cat_fg = _categorise(n.get("title", ""), n.get("message", "")) # type: ignore

        # Header
        hdr = tk.Frame(dlg, bg="#4f46e5", padx=24, pady=20)
        hdr.pack(fill="x")
        hdr_inner = tk.Frame(hdr, bg="#4f46e5")
        hdr_inner.pack(fill="x")
        ic_bg = tk.Frame(hdr_inner, bg=cat_bg, padx=10, pady=10)
        ic_bg.pack(side="left", padx=(0, 16))
        tk.Label(ic_bg, text=icon, bg=cat_bg, font=("Segoe UI", 22)).pack()
        
        info = tk.Frame(hdr_inner, bg="#4f46e5")
        info.pack(side="left", fill="both", expand=True)
        tk.Label(info, text=n.get("title", "Thong bao"), # type: ignore
                 bg="#4f46e5", fg="white",
                 font=("Segoe UI", 16, "bold"), anchor="w").pack(fill="x")
        sender = n.get("sender_name", "He thong") # type: ignore
        tk.Label(info, text=f"Tu: {sender}",
                 bg="#4f46e5", fg="#c7d2fe",
                 font=("Segoe UI", 10)).pack(anchor="w")

        # Body
        body = tk.Frame(dlg, bg=C_SURFACE, padx=24, pady=24)
        body.pack(fill="both", expand=True)

        # Time row
        created = n.get("created_at", "") # type: ignore
        rel = relative_time(created) # type: ignore
        try:
            from datetime import datetime
            abs_time = datetime.fromisoformat(str(created)).strftime("%d/%m/%Y %H:%M")
        except Exception:
            abs_time = str(created)
            
        time_f = tk.Frame(body, bg="#f8fafc", highlightthickness=1,
                         highlightbackground=C_BORDER, padx=12, pady=8)
        time_f.pack(fill="x", pady=(0, 16))
        tk.Label(time_f, text=f"🕐  Thoi gian: {abs_time} ({rel})",
                 bg="#f8fafc", fg=C_MUTED, font=("Segoe UI", 10)).pack(anchor="w")

        # Message content
        msg_scroll = tk.Frame(body, bg=C_SURFACE)
        msg_scroll.pack(fill="both", expand=True)
        
        txt = tk.Text(msg_scroll, bg=C_SURFACE, fg=C_TEXT, font=("Segoe UI", 11),
                      relief="flat", wrap="word", padx=10, pady=10)
        txt.insert("1.0", n.get("message", "")) # type: ignore
        txt.config(state="disabled")
        txt.pack(side="left", fill="both", expand=True)
        
        # Buttons
        btn_row = tk.Frame(body, bg=C_SURFACE)
        btn_row.pack(fill="x", pady=(16, 0))
        btn(btn_row, "Dong", dlg.destroy, variant="primary").pack(side="right")

        dlg.update_idletasks()
        w, h = 650, 500
        pw = self.winfo_rootx() + self.winfo_width() // 2
        ph = self.winfo_rooty() + self.winfo_height() // 2
        dlg.geometry(f"{w}x{h}+{pw - w//2}+{ph - h//2}")
