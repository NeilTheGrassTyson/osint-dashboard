import feedparser
import re
from typing import List, Dict
from urllib.parse import urlparse
import argparse
import json
from pathlib import Path
from time import strftime
from db.db_utils import init_db, insert_event
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo
from datetime import datetime, timezone, timedelta

GEOPOL_KEYWORDS = {
    # conflict/war
    "war",
    "conflict",
    "airstrike",
    "air strike",
    "missile",
    "rocket",
    "drone strike",
    "shelling",
    "ceasefire",
    "cease-fire",
    "truce",
    "front line",
    "offensive",
    "raid",
    "hostage",
    "militia",
    "military",
    "army",
    "troops",
    "insurgent",
    "insurgency",
    "terror",
    "terrorist",
    "uprising",
    "coup",
    "occupation",
    "nuclear",
    "airspace",
    "blockade",
    "border",
    "carrier strike group",
    # diplomacy/governance
    "sanction",
    "embargo",
    "treaty",
    "talks",
    "negotiation",
    "summit",
    "diplomat",
    "ambassador",
    "parliament",
    "cabinet",
    "coalition",
    "regime",
    "election",
    "ballot",
    "referendum",
    "prime minister",
    "president",
    "defense minister",
    "secretary of",
    "minister",
    "department of war",
    "department of defense",
    # orgs & hot spots
    "nato",
    "security council",
    "eu",
    "e.u.",
    "moscow",
    "kyiv",
    "gaza",
    "west bank",
    "taiwan",
    "south china sea",
    "horn of africa",
    "yemen",
    "syria",
    "iraq",
    "afghanistan",
    "libya",
    "venezuela",
    "north korea",
    "nigeria",
    "sudan",
    "israel",
    "ukraine"
    "pentagon",
    "kremlin",
    "ministry of defense",
    "state department",
    "cia",
    "brics",
    "norad",
    "centcom",
    "eurocom",
    "africom",
    "indopacom",
}

# Precompile word-boundary regexes (phrases handled as-is)
_KEYWORD_PATTERNS = [re.compile(rf"\b{re.escape(k)}\b", re.I) for k in GEOPOL_KEYWORDS]

# Precompile false positive pattern to avoid mistaking labor strikes for political protests 
_FALSE_POSITIVE_PATTERNS = [
    re.compile(r"\blabor strike\b", re.I),
]

# Precopile HTML tag remover
_HTML_TAGS = re.compile(r"<[^>]+>")

# set up local timezone (EST/EDT) for local time display
try:
    from zoneinfo import ZoneInfo
    LOCAL_TZ = ZoneInfo("America/New_York")  # DST-aware if tzdata installed
except Exception:
    # Fallback: fixed -05:00 (EST) without DST, no external deps
    LOCAL_TZ = timezone(timedelta(hours=-5), name="EST")

def _count_hits(text: str) -> int:
    # Count distinct keyword/phrase matches in text (case-insensitive).
    text = text.lower()
    hits = 0
    for pat in _KEYWORD_PATTERNS:
        if pat.search(text):
            hits += 1
    return hits


def _is_false_positive(text: str) -> bool:
    # Check if text matches any false positive patterns.
    return any(pat.search(text) for pat in _FALSE_POSITIVE_PATTERNS)


def _is_geopolitics(entry, source_host: str) -> bool:
    # Threshold-only filter: require N keyword hits. Title hits get a small bonus to reduce false positives.
    title = entry.get("title") or ""
    summary = entry.get("summary") or entry.get("description") or ""

    # Per-source thresholds (tune as needed). Number indicates minimum hits required.
    if "news.un" in source_host:
        threshold = 1  # UN is already topical
    elif "bbc" in source_host or "news.google" in source_host:
        threshold = 2  # generalist feeds: be stricter
    else:
        threshold = 3  # default

    blob = f"{title} {summary}"
    if _is_false_positive(blob):
        return False
    body_hits = _count_hits(blob)
    title_hits = _count_hits(title)

    score = body_hits + (1 if title_hits else 0)  # title bonus

    return score >= threshold

def _clean_html(s: str) -> str:
    return _HTML_TAGS.sub("", s or "").strip()

def _parse_dt(entry) -> datetime | None:
    # Try RFC-822-like strings with timezone first
    for key in ("published", "updated", "dc:date", "date"):
        s = entry.get(key)
        if s:
            try:
                dt = parsedate_to_datetime(s)
                return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
            except Exception:
                pass
    # Fall back to feedparser struct_time (assumed UTC)
    for key in ("published_parsed", "updated_parsed", "created_parsed", "expired_parsed", "date_parsed"):
        t = entry.get(key)
        if t:
            try:
                return datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec, tzinfo=timezone.utc)
            except Exception:
                pass
    return None

def _iso_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

def _iso_local(dt: datetime) -> str:
    return dt.astimezone(LOCAL_TZ).isoformat(timespec="seconds")

def parse_items(feed, url) -> List[Dict]:
    events: List[Dict] = []
    seen = set()  # prevent duplicates across overlapping feeds
    host = urlparse(url).netloc
    source_title = feed.get("feed", {}).get("title", "") or host

    for entry in feed.entries:
        if not _is_geopolitics(entry, host):
            continue

        title = (entry.get("title") or "").strip()
        link = (entry.get("link") or "").strip()
        if not title or not link:
            continue

        # de-dupe by (title, link)
        dedupe_key = (title.lower(), link.lower())
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)

        # compute times
        src_dt = _parse_dt(entry) or datetime.now(timezone.utc)
        now_utc = datetime.now(timezone.utc)

        event = {
            "title": title,
            "link": link,
            "published_utc": _iso_utc(src_dt),          # canonical
            "published_local": _iso_local(src_dt),      # EST/EDT for display
            "ingested_utc": _iso_utc(now_utc),          # when event was ingested
            "latency_sec": int((now_utc - src_dt.astimezone(timezone.utc)).total_seconds()),
            "summary": _clean_html(entry.get("summary") or entry.get("description") or ""),
            "source": source_title,
        }
        events.append(event)

        # persist to DB; insert_event takes a dict, so pass event directly
        try:
            insert_event(event)
        except Exception:
            pass

    return events


def fetch_rss(url: str):
    # Fetch and parse RSS/Atom feed from a given URL
    return feedparser.parse(url)


def save_to_json(events, filename: str = "events.json"):
    # Save parsed events to JSON file.
    Path(filename).write_text(
        json.dumps(events, indent=4, ensure_ascii=False), encoding="utf-8"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OSCENT: RSS Ingestor")
    parser.add_argument(
        "feeds",
        nargs="*",
        help="Feed URLs to ingest",
        default="https://news.un.org/feed/subscribe/en/news/all/rss.xml",
    )

    parser.add_argument(
        "--json", dest="json", help="Optional path to write events.json", default=None
    )
    args = parser.parse_args()

    init_db()
    all_events = []
    for url in args.feeds:
        feed = fetch_rss(url)
        events = parse_items(feed, url)
        all_events.extend(events)

    out = args.json or "events.json"
    save_to_json(all_events, out)
    print(f"💾 Wrote {len(all_events)} filtered events to {out}")
    print(f"✅ Ingested {len(all_events)} events from {len(args.feeds)} feed(s).")
