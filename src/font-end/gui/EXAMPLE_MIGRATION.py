# ==================================================================================
# EXAMPLE: How to Migrate Existing GUI to Use Enhanced Components
# ==================================================================================
# This file shows before/after examples of refactoring GUI code.
# Copy patterns từ đây để update các file GUI hiện tại.

import tkinter as tk
from tkinter import ttk
from gui.theme import C_BG, C_SURFACE, C_MUTED, C_PRIMARY
from gui.theme_enhanced import (
    enhanced_labeled_entry, btn_with_shadow, enhanced_make_card,
    form_grid, apply_enhanced_table_style, make_stat_card
)


# ==================================================================================
# EXAMPLE 1: USER MANAGEMENT DIALOG - BEFORE vs AFTER
# ==================================================================================

# --- BEFORE (từ user_gui.py) ---
class UserDialogOld(tk.Toplevel):
    def _build_old(self) -> None:
        frm = tk.Frame(self, bg=C_SURFACE, padx=24, pady=20)
        frm.pack()
        
        # Old way: labeled_entry from theme.py
        from gui.theme import labeled_entry
        icons = {"user_id": "🔑", "username": "👤"}
        labels = {"user_id": "MA NGUOI DUNG", "username": "TEN DANG NHAP"}
        
        for key in ("user_id", "username"):
            _outer, entry = labeled_entry(
                frm, labels[key], self.vars[key],
                icon=icons[key], width=32
            )


# --- AFTER (Using Enhanced Components) ---
class UserDialogNew(tk.Toplevel):
    def _build_new(self) -> None:
        frm = tk.Frame(self, bg=C_SURFACE, padx=24, pady=20)
        frm.pack()
        
        # New way: enhanced_labeled_entry with better focus states
        icons = {"user_id": "🔑", "username": "👤"}
        labels = {"user_id": "MA NGUOI DUNG", "username": "TEN DANG NHAP"}
        
        for key in ("user_id", "username"):
            _outer, entry = enhanced_labeled_entry(
                frm, 
                labels[key], 
                self.vars[key],
                icon=icons[key], 
                width=32,
                required=True,  # NEW: Show required indicator
                help_text="Không thể thay đổi sau tạo"  # NEW: Help text
            )
        
        # NEW: Use form_grid for better layout
        # form_grid(frm, [
        #     ("MA NGUOI DUNG", self.vars["user_id"], "🔑"),
        #     ("TEN DANG NHAP", self.vars["username"], "👤"),
        #     ("HO VA TEN", self.vars["full_name"], "📛"),
        #     ("EMAIL", self.vars["email"], "📧"),
        # ], columns=2)


# ==================================================================================
# EXAMPLE 2: BUTTON STYLING - BEFORE vs AFTER
# ==================================================================================

# --- BEFORE (từ user_gui.py) ---
class FormOld(tk.Frame):
    def _build_buttons_old(self) -> None:
        from gui.theme import btn
        
        btn_row = tk.Frame(self, bg=C_SURFACE)
        btn_row.pack(fill="x", pady=(20, 0))
        
        # Old buttons: Flat, no shadow
        btn(btn_row, "Luu lai", self._save, icon="💾").pack(side="right", padx=(6, 0))
        btn(btn_row, "Huy", self.destroy, variant="ghost").pack(side="right")


# --- AFTER (Enhanced Buttons) ---
class FormNew(tk.Frame):
    def _build_buttons_new(self) -> None:
        btn_row = tk.Frame(self, bg=C_SURFACE)
        btn_row.pack(fill="x", pady=(20, 0))
        
        # New buttons: With shadow + press animation
        btn_with_shadow(btn_row, "Luu lai", self._save, 
                       variant="primary", icon="💾").pack(side="right", padx=(6, 0))
        btn_with_shadow(btn_row, "Huy", self.destroy, 
                       variant="ghost").pack(side="right")


# ==================================================================================
# EXAMPLE 3: STAT CARDS - BEFORE vs AFTER
# ==================================================================================

# --- BEFORE (từ user_gui.py) ---
class StatsOld(tk.Frame):
    def _build_stats_old(self) -> None:
        from gui.theme import make_card
        
        stats_outer = tk.Frame(self, bg=C_BG)
        stats_outer.pack(fill="x", padx=0, pady=(10, 5))
        for i in range(5):
            stats_outer.columnconfigure(i, weight=1)
        
        for i, (key, icon, label, bg, fg) in enumerate([
            ("total", "👥", "Tổng cộng", "#eff6ff", "#2563eb"),
            ("admin", "🛡️", "Quản trị", "#faf5ff", "#7c3aed"),
        ]):
            # Old way: Manual card creation with lots of code
            outer, chip = make_card(stats_outer, padx=15, pady=15, shadow=True)
            outer.grid(row=0, column=i, sticky="nsew", padx=10, pady=10)
            
            badge = tk.Frame(chip, bg="#f8fafc", padx=10, pady=8)
            badge.pack(side="left", padx=(0, 15))
            tk.Label(badge, text=icon, bg="#f8fafc", font=("Segoe UI", 20)).pack()
            
            # ... more code ...


# --- AFTER (Using make_stat_card Helper) ---
class StatsNew(tk.Frame):
    def _build_stats_new(self) -> None:
        stats_outer = tk.Frame(self, bg=C_BG)
        stats_outer.pack(fill="x", padx=0, pady=(10, 5))
        for i in range(5):
            stats_outer.columnconfigure(i, weight=1)
        
        self._stat_labels = {}
        
        for i, (key, icon, label, color_bg, color_fg) in enumerate([
            ("total", "👥", "Tổng cộng", "#eff6ff", "#2563eb"),
            ("admin", "🛡️", "Quản trị", "#faf5ff", "#7c3aed"),
        ]):
            # New way: One function call!
            val_lbl = make_stat_card(stats_outer, icon, label, 0, color_fg, color_bg)
            self._stat_labels[key] = val_lbl
            
            # Find and grid the parent outer frame
            outer = val_lbl.master.master
            outer.grid(row=0, column=i, sticky="nsew", padx=10, pady=10)


# ==================================================================================
# EXAMPLE 4: FORM WITH GRID LAYOUT
# ==================================================================================

# --- BEFORE (Inconsistent Spacing) ---
class RoomFormOld(tk.Frame):
    def _build_form_old(self) -> None:
        from gui.theme import labeled_entry
        
        frm = tk.Frame(self, bg=C_SURFACE, padx=26, pady=20)
        frm.pack(fill="both", expand=True)
        
        # Old: Each field packed individually, hard to align columns
        labeled_entry(frm, "MA PHONG *", self.vars["room_id"], icon="🔑", width=34)
        labeled_entry(frm, "TEN PHONG *", self.vars["name"], icon="📛", width=34)
        labeled_entry(frm, "SUC CHUA *", self.vars["capacity"], icon="👥", width=34)
        
        # Spacing between fields is inconsistent


# --- AFTER (Grid-based Layout) ---
class RoomFormNew(tk.Frame):
    def _build_form_new(self) -> None:
        frm = tk.Frame(self, bg=C_SURFACE, padx=26, pady=20)
        frm.pack(fill="both", expand=True)
        
        # New: Grid layout with consistent spacing
        form_grid(frm, [
            ("MA PHONG", self.vars["room_id"], "🔑"),
            ("TEN PHONG", self.vars["name"], "📛"),
            ("SUC CHUA", self.vars["capacity"], "👥"),
            ("LOAI PHONG", self.vars["room_type"], "📚"),
            ("TRANG THIET BI", self.vars["equipment"], "🔧"),
            ("TRANG THAI", self.vars["status"], "✅"),
        ], columns=2)


# ==================================================================================
# EXAMPLE 5: INTERACTIVE CARDS (Dashboard)
# ==================================================================================

# --- BEFORE (Static Cards) ---
class DashboardOld(tk.Frame):
    def _build_cards_old(self) -> None:
        from gui.theme import make_card, btn
        
        cards_frame = tk.Frame(self, bg=C_BG)
        cards_frame.pack(fill="both", expand=True)
        
        for i in range(3):
            outer, content = make_card(cards_frame, padx=20, pady=20, shadow=True)
            content.pack(fill="both", expand=True, padx=10, pady=10)
            
            tk.Label(content, text=f"Card {i+1}", bg=C_SURFACE, 
                    fg=C_PRIMARY, font=("Segoe UI", 14, "bold")).pack()
            
            # Cards are static - clicking does nothing special


# --- AFTER (Clickable Cards with Hover) ---
class DashboardNew(tk.Frame):
    def _build_cards_new(self) -> None:
        cards_frame = tk.Frame(self, bg=C_BG)
        cards_frame.pack(fill="both", expand=True)
        
        for i in range(3):
            def on_card_click(idx=i):
                print(f"Card {idx+1} clicked!")
            
            # New: Clickable cards with hover effect
            outer, content = enhanced_make_card(
                cards_frame, 
                padx=20, pady=20, shadow=True,
                clickable=True,
                on_click=on_card_click
            )
            outer.pack(fill="both", expand=True, padx=10, pady=10)
            
            tk.Label(content, text=f"Card {i+1}", bg=C_SURFACE,
                    fg=C_PRIMARY, font=("Segoe UI", 14, "bold")).pack()


# ==================================================================================
# EXAMPLE 6: TABLE STYLING (Dashboard / Booking List)
# ==================================================================================

# --- BEFORE (Theme.py) ---
# style.configure("TV.Treeview", rowheight=36)  # Small rows, hard to read

# --- AFTER (Enhanced Styling) ---
def setup_tables_new(root: tk.Tk) -> None:
    style = ttk.Style()
    style.theme_use("clam")
    
    # Apply enhanced table styling
    apply_enhanced_table_style(style)  # ← Does everything!
    
    # Now all Treeviews will have:
    # - 44px row height (vs 36px) for better readability
    # - Better alternating row colors (more contrast)
    # - Improved selection highlighting
    # - Better header styling


# ==================================================================================
# EXAMPLE 7: ROOM DETAIL DIALOG - COMPLETE REFACTOR
# ==================================================================================

# --- BEFORE (From room_detail_gui.py) ---
class RoomDetailDialogOld(tk.Toplevel):
    def _build_old(self) -> None:
        from gui.theme import labeled_entry
        
        frm = tk.Frame(self, bg=C_SURFACE, padx=26, pady=20)
        frm.pack(fill="both", expand=True)
        
        # Repetitive code for each field
        labeled_entry(frm, "MA PHONG *", self.vars["room_id"], icon="🔑", width=34)
        labeled_entry(frm, "TEN PHONG *", self.vars["name"], icon="📛", width=34)
        labeled_entry(frm, "SUC CHUA *", self.vars["capacity"], icon="👥", width=34)
        labeled_entry(frm, "LOAI PHONG", self.vars["room_type"], icon="📚", width=34)
        labeled_entry(frm, "TRANG THIET BI", self.vars["equipment"], icon="🔧", width=34)
        
        # Buttons
        from gui.theme import btn
        btn_row = tk.Frame(frm, bg=C_SURFACE)
        btn_row.pack(fill="x", pady=(20, 0))
        btn(btn_row, "Luu lai", self._save, icon="💾").pack(side="left", padx=(0, 8))
        btn(btn_row, "Huy", self.destroy, variant="ghost").pack(side="left")


# --- AFTER (Refactored) ---
class RoomDetailDialogNew(tk.Toplevel):
    def _build_new(self) -> None:
        self._error_vars = {k: tk.StringVar() for k in self.vars.keys()}
        
        frm = tk.Frame(self, bg=C_SURFACE, padx=26, pady=20)
        frm.pack(fill="both", expand=True)
        
        # Cleaner field definitions
        field_defs = [
            ("room_id", "MA PHONG", "🔑", True),
            ("name", "TEN PHONG", "📛", True),
            ("capacity", "SUC CHUA (NGUOI)", "👥", True),
            ("room_type", "LOAI PHONG", "📚", False),
            ("equipment", "TRANG THIET BI", "🔧", False),
        ]
        
        for key, label, icon, required in field_defs:
            enhanced_labeled_entry(
                frm, label, self.vars[key],
                icon=icon, width=34, required=required,
                error_var=self._error_vars[key],
                help_text="Bắt buộc" if required else ""
            )
        
        # Better buttons
        btn_row = tk.Frame(frm, bg=C_SURFACE)
        btn_row.pack(fill="x", pady=(20, 0))
        btn_with_shadow(btn_row, "Luu lai", self._save, icon="💾").pack(side="left", padx=(0, 8))
        btn_with_shadow(btn_row, "Huy", self.destroy, variant="ghost").pack(side="left")


# ==================================================================================
# CHECKLIST: How to Migrate Your GUI Files
# ==================================================================================

MIGRATION_CHECKLIST = """
📋 STEP-BY-STEP MIGRATION GUIDE

1. Update imports in your GUI file:
   FROM: from gui.theme import labeled_entry, btn, make_card
   TO:   from gui.theme import ...  (keep these)
         from gui.theme_enhanced import (
             enhanced_labeled_entry, btn_with_shadow, 
             enhanced_make_card, form_grid
         )

2. Replace components:
   ✓ labeled_entry()  →  enhanced_labeled_entry()
   ✓ btn()           →  btn_with_shadow()
   ✓ make_card()     →  enhanced_make_card()
   ✓ (custom grids)  →  form_grid()

3. Add table enhancement (one-time in main app):
   In your main app initialization:
   
   style = ttk.Style()
   apply_enhanced_table_style(style)

4. For forms, replace manual pack() with form_grid():
   BEFORE:
   - Multiple labeled_entry() calls
   - Inconsistent spacing
   - Hard to maintain layout
   
   AFTER:
   - One form_grid() call
   - List of fields
   - Perfect 2-column layout

5. Update stat cards:
   BEFORE: make_card() + manual Label creation
   AFTER: make_stat_card() - one function!

6. Test each dialog:
   - Check focus states (should glow blue)
   - Click buttons (should have press animation)
   - Hover cards (should lift and shadow changes)
   - Tables (should have better row height)

FILES TO UPDATE (Priority Order):
  1. user_gui.py              (4 occurrences)
  2. room_detail_gui.py       (3 occurrences)
  3. equipment_gui.py         (similar pattern)
  4. dashboard_gui.py         (stat cards + tables)
  5. booking_form_gui.py      (forms)
  6. profile_gui.py           (simple dialog)
  7. login_gui.py             (already styled well)

Estimated time per file: 15-30 minutes
Total effort: 2-3 hours for full migration
Benefit: Much better UX! 🎨
"""

print(MIGRATION_CHECKLIST)

# ==================================================================================
# QUICK TEST: Run this to verify components work
# ==================================================================================

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Enhanced Theme Components Test")
    root.geometry("600x500")
    
    # Test 1: Enhanced input
    test_var = tk.StringVar()
    enhanced_labeled_entry(
        root, "Test Input", test_var, icon="✉️",
        help_text="Try typing here to see focus state"
    )
    
    # Test 2: Buttons
    btn_frame = tk.Frame(root, bg="#f8fafc")
    btn_frame.pack(fill="x", padx=20, pady=20)
    btn_with_shadow(btn_frame, "Primary Button", lambda: print("Click!"), variant="primary").pack(side="left", padx=5)
    btn_with_shadow(btn_frame, "Danger Button", lambda: print("Delete!"), variant="danger").pack(side="left", padx=5)
    
    # Test 3: Cards
    outer, content = enhanced_make_card(root, clickable=True, on_click=lambda: print("Card clicked!"))
    outer.pack(fill="both", expand=True, padx=20, pady=20)
    tk.Label(content, text="Click this card!", bg="white", fg="#4f46e5", font=("Segoe UI", 14)).pack(pady=40)
    
    root.mainloop()
