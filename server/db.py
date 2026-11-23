import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "campus.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0,
                due_date TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )


def list_todos() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, title, done, due_date, created_at FROM todos ORDER BY id"
        ).fetchall()
    return [dict(row) for row in rows]


def create_todo(title: str, due_date: str | None = None) -> dict:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO todos (title, due_date) VALUES (?, ?)",
            (title, due_date),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id, title, done, due_date, created_at FROM todos WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
    return dict(row)


def update_todo_done(todo_id: int, done: bool) -> dict | None:
    with get_connection() as conn:
        conn.execute("UPDATE todos SET done = ? WHERE id = ?", (int(done), todo_id))
        conn.commit()
        row = conn.execute(
            "SELECT id, title, done, due_date, created_at FROM todos WHERE id = ?",
            (todo_id,),
        ).fetchone()
    return dict(row) if row else None


def delete_todo(todo_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        conn.commit()
    return cursor.rowcount > 0
