
import sqlite3
import os

DB_PATH = r"src/back end/database/classroom_booking.db"

if not os.path.exists(DB_PATH):
    print("DB not found")
else:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    print("--- USERS ---")
    users = conn.execute("SELECT id, username, role FROM users").fetchall()
    for u in users:
        print(dict(u))
        
    print("\n--- EQUIPMENT ---")
    eqs = conn.execute("SELECT * FROM equipment").fetchall()
    for e in eqs:
        print(dict(e))
        
    conn.close()
