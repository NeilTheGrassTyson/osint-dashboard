from db.db_utils import init_db
from app.rss_ingest import fetch_rss, parse_items

def main():
    init_db()

    feeds = [
        "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
        "https://www.reutersagency.com/feed/?best-topics=world&post_type=best",
        "https://feeds.bbci.co.uk/news/world/rss.xml"
    ]

    total_events = 0
    for url in feeds:
        feed = fetch_rss(url)
        events = parse_items(feed, url)
        total_events += len(events)
        print(f"Ingested {len(events)} events from {url}")

    print(f"\n✅ Ingested {total_events} total events from {len(feeds)} feed(s).")

if __name__ == "__main__":
    main()