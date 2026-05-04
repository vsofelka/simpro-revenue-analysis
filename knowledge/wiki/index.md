# Knowledge Base Index

Claude Code-generated wiki covering Simpro Group, field service management, and competitive landscape. Built from 15+ scraped sources across simprogroup.com, G2, Capterra, GetApp, and competitor sites.

## Wiki Pages

| Page | Summary |
|---|---|
| [overview.md](overview.md) | Simpro company overview: products, market position, scale, revenue model, key metrics |
| [key-entities.md](key-entities.md) | Key companies, competitor profiles, buyer personas, and integration partners |
| [themes.md](themes.md) | Seven synthesized themes across all sources: buying triggers, sentiment patterns, competitive dynamics |

## Raw Sources

All scraped source documents live in `knowledge/raw/`. Each file is named by source and begins with the URL it was scraped from.

| File | Source |
|---|---|
| `simpro_about.md` | simprogroup.com/about-us |
| `simpro_features.md` | simprogroup.com/features |
| `simpro_pricing.md` | simprogroup.com/pricing |
| `simpro_customers.md` | simprogroup.com/customers |
| `simpro_blog.md` | simprogroup.com/blog |
| `g2_simpro_reviews.md` | g2.com — simPRO reviews |
| `capterra_simpro_reviews.md` | capterra.com — simPRO reviews |
| `capterra_fsm_comparison.md` | capterra.com — FSM software comparison |
| `getapp_simpro.md` | getapp.com — simPRO profile |
| `getapp_fsm_category.md` | getapp.com — FSM category |
| `softwareadvice_simpro.md` | softwareadvice.com — simPRO profile |
| `techradar_fsm_software.md` | techradar.com — best FSM software roundup |
| `servicetitan_about.md` | servicetitan.com/about |
| `servicetitan_features.md` | servicetitan.com/features |
| `jobber_about.md` | getjobber.com/about |
| `jobber_features.md` | getjobber.com/features |
| `fieldedge_about.md` | fieldedge.com/about-us |

## How to Query

Open Claude Code from the repo root and ask natural-language questions:

- "What are the main pain points Simpro customers report on G2?"
- "Who are Simpro's main competitors and how do they differ?"
- "What RevOps metrics matter most to SaaS field service companies?"
- "What does the knowledge base say about Simpro's pricing model?"
- "How does Simpro compare to ServiceTitan?"
- "What are the most common reasons customers churn from simPRO?"

Claude Code reads wiki pages first, then falls back to raw sources for detail.
