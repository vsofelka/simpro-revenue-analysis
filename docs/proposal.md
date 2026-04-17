# Project Proposal

**Student:** Victor Sofelkanik
**Course:** ISBA 4715 — Analytics Engineering, Loyola Marymount University
**Project Name:** Simpro RevOps Pipeline Analytics
**Target Role:** Revenue Operations Analyst — Simpro Group (Los Angeles, CA)

---

## Job Posting Summary

The Revenue Operations Analyst at Simpro Group is responsible for delivering trusted, actionable insights to support go-to-market teams and executive leadership. Core responsibilities include building and maintaining operational dashboards, partnering with Data Engineering on pipeline reliability, owning Board-level reporting accuracy, and conducting ad hoc analyses to surface revenue trends and drivers. The role requires strong SQL skills, experience with cloud data warehouses, and the ability to communicate findings to both technical and non-technical stakeholders. Simpro Group is a SaaS field service management company serving 22,000+ businesses worldwide.

---

## Problem Statement

Revenue Operations teams at SaaS companies struggle to answer critical pipeline questions — where deals get stuck, which lead sources convert best, and how deal velocity trends over time — because CRM data is often siloed, inconsistently modeled, and inaccessible to non-technical stakeholders. Without a reliable, well-modeled data layer and self-service dashboards, RevOps analysts spend more time wrangling data than generating insights.

---

## Proposed Data Sources

1. **HubSpot CRM API** — Deal records, contact data, and pipeline stage history extracted daily via Python. Loaded into Snowflake as raw tables (`RAW.HUBSPOT_DEALS`, `RAW.HUBSPOT_CONTACTS`).
2. **Firecrawl Web Scrape** — Scraped Simpro product pages, G2 reviews, and competitor content scraped weekly and stored as markdown files in `knowledge/raw/` to enrich business context.

---

## Solution Overview

This project builds an end-to-end analytics engineering pipeline that mirrors the technical stack and responsibilities of the target role:

- **Extract:** Python scripts pull data from the HubSpot CRM API and Firecrawl on automated schedules via GitHub Actions
- **Load:** Raw data lands in Snowflake for centralized storage
- **Transform:** dbt models clean and structure the data into a star schema (staging layer → mart layer) with documented metrics
- **Visualize:** A Streamlit dashboard delivers self-service views on pipeline health, lead source performance, deal velocity, and conversion rates

The output directly addresses the four key business questions a RevOps analyst at Simpro would face: pipeline bottlenecks, lead source ROI, deal velocity trends, and close probability drivers.
