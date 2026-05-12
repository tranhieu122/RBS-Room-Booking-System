import sqlite3
import os

db_path = r"src\back end\database\classroom_booking.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT id, user_id, user_name, status, booking_date FROM bookings").fetchall()
with open("bookings_debug.txt", "w", encoding="utf-8") as f:
    f.write(f"Found {len(rows)} bookings:\n")
    for r in rows:
        f.write(str(dict(r)) + "\n")
conn.close()
print("Done writing to bookings_debug.txt")
