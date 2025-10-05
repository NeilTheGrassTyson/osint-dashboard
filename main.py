from db.db_utils import init_db, fetch_events
from app.rss_ingest import fetch_rss, parse_items

DEFAULT_FEEDS = [
    "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
]

def ingest_default():
    init_db()
    for url in DEFAULT_FEEDS:
        feed = fetch_rss(url)
        parse_items(feed)

def show_latest(n: int = 5):
    events = fetch_events(limit=n)
    for e in events:
        print(f"- {e['title']} ({e['source']})\n  {e['link']}\n")

if __name__ == "__main__":
    ingest_default()
    show_latest(5)
