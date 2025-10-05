# OSINT Dashboard (MVP)

A tiny, learning-first OSINT pipeline that ingests RSS feeds into SQLite and prints recent items. Built to iterate quickly and showcase progress while I learn better prompting, agent workflows, and data engineering basics.

## Please view [this Notion link](https://www.notion.so/OSINT-Web-Scraper-Dashboard-Name-TBD-2773c0690a6080059cb8f6f63dd70e0c?source=copy_link) for full dev log

## Current features
*   Output a list of 5 events from UN news featuring a headline and article link.
*   Collect UN news into a database.

## Roadmap (short)

*   Add duplicate protection (UNIQUE on `link`) and `INSERT OR IGNORE`
*   Basic FastAPI service to serve `/events` and `/health`
*   Dockerfile + GitHub Actions CI
*   Lightweight web UI (Next.js or simple Flask/Jinja)
*   Add more sources (official gov/IGO/NGO feeds), per-source parsers
*   Basic enrichment (language, geo tags) + source tagging

## Learning goals

*   Experiment with AI (prompting, NLP/ML)
*   Compare assistant tools (VS Code extension, Codex web, etc.)
*   Build small, testable components and iterate quickly
*   Document decisions and issues in Notion

## Quickstart

```
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Ingest default feed and show latest
python main.py

# Or ingest specific feeds and dump JSON
python app/rss_ingest.py https://apnews.com/rss https://www.reuters.com/rssFeed/world --json events.json
```

## Project Layout

```
OSINT Dashboard/
├── app/
│   └── rss_ingest.py
├── db/
│   ├── db_utils.py
│   └── schema.sql
├── learning/
│   └── test.py
├── main.py
├── requirements.txt
└── .gitignore
```