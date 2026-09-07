import sqlite3
import json
from typing import Optional, Dict, Any

DB_PATH = "data/tasks.db"


def init_db():
    """Initializes the SQLite database and creates the tasks table if it does not exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            summary TEXT,
            artifacts TEXT,
            error TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_task(task_id: str, status: str = "queued"):
    """Saves a new task or updates the status of an existing task."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (task_id, status, summary, artifacts, error)
        VALUES (?, ?, '', '[]', NULL)
        ON CONFLICT(task_id) DO UPDATE SET status=excluded.status
    """, (task_id, status))
    conn.commit()
    conn.close()


def update_task_result(task_id: str, status: str, summary: str = "", artifacts: list = None, error: Optional[str] = None):
    """Updates the final completion result for a finished or failed task."""
    artifacts_json = json.dumps(artifacts if artifacts else [])
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tasks
        SET status = ?, summary = ?, artifacts = ?, error = ?
        WHERE task_id = ?
    """, (status, summary, artifacts_json, error, task_id))
    conn.commit()
    conn.close()


def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a task by its task_id from SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT task_id, status, summary, artifacts, error FROM tasks WHERE task_id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "task_id": row[0],
            "status": row[1],
            "summary": row[2],
            "artifacts": json.loads(row[3]) if row[3] else [],
            "error": row[4]
        }
    return None