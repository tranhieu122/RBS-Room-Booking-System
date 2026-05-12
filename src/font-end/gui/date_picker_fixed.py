# ==================================================================================
# FIXED DATE PICKER - Ngày không biến mất khi popup calendar
# ==================================================================================
# Vấn đề: Khi click DateEntry để chọn ngày, calendar popup che phủ lên text,
# khiến ngày biến mất. Giải pháp: Đặt text bên ngoài DateEntry.

import tkinter as tk
from tkinter import ttk
import datetime as dt
from tkcalendar import DateEntry  # type: ignore[import-untyped]
from typing import Optional, Callable, Any

from gui.theme import C_SURFACE, C_BORDER, C_TEXT, C_MUTED, C_PRIMARY


# ==================================================================================
# SOLUTION 1: DateEntry with Display Label (RECOMMENDED - Simplest)
# ==================================================================================

class DatePickerWithLabel(tk.Frame):
    """
    DateEntry wrapper với display label riêng.
    Khi chọn ngày, calendar popup hiện, text ngày ở label không bị che.
    
    Usage:
        date_picker = DatePickerWithLabel(parent, date_var)
        date_picker.pack()
    """
    
    def __init__(
        self,
        master: tk.Widget,
        date_var: tk.StringVar,
        on_change: Optional[Callable] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(master, bg=C_SURFACE)
        self.date_var = date_var
        self.on_change = on_change
        self._date_entry: Optional[DateEntry] = None
        self._label: Optional[tk.Label] = None
        self._build()
    
    def _build(self) -> None:
        # Style the frame to look like a premium input field
        self.config(highlightthickness=1, highlightbackground=C_BORDER)
        
        # 1. Calendar Icon Button - Pack FIRST on the RIGHT
        cal_btn = tk.Label(
            self,
            text="📅",
            bg=C_SURFACE,
            font=("Segoe UI", 12),
            cursor="hand2",
            fg=C_PRIMARY,
            padx=10,
            pady=6
        )
        cal_btn.pack(side="right")
        
        # 2. Date display label - Pack on the LEFT, occupying remaining space
        self._label = tk.Label(
            self,
            bg=C_SURFACE,
            fg=C_TEXT,
            font=("Segoe UI", 10, "bold"),
            anchor="w",
            padx=12,
            pady=6
        )
        self._label.pack(side="left", fill="both", expand=True)
        
        # Ensure date_var has a value
        if not self.date_var.get():
            self.date_var.set(dt.date.today().isoformat())
            
        # Initialize label text
        self._update_label()
        
        # Hidden DateEntry (width=1 to ensure initialization)
        self._date_entry = DateEntry(
            self,
            width=1, 
            date_pattern="yyyy-mm-dd",
            background=C_PRIMARY,
            foreground="white",
            headersbackground=C_PRIMARY,
            headersforeground="white",
            selectbackground=C_PRIMARY,
            selectforeground="white",
            weekendbackground="white",
            weekendforeground="black",
            borderwidth=0,
            font=("Segoe UI", 10),
            state="readonly"
        )
        # Place it at bottom-right corner of the component
        self._date_entry.place(relx=1.0, rely=1.0, width=1, height=1, anchor="se")
        
        # Set initial date
        try:
            val = self.date_var.get()
            if val:
                initial_date = dt.datetime.fromisoformat(val).date()
                self._date_entry.set_date(initial_date)  # type: ignore
        except (ValueError, AttributeError):
            self._date_entry.set_date(dt.date.today())  # type: ignore
        
        # Bind date selection
        self._date_entry.bind("<<DateEntrySelected>>",  # type: ignore[attr-defined]
                             self._on_date_selected)
        
        # Bind click events to show calendar
        def show_calendar(_: Any) -> None:
            try:
                self._date_entry.drop_down() # type: ignore
            except (AttributeError, tk.TclError):
                self._date_entry.event_generate("<Button-1>")
        
        self._label.bind("<Button-1>", show_calendar)
        cal_btn.bind("<Button-1>", show_calendar)
        
        # Update label and internal widget when date_var changes
        self.date_var.trace_add("write", self._sync_from_var)
    
    def _sync_from_var(self, *args: Any) -> None:
        """Synchronize UI when date_var is changed externally."""
        self._update_label()
        try:
            val = self.date_var.get()
            if val:
                d = dt.datetime.fromisoformat(val).date()
                self._date_entry.set_date(d) # type: ignore
        except (ValueError, AttributeError):
            pass
    
    def _on_date_selected(self, event: Any = None) -> None:
        """Handle date selection from calendar."""
        selected_date = self._date_entry.get_date()  # type: ignore
        self.date_var.set(selected_date.isoformat())
        
        if self.on_change:
            self.on_change()
    
    def _update_label(self, *args: Any) -> None:
        """Update display label when date_var changes."""
        if self._label:
            date_str = self.date_var.get()
            try:
                # Format: 2024-05-12 → 12/05/2024
                parsed = dt.datetime.fromisoformat(date_str).date()
                display = parsed.strftime("%d/%m/%Y")
            except (ValueError, AttributeError):
                display = date_str
            
            self._label.config(text=display)


# ==================================================================================
# SOLUTION 2: DateEntry with Tooltip (Alternative)
# ==================================================================================

class DatePickerWithTooltip(tk.Frame):
    """
    Alternative: DateEntry + tooltip khi hover.
    Calendar popup hiện, nhưng tooltip hiện ngày hiện tại.
    """
    
    def __init__(
        self,
        master: tk.Widget,
        date_var: tk.StringVar,
        on_change: Optional[Callable] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(master, bg=C_SURFACE)
        self.date_var = date_var
        self.on_change = on_change
        self._tooltip_window: Optional[tk.Toplevel] = None
        self._build()
    
    def _build(self) -> None:
        container = tk.Frame(self, bg=C_BORDER, padx=1, pady=1)
        container.pack(fill="x", expand=True)
        
        inner = tk.Frame(container, bg=C_SURFACE)
        inner.pack(fill="both", expand=True)
        
        # DateEntry (visible)
        self._date_entry = DateEntry(
            inner,
            width=28,
            date_pattern="yyyy-mm-dd",
            background=C_PRIMARY,
            foreground="white",
            headersbackground=C_PRIMARY,
            headersforeground="white",
            selectbackground=C_PRIMARY,
            selectforeground="white",
            weekendbackground="white",
            weekendforeground="black",
            borderwidth=2,
            font=("Segoe UI", 10),
            state="readonly"
        )
        self._date_entry.pack(fill="x", expand=True, padx=6, pady=6)  # type: ignore
        
        try:
            initial_date = dt.datetime.fromisoformat(self.date_var.get()).date()
            self._date_entry.set_date(initial_date)  # type: ignore
        except (ValueError, AttributeError):
            self._date_entry.set_date(dt.date.today())  # type: ignore
        
        # Bind events
        self._date_entry.bind("<<DateEntrySelected>>",  # type: ignore[attr-defined]
                             self._on_date_selected)
        
        # Show tooltip on hover
        self._date_entry.bind("<Enter>", self._show_tooltip)  # type: ignore
        self._date_entry.bind("<Leave>", self._hide_tooltip)  # type: ignore
    
    def _on_date_selected(self, event: Any = None) -> None:
        """Handle date selection."""
        selected_date = self._date_entry.get_date()  # type: ignore
        self.date_var.set(selected_date.isoformat())
        
        if self.on_change:
            self.on_change()
    
    def _show_tooltip(self, event: Any) -> None:
        """Show tooltip with current date."""
        if self._tooltip_window:
            return
        
        date_str = self.date_var.get()
        try:
            parsed = dt.datetime.fromisoformat(date_str).date()
            display = parsed.strftime("%d/%m/%Y")
        except (ValueError, AttributeError):
            display = date_str
        
        self._tooltip_window = tk.Toplevel(self)
        self._tooltip_window.overrideredirect(True)
        self._tooltip_window.attributes("-topmost", True)
        
        tk.Label(
            self._tooltip_window,
            text=display,
            bg="#1e1b4b",
            fg="#e0e7ff",
            font=("Segoe UI", 9, "bold"),
            padx=8,
            pady=4
        ).pack()
        
        self._tooltip_window.update_idletasks()
        x = event.widget.winfo_rootx() + event.widget.winfo_width() // 2
        y = event.widget.winfo_rooty() - self._tooltip_window.winfo_height() - 5
        self._tooltip_window.geometry(f"+{x}+{y}")
    
    def _hide_tooltip(self, event: Any = None) -> None:
        """Hide tooltip."""
        if self._tooltip_window:
            try:
                self._tooltip_window.destroy()
            except tk.TclError:
                pass
            self._tooltip_window = None


# ==================================================================================
# SOLUTION 3: Custom Calendar in Popover (Most Advanced)
# ==================================================================================

class DatePickerCustom(tk.Frame):
    """
    Custom date picker with calendar in a better positioned popover.
    Có logic tốt hơn để đặt popover không che text.
    """
    
    def __init__(
        self,
        master: tk.Widget,
        date_var: tk.StringVar,
        on_change: Optional[Callable] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(master, bg=C_SURFACE)
        self.date_var = date_var
        self.on_change = on_change
        self._date_entry: Optional[DateEntry] = None
        self._popover: Optional[tk.Toplevel] = None
        self._is_showing = False
        self._build()
    
    def _build(self) -> None:
        container = tk.Frame(self, bg=C_BORDER, padx=1, pady=1)
        container.pack(fill="x", expand=True)
        
        inner = tk.Frame(container, bg=C_SURFACE)
        inner.pack(fill="both", expand=True)
        
        # Display label + button in row
        display_frame = tk.Frame(inner, bg=C_SURFACE)
        display_frame.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        
        self._label = tk.Label(
            display_frame,
            text=self._format_date(self.date_var.get()),
            bg=C_SURFACE,
            fg=C_TEXT,
            font=("Segoe UI", 11),
            anchor="w"
        )
        self._label.pack(fill="both", expand=True)
        
        # Calendar button
        cal_btn = tk.Button(
            inner,
            text="📅",
            bg="#f8fafc",
            fg=C_PRIMARY,
            relief="flat",
            font=("Segoe UI", 12),
            cursor="hand2",
            padx=10,
            pady=6,
            command=self._toggle_calendar
        )
        cal_btn.pack(side="right", padx=4, pady=4)
        
        # Hidden DateEntry (for calendar functionality)
        self._date_entry = DateEntry(
            self,
            width=0,
            date_pattern="yyyy-mm-dd",
            background=C_PRIMARY,
            foreground="white",
            headersbackground=C_PRIMARY,
            headersforeground="white",
            selectbackground=C_PRIMARY,
            selectforeground="white",
            weekendbackground="white",
            weekendforeground="black",
            borderwidth=0,
            font=("Segoe UI", 10),
            state="readonly"
        )
        
        try:
            initial_date = dt.datetime.fromisoformat(self.date_var.get()).date()
            self._date_entry.set_date(initial_date)  # type: ignore
        except (ValueError, AttributeError):
            self._date_entry.set_date(dt.date.today())  # type: ignore
        
        self._date_entry.bind("<<DateEntrySelected>>",  # type: ignore[attr-defined]
                             self._on_date_selected)
        
        self.date_var.trace_add("write", lambda *a: self._update_display())
    
    def _format_date(self, date_str: str) -> str:
        """Format ISO date to DD/MM/YYYY."""
        try:
            parsed = dt.datetime.fromisoformat(date_str).date()
            return parsed.strftime("%d/%m/%Y")
        except (ValueError, AttributeError):
            return date_str
    
    def _toggle_calendar(self) -> None:
        """Toggle calendar popover visibility."""
        if self._is_showing:
            self._hide_calendar()
        else:
            self._show_calendar()
    
    def _show_calendar(self) -> None:
        """Show calendar in a popover positioned below."""
        self._is_showing = True
        
        # Get button position
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + 5
        
        # Create popover
        self._popover = tk.Toplevel(self.winfo_toplevel())
        self._popover.overrideredirect(True)
        self._popover.geometry(f"+{x}+{y}")
        self._popover.attributes("-topmost", True)
        
        # Add DateEntry to popover (will show calendar)
        popup_frame = tk.Frame(self._popover, bg=C_SURFACE)
        popup_frame.pack()
        
        # Clone DateEntry to popover
        popup_entry = DateEntry(
            popup_frame,
            width=20,
            date_pattern="yyyy-mm-dd",
            background=C_PRIMARY,
            foreground="white",
            headersbackground=C_PRIMARY,
            headersforeground="white",
            selectbackground=C_PRIMARY,
            selectforeground="white",
            weekendbackground="white",
            weekendforeground="black",
            borderwidth=0,
            font=("Segoe UI", 10),
            state="readonly"
        )
        
        try:
            initial = dt.datetime.fromisoformat(self.date_var.get()).date()
            popup_entry.set_date(initial)  # type: ignore
        except (ValueError, AttributeError):
            popup_entry.set_date(dt.date.today())  # type: ignore
        
        popup_entry.pack(padx=10, pady=10)  # type: ignore
        
        def on_select(_: Any) -> None:
            selected = popup_entry.get_date()  # type: ignore
            self.date_var.set(selected.isoformat())
            self._hide_calendar()
        
        popup_entry.bind("<<DateEntrySelected>>", on_select)  # type: ignore[attr-defined]
        
        # Close popover when click outside
        def on_focus_out(_: Any) -> None:
            self.after(200, self._hide_calendar)
        
        self._popover.bind("<FocusOut>", on_focus_out)
    
    def _hide_calendar(self) -> None:
        """Hide calendar popover."""
        self._is_showing = False
        if self._popover:
            try:
                self._popover.destroy()
            except tk.TclError:
                pass
            self._popover = None
    
    def _on_date_selected(self, event: Any = None) -> None:
        """Handle date selection from main DateEntry."""
        selected_date = self._date_entry.get_date()  # type: ignore
        self.date_var.set(selected_date.isoformat())
        
        if self.on_change:
            self.on_change()
    
    def _update_display(self) -> None:
        """Update display label."""
        if hasattr(self, "_label"):
            self._label.config(text=self._format_date(self.date_var.get()))


# ==================================================================================
# USAGE EXAMPLE & MIGRATION GUIDE
# ==================================================================================

MIGRATION_GUIDE = """
🗓️ FIX: Ngày không biến mất khi click DateEntry

VẤN ĐỀ:
- Khi click DateEntry để chọn ngày, calendar popup hiện ra
- Calendar popup che phủ lên text, khiến ngày biến mất
- Khó nhìn date đã chọn

GIẢI PHÁP:
Có 3 tùy chọn, tăng độ phức tạp:

1️⃣ SOLUTION 1: DatePickerWithLabel (RECOMMENDED)
   ✅ Simplest - chỉ cần 3 dòng import
   ✅ Text luôn hiển thị (riêng biệt từ DateEntry)
   ✅ Click icon hoặc text để mở calendar
   ✅ Best UX

2️⃣ SOLUTION 2: DatePickerWithTooltip
   ✅ Giữ DateEntry nguyên bản
   ✅ Tooltip hiển thị ngày khi hover
   ✅ Ít thay đổi code
   ⚠️ Phải hover để xem ngày

3️⃣ SOLUTION 3: DatePickerCustom (Most Control)
   ✅ Custom popover positioning
   ✅ Full control over layout
   ✅ Có nút toggle để show/hide calendar
   ⚠️ Phức tạp hơn

RECOMMENDED: Use SOLUTION 1 (DatePickerWithLabel)

─────────────────────────────────────────────────────────────

MIGRATION STEPS:

OLD CODE (booking_form_gui.py, lines 142-161):
─────────────────────────────────────────────────────────────
    date_frame = tk.Frame(card, bg=C_SURFACE)
    date_frame.grid(row=1, column=1, sticky="ew", padx=(12, 0))
    de = DateEntry(date_frame,
                   width=28, date_pattern="yyyy-mm-dd",
                   background=C_PRIMARY, foreground="white",
                   headersbackground=C_PRIMARY, headersforeground="white",
                   selectbackground=C_PRIMARY, selectforeground="white",
                   weekendbackground="white", weekendforeground="black",
                   borderwidth=2, font=("Segoe UI", 10),
                   state="readonly")
    de.set_date(dt.date.today())
    de.pack(fill="x", expand=True)
    self._date_entry = de

    def _on_date_selected() -> None:
        self.date_var.set(de.get_date().isoformat())
        self._refresh_slots()

    de.bind("<<DateEntrySelected>>",
            lambda *_: self.after(100, _on_date_selected))

NEW CODE (3 lines instead of 20):
─────────────────────────────────────────────────────────────
    from gui.date_picker_fixed import DatePickerWithLabel
    
    date_frame = tk.Frame(card, bg=C_SURFACE)
    date_frame.grid(row=1, column=1, sticky="ew", padx=(12, 0))
    
    date_picker = DatePickerWithLabel(
        date_frame,
        self.date_var,
        on_change=self._refresh_slots
    )
    date_picker.pack(fill="x", expand=True)

THAT'S IT! ✨

─────────────────────────────────────────────────────────────

WHAT CHANGES:

BEFORE:
  | 12/05/2024  |  ← Click here
    [Calendar pops up, text disappears!]

AFTER:
  | 12/05/2024  |  📅  ← Click text OR calendar icon
    [Calendar pops up, text STAYS VISIBLE in label on left!]

─────────────────────────────────────────────────────────────

IMPORT IN booking_form_gui.py:
─────────────────────────────────────────────────────────────
FROM:
    from tkcalendar import DateEntry  # type: ignore[import-untyped]

TO:
    from gui.date_picker_fixed import DatePickerWithLabel

    # OR keep tkcalendar import if using Solution 2/3

─────────────────────────────────────────────────────────────

TEST:
1. Run booking form
2. Click on date area (text or calendar icon)
3. Calendar popup appears
4. Date text STAYS VISIBLE - doesn't disappear!
5. Select new date
6. Popover closes, new date shows
✅ Done!

─────────────────────────────────────────────────────────────

WHICH SOLUTION TO CHOOSE?

Use SOLUTION 1 if:
  ✓ You want simplest code
  ✓ You want text always visible
  ✓ You want modern UX (label + icon)
  ✓ You want minimal changes
  → Use DatePickerWithLabel

Use SOLUTION 2 if:
  ✓ You want to keep existing DateEntry style
  ✓ You only need tooltip on hover
  ✓ You want 1 click to show calendar
  → Use DatePickerWithTooltip

Use SOLUTION 3 if:
  ✓ You need custom popover positioning
  ✓ You want show/hide toggle button
  ✓ You want full control
  → Use DatePickerCustom

RECOMMENDATION: Start with SOLUTION 1! 🎯
"""

if __name__ == "__main__":
    print(MIGRATION_GUIDE)
    
    # Test SOLUTION 1
    root = tk.Tk()
    root.title("Date Picker - Fixed")
    root.geometry("400x200")
    
    date_var = tk.StringVar(value=dt.date.today().isoformat())
    
    tk.Label(root, text="Chọn ngày:", font=("Segoe UI", 12, "bold")).pack(pady=10)
    
    picker = DatePickerWithLabel(root, date_var)
    picker.pack(padx=20, pady=20, fill="x")
    
    tk.Label(root, text=f"Selected: {date_var.get()}", font=("Segoe UI", 10)).pack(pady=10)
    
    def update_label(*args: Any) -> None:
        root.winfo_children()[2].config(text=f"Selected: {date_var.get()}")
    
    date_var.trace_add("write", update_label)
    
    root.mainloop()
