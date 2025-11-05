# OSCENT: Open Source Central Intelligence

A tiny, learning-first OSINT pipeline that ingests RSS feeds into SQLite and prints recent items. Built to iterate quickly and showcase progress while I learn better prompting, agent workflows, and data engineering basics. 

## Please view [this Notion link](https://www.notion.so/OSINT-Web-Scraper-Dashboard-Name-TBD-2773c0690a6080059cb8f6f63dd70e0c?source=copy_link) for full dev log

## Current features
*   Ingest current geopolitical events from various sources. Includes an article title, summary, and link. Currently supporting:
    *   UN News
    *   AP
    *   BBC
*   Store events in a database

## Roadmap

*   Basic FastAPI service to serve `/events` and `/health`
*   Dockerfile + GitHub Actions CI
*   Lightweight web UI (Next.js or simple Flask/Jinja)
*   Add more sources (official gov/IGO/NGO feeds), per-source parsers
*   Basic enrichment (language, geo tags) + source tagging
*   Add support for specific RSS links with starting
*   Full map and visualization dashboard for event tracking

## Learning goals

*   Experiment with AI (prompting, NLP/ML)
*   Compare assistant tools (VS Code extension, Codex web, etc.)
*   Build small, testable components and iterate quickly
*   Document decisions and issues in Notion
*   Learn front-end development for dashboard (React + TypeScript)

## Quickstart

```
python -m venv .venv && source .venv/bin/activate    
    # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Ingest default feed and show latest
python main.py
```

## Project Layout

```
OSINT Dashboard/
├── app/
│   └── rss_ingest.py
├── db/
│   ├── db_utils.py
│   └── schema.sql
├── main.py
├── requirements.txt
└── .gitignore
```