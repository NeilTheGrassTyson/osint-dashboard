import feedparser
from typing import List, Dict
from urllib.parse import urlparse
import argparse
import json
from pathlib import Path

from db.db_utils import init_db, insert_event

def fetch_rss(url: str):
    # Fetch and parse RSS/Atom feed from a given URL
    return feedparser.parse(url)

def parse_items(feed) -> List[Dict]:
    # Extract relevant fields from RSS items and persist them.
    events = []
    source_title = feed.get('feed', {}).get('title', '') or urlparse(feed.get('href', '') or '').netloc
    for entry in feed.entries:
        event = {
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "published": entry.get("published", "") or entry.get("updated", ""),
            "summary": entry.get("summary", "") or entry.get("description", ""),
            "source": source_title,
        }
        events.append(event)
        insert_event(event)
    return events

def save_to_json(events, filename: str = "events.json"):
    # Save parsed events to JSON file. 
    Path(filename).write_text(json.dumps(events, indent=4, ensure_ascii=False), encoding="utf-8")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OSINT Dashboard: RSS Ingestor")
    parser.add_argument("feeds", nargs="*", help="Feed URLs to ingest",
                        default=["https://news.un.org/feed/subscribe/en/news/all/rss.xml"])
    parser.add_argument("--json", dest="json", help="Optional path to write events.json", default=None)
    args = parser.parse_args()

    init_db()
    all_events = []
    for url in args.feeds:
        feed = fetch_rss(url)
        events = parse_items(feed)
        all_events.extend(events[:3])  # keep a small sample for combined JSON

    if args.json:
        save_to_json(all_events, args.json)

    print(f"Ingested {len(all_events)} events from {len(args.feeds)} feed(s).")
