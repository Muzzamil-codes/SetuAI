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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            model TEXT NOT NULL,
            messages TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_conversation(conv_data: Dict[str, Any]):
    """Saves or updates a conversation."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO conversations (id, title, model, messages, created_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET 
            title=excluded.title,
            model=excluded.model,
            messages=excluded.messages,
            created_at=excluded.created_at
    """, (
        conv_data["id"],
        conv_data["title"],
        conv_data["model"],
        json.dumps(conv_data["messages"]),
        conv_data.get("createdAt", "")
    ))
    conn.commit()
    conn.close()

def get_conversations() -> list:
    """Retrieves all conversations, sorted by created_at descending."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, model, messages, created_at FROM conversations ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        result.append({
            "id": row[0],
            "title": row[1],
            "model": row[2],
            "messages": json.loads(row[3]) if row[3] else [],
            "createdAt": row[4]
        })
    return result

def delete_conversation(conv_id: str):
    """Deletes a conversation by ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
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