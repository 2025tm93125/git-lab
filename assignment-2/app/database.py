import os
import sqlite3
from werkzeug.security import generate_password_hash

def get_db_connection(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path, admin_username="admin", admin_password=None):
    conn = get_db_connection(db_path)
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        age INTEGER,
        height REAL,
        weight REAL,
        program TEXT,
        calories INTEGER,
        target_weight REAL,
        target_adherence INTEGER,
        membership_status TEXT DEFAULT 'Active',
        membership_end TEXT
    );

    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT NOT NULL,
        week TEXT NOT NULL,
        adherence INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT NOT NULL,
        date TEXT NOT NULL,
        workout_type TEXT NOT NULL,
        duration_min INTEGER NOT NULL,
        notes TEXT
    );

    CREATE TABLE IF NOT EXISTS exercises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workout_id INTEGER,
        name TEXT NOT NULL,
        sets INTEGER,
        reps INTEGER,
        weight REAL
    );

    CREATE TABLE IF NOT EXISTS metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT NOT NULL,
        date TEXT NOT NULL,
        weight REAL,
        waist REAL,
        bodyfat REAL
    );
    """)

    # Create an initial administrator only when a password is configured.
    if admin_password:
        existing = cur.execute(
            "SELECT username FROM users WHERE username = ?",
            (admin_username,)
        ).fetchone()

        if not existing:
            cur.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (admin_username, generate_password_hash(admin_password), "Admin")
            )

    conn.commit()
    conn.close()
