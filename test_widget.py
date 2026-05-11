import tkinter as tk
from tkcalendar import DateEntry
root = tk.Tk()
try:
    de = DateEntry(root)
    print("DateEntry created successfully")
except Exception as e:
    print(f"Error creating DateEntry: {e}")
root.destroy()
