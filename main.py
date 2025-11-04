from db.db_utils import init_db
from app.rss_ingest import fetch_rss, parse_items, save_to_json


def main():
    init_db()

    feeds = [
        "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
        "https://news.google.com/rss/search?q=site:apnews.com&hl=en-US&gl=US&ceid=US:en",
        "https://feeds.bbci.co.uk/news/world/rss.xml",
    ]

    total_events = 0
    all_events = []
    for url in feeds:
        feed = fetch_rss(url)
        events = parse_items(feed, url)
        all_events.extend(events)
        total_events += len(events)
        print(f"Ingested {len(events)} events from {url}")

    save_to_json(all_events, "events.json")
    print(f"\n✅ Ingested {total_events} total events from {len(feeds)} feed(s).")
    print(f"💾 Wrote {len(all_events)} events to events.json")


if __name__ == "__main__":
    main()
