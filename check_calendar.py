import tkinter as tk
try:
    from tkcalendar import DateEntry
    print("tkcalendar is found and working")
except ImportError:
    print("tkcalendar is NOT found")
except Exception as e:
    print(f"Error importing tkcalendar: {e}")
