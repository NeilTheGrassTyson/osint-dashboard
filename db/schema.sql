CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    link TEXT,
    published TEXT,
    summary TEXT,
    source TEXT,
    UNIQUE(link)
);
