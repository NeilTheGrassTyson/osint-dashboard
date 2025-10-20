import sqlite3
from pathlib import Path

DB_FILE = "events.db"
SCHEMA_FILE = Path(__file__).parent / "schema.sql"

def init_db():
    # Initialize database with schema if it doesn't exist.
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Read and execute schema.sql
    if Path(SCHEMA_FILE).exists():
        with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
            cur.executescript(f.read())
    else:
        raise FileNotFoundError(f"{SCHEMA_FILE} not found.")

    conn.commit()
    conn.close()


def insert_event(event: dict):

    # Insert one event into the database
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM events WHERE link = ?",
        (event.get("link", ""),)
    )

    # Prevent duplicate entries based on link
    if cur.fetchone()[0] == 0:
        cur.execute(
            """
            INSERT INTO events (title, link, published, summary, source)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                event.get("title", ""),
                event.get("link", ""),
                event.get("published", ""),
                event.get("summary", ""),
                event.get("source", ""),
            ),
        )

    conn.commit()
    conn.close()


def fetch_events(limit=10):
    # Fetch the latest N events from the database.
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute(
        "SELECT id, title, link, published, summary, source FROM events ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    results = cur.fetchall()

    conn.close()
    return results