-- ═══════════════════════════════════════════════════════════════════════════
-- He Thong Quan Ly Dat Phong Hoc – Nhom 24
-- SQLite schema reference (actual schema is applied by sqlite_db.py)
-- ═══════════════════════════════════════════════════════════════════════════



CREATE TABLE IF NOT EXISTS users (
    id            TEXT PRIMARY KEY,
    username      TEXT NOT NULL UNIQUE,
    full_name     TEXT NOT NULL,
    role          TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    phone         TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    status        TEXT NOT NULL DEFAULT 'Hoat dong'
);

CREATE TABLE IF NOT EXISTS rooms (
    id         TEXT PRIMARY KEY,
    name       TEXT NOT NULL UNIQUE,
    capacity   INTEGER NOT NULL,
    room_type  TEXT NOT NULL,
    equipment  TEXT NOT NULL DEFAULT '',
    status     TEXT NOT NULL DEFAULT 'Hoat dong'
);

CREATE TABLE IF NOT EXISTS bookings (
    id               TEXT PRIMARY KEY,
    user_id          TEXT NOT NULL,
    user_name        TEXT NOT NULL,
    room_id          TEXT NOT NULL,
    booking_date     TEXT NOT NULL,
    slot             TEXT NOT NULL,
    purpose          TEXT NOT NULL,
    status           TEXT NOT NULL DEFAULT 'Cho duyet',
    rejection_reason TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (room_id) REFERENCES rooms(id)
);

CREATE TABLE IF NOT EXISTS equipment (
    id             TEXT PRIMARY KEY,
    name           TEXT NOT NULL,
    equipment_type TEXT NOT NULL,
    room_id        TEXT NOT NULL,
    status         TEXT NOT NULL,
    purchase_date  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS schedules (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id  TEXT NOT NULL,
    weekday  TEXT NOT NULL,
    slot     TEXT NOT NULL,
    label    TEXT NOT NULL DEFAULT '',
    status   TEXT NOT NULL DEFAULT 'Trong',
    UNIQUE (room_id, weekday, slot)
);

CREATE TABLE IF NOT EXISTS room_ratings (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id    TEXT NOT NULL,
    user_id    TEXT NOT NULL,
    user_name  TEXT NOT NULL,
    stars      INTEGER NOT NULL CHECK(stars BETWEEN 1 AND 5),
    comment    TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS room_issues (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id     TEXT NOT NULL,
    user_id     TEXT NOT NULL,
    user_name   TEXT NOT NULL,
    description TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'Chua xu ly',
    notes       TEXT NOT NULL DEFAULT '',
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);