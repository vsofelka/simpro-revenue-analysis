# CLAUDE.md — Project Context

## Project Overview

This is an analytics engineering portfolio project built for the Loyola Marymount University Analytics Engineering course. The project targets the **Revenue Operations Analyst** role at **Simpro Group** and demonstrates end-to-end data pipeline skills: API extraction, Snowflake loading, dbt transformation, and Streamlit dashboarding.

**Repo:** https://github.com/vsofelka/sports-data-analysis
**Student:** Victor Sofelkanik
**Stack:** Python · HubSpot API · Firecrawl · Snowflake · dbt · GitHub Actions · Streamlit

---

## Repository Structure

```
├── docs/                   # Proposal, job posting, resume
├── pipeline/               # Python extraction scripts
│   ├── hubspot_extract.py  # HubSpot CRM API → Snowflake raw
│   └── firecrawl_scrape.py # Firecrawl web scrape → knowledge/raw/
├── dbt/                    # dbt project
│   ├── models/
│   │   ├── staging/        # stg_deals, stg_contacts, stg_stages
│   │   └── mart/           # fct_deals, dim_contacts, dim_stages, dim_date
│   └── dbt_project.yml
├── streamlit/              # Streamlit dashboard app
│   └── app.py
├── knowledge/              # Knowledge base
│   ├── raw/                # Scraped source documents (15+ files)
│   └── wiki/               # Claude Code-generated synthesis pages
│       ├── index.md
│       ├── overview.md
│       ├── key-entities.md
│       └── themes.md
├── .github/
│   └── workflows/          # GitHub Actions pipelines
├── .gitignore
├── requirements.txt
└── CLAUDE.md               # This file
```

---

## Data Pipeline

### Source 1: HubSpot CRM API
- **Script:** `pipeline/hubspot_extract.py`
- **Loads to:** Snowflake `RAW.HUBSPOT_DEALS`, `RAW.HUBSPOT_CONTACTS`
- **Schedule:** Daily via GitHub Actions
- **Credentials:** `HUBSPOT_API_KEY`, `SNOWFLAKE_*` env vars (never committed)

### Source 2: Firecrawl Web Scrape
- **Script:** `pipeline/firecrawl_scrape.py`
- **Loads to:** `knowledge/raw/` as markdown files
- **Schedule:** Weekly via GitHub Actions
- **Credentials:** `FIRECRAWL_API_KEY` env var (never committed)

---

## dbt Models

### Staging Layer
- `stg_deals` — cleaned deal records from HubSpot (renamed columns, cast types, null handling)
- `stg_contacts` — cleaned contact/lead records
- `stg_pipeline_stages` — pipeline stage reference data

### Mart Layer (Star Schema)
- `fct_deals` — fact table: one row per deal, foreign keys to all dimensions
- `dim_contacts` — contact dimension
- `dim_stages` — pipeline stage dimension
- `dim_date` — date spine for time-series analysis

---

## Dashboard

**App:** `streamlit/app.py`
**Deployed:** Streamlit Community Cloud (public URL in README)

Key views:
- **Descriptive:** Pipeline stage breakdown, revenue by lead source, deal count over time
- **Diagnostic:** Deal velocity analysis, conversion rate by source, win/loss drivers
- **Interactive:** Stage filter, date range selector, source filter

---

## Knowledge Base

### How to Query the Knowledge Base

To ask questions about the knowledge base, run Claude Code from the repo root and ask:

> "What does my knowledge base say about [topic]?"

Claude Code will read `knowledge/wiki/` pages and `knowledge/raw/` sources to answer. Wiki pages are the primary reference; raw sources provide supporting detail.

### Wiki Page Conventions
- `knowledge/wiki/index.md` — index of all wiki pages with one-line summaries
- `knowledge/wiki/overview.md` — company overview, product, market position
- `knowledge/wiki/key-entities.md` — key companies, competitors, personas, products
- `knowledge/wiki/themes.md` — synthesized themes across all sources

### Query Examples
- "What are the main pain points Simpro customers report on G2?"
- "Who are Simpro's main competitors and how do they differ?"
- "What RevOps metrics matter most to SaaS field service companies?"
- "What does the knowledge base say about Simpro's pricing model?"

---

## Environment Variables

Never commit credentials. All secrets stored as GitHub Actions secrets and local `.env` file (gitignored).

```
HUBSPOT_API_KEY=
SNOWFLAKE_ACCOUNT=
SNOWFLAKE_USER=
SNOWFLAKE_PASSWORD=
SNOWFLAKE_DATABASE=
SNOWFLAKE_WAREHOUSE=
SNOWFLAKE_SCHEMA=
FIRECRAWL_API_KEY=
```

---

## Key Business Questions This Project Answers

1. Where are deals getting stuck in the sales pipeline?
2. Which lead sources drive the highest conversion rates and revenue?
3. How does deal velocity trend over time?
4. What factors predict deal close probability?
