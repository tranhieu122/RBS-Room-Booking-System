import sqlite3
import os

db_path = r"src\back end\database\classroom_booking.db"
if not os.path.exists(db_path):
    print(f"DB not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT id, user_id, status, booking_date FROM bookings").fetchall()
    print(f"Found {len(rows)} bookings:")
    for r in rows:
        print(dict(r))
    conn.close()
