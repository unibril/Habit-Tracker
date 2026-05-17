import sqlite3
import os
from datetime import date

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "habits.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True) 
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets you access columns by name
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at DATE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            logged_date DATE NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits(id),
            UNIQUE(habit_id, logged_date)  -- prevent duplicate logs for same day
        );
    """)

    conn.commit()
    conn.close()


# --- Habits ---

def add_habit(name: str) -> bool:
    """Add a new habit. Returns False if it already exists."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO habits (name, created_at) VALUES (?, ?)",
            (name.strip(), date.today())
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # duplicate
    finally:
        conn.close()


def delete_habit(name: str) -> bool:
    """Delete a habit and all its logs."""
    conn = get_connection()
    cursor = conn.cursor()
    habit = cursor.execute("SELECT id FROM habits WHERE name = ?", (name,)).fetchone()
    if not habit:
        conn.close()
        return False
    cursor.execute("DELETE FROM logs WHERE habit_id = ?", (habit["id"],))
    cursor.execute("DELETE FROM habits WHERE id = ?", (habit["id"],))
    conn.commit()
    conn.close()
    return True


def get_all_habits() -> list:
    conn = get_connection()
    habits = conn.execute("SELECT * FROM habits ORDER BY created_at").fetchall()
    conn.close()
    return [dict(h) for h in habits]


def get_habit_by_name(name: str):
    conn = get_connection()
    habit = conn.execute("SELECT * FROM habits WHERE name = ?", (name,)).fetchone()
    conn.close()
    return dict(habit) if habit else None


# --- Logs ---

def log_habit(name: str, log_date: date = None) -> str:
    """
    Mark a habit as done for a given date.
    Returns 'ok', 'already_logged', or 'not_found'.
    """
    if log_date is None:
        log_date = date.today()

    conn = get_connection()
    cursor = conn.cursor()

    habit = cursor.execute("SELECT id FROM habits WHERE name = ?", (name,)).fetchone()
    if not habit:
        conn.close()
        return "not_found"

    try:
        cursor.execute(
            "INSERT INTO logs (habit_id, logged_date) VALUES (?, ?)",
            (habit["id"], log_date)
        )
        conn.commit()
        return "ok"
    except sqlite3.IntegrityError:
        return "already_logged"
    finally:
        conn.close()


def unlog_habit(name: str, log_date: date = None) -> bool:
    """Remove a log entry (undo a log)."""
    if log_date is None:
        log_date = date.today()

    conn = get_connection()
    cursor = conn.cursor()
    habit = cursor.execute("SELECT id FROM habits WHERE name = ?", (name,)).fetchone()
    if not habit:
        conn.close()
        return False
    cursor.execute(
        "DELETE FROM logs WHERE habit_id = ? AND logged_date = ?",
        (habit["id"], log_date)
    )
    conn.commit()
    conn.close()
    return True


def get_logs_for_habit(habit_id: int) -> list:
    """Return all logged dates for a habit as a list of date strings."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT logged_date FROM logs WHERE habit_id = ? ORDER BY logged_date",
        (habit_id,)
    ).fetchall()
    conn.close()
    return [row["logged_date"] for row in rows]


def get_all_logs() -> list:
    """Return all logs joined with habit names."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT h.name, l.logged_date
        FROM logs l
        JOIN habits h ON l.habit_id = h.id
        ORDER BY l.logged_date DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def is_logged_today(habit_id: int) -> bool:
    conn = get_connection()
    row = conn.execute(
        "SELECT 1 FROM logs WHERE habit_id = ? AND logged_date = ?",
        (habit_id, date.today())
    ).fetchone()
    conn.close()
    return row is not None
