import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "events.db"
SCHEMA_FILE = BASE_DIR / "db" / "schema.sql"

def init_db() -> None:
    # Initialize the SQLite database using schema.sql (idempotent)
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    try:
        with conn:
            schema = SCHEMA_FILE.read_text(encoding="utf-8")
            conn.executescript(schema)
    finally:
        conn.close()

def insert_event(event: Dict[str, Any]) -> None:
    # Insert one event into the database.
    conn = sqlite3.connect(DB_FILE)
    try:
        with conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO events (title, link, published, summary, source)
                VALUES (:title, :link, :published, :summary, :source)
                """.strip(),
                {
                    "title": event.get("title", ""),
                    "link": event.get("link", ""),
                    "published": event.get("published", ""),
                    "summary": event.get("summary", ""),
                    "source": event.get("source", ""),
                },
            )
    finally:
        conn.close()


def fetch_events(limit: int = 10) -> List[Dict[str, Optional[str]]]:
    # Fetch latest N events from database, newest-first by row id.
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute(
            "SELECT id, title, link, published, summary, source FROM events ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()
