---
marp: true
theme: gaia
class: invert
paginate: true
html: true
---

<style>
.pipeline-flow {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin: 24px 0;
}
.pipeline-box {
  background: #1a4a7a;
  border: 2px solid #4fc3f7;
  border-radius: 10px;
  padding: 14px 18px;
  text-align: center;
  font-size: 0.72em;
  line-height: 1.5;
  min-width: 110px;
}
.pipeline-arrow {
  font-size: 1.6em;
  color: #4fc3f7;
}
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin: 20px 0;
}
.kpi-box {
  background: #1a3a5c;
  border-radius: 10px;
  padding: 16px 10px;
  text-align: center;
}
.kpi-value {
  font-size: 1.6em;
  font-weight: bold;
  color: #4fc3f7;
}
.kpi-label {
  font-size: 0.65em;
  color: #aaa;
  margin-top: 4px;
}
.callout {
  background: #f39c12;
  color: #000;
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 0.72em;
  font-weight: bold;
  margin-top: 8px;
  display: inline-block;
  line-height: 1.4;
}
.rec-box {
  background: #0a2233;
  border-left: 5px solid #4fc3f7;
  border-radius: 8px;
  padding: 16px 20px;
  margin: 12px 0;
  font-size: 0.78em;
  line-height: 1.6;
}
.action { color: #ffffff; font-weight: bold; }
.outcome { color: #90caf9; font-weight: bold; }
.skills-table th { background: #1a3a5c; }
</style>

<!-- _class: lead invert -->

# Simpro RevOps Pipeline Analytics

Building the Analytics Layer a Revenue Operations Analyst Uses on Day One

**Victor Sofelkanik** · Loyola Marymount University · ISBA 4715 · May 2026

---

## What I Built

<div class="pipeline-flow">
  <div class="pipeline-box"><strong>HubSpot API</strong><br>Deals · Contacts<br>Stages</div>
  <div class="pipeline-arrow">→</div>
  <div class="pipeline-box"><strong>Snowflake</strong><br>RAW Layer<br>226 Deals</div>
  <div class="pipeline-arrow">→</div>
  <div class="pipeline-box"><strong>dbt</strong><br>Star Schema<br>4 Models</div>
  <div class="pipeline-arrow">→</div>
  <div class="pipeline-box"><strong>Streamlit</strong><br>Live Dashboard<br>Deployed</div>
</div>

<div class="kpi-grid">
  <div class="kpi-box"><div class="kpi-value">226</div><div class="kpi-label">Total Deals</div></div>
  <div class="kpi-box"><div class="kpi-value">$13.5M</div><div class="kpi-label">Pipeline Value</div></div>
  <div class="kpi-box"><div class="kpi-value">$59,951</div><div class="kpi-label">Avg Deal Size</div></div>
  <div class="kpi-box"><div class="kpi-value">31.9%</div><div class="kpi-label">Win Rate</div></div>
</div>

Automated daily via **GitHub Actions** · Modeled in **dbt** · Served in **Streamlit**

---

<p style="font-size:0.55em; color:#4fc3f7; text-transform:uppercase; letter-spacing:2px; margin:0 0 6px 0;">Descriptive Insight</p>
<p style="font-size:0.82em; font-weight:bold; margin:0 0 10px 0; line-height:1.3;">"Closed Won Dominates Pipeline Value — 5 of 7 Open Stages Stall Below $1.5M"</p>

![bg right:58% fit](./pipeline-stage-chart.png)

<div class="callout">
  Closed Won: $5M+ &nbsp;|&nbsp; Next open stage: $2.3M<br>
  5 of 7 stages stuck below $1.5M<br>
  Opportunity: accelerate open deals, not generate new ones
</div>

---

## Diagnostic Insight

#### "Deals That Close Lost Take 27% Longer Than Wins — Velocity Is a Leading Indicator of Outcome"

![bg right:52% fit](./velocity-chart.png)

<div class="callout">
  Closed Lost: 60.4 days &nbsp;|&nbsp; Closed Won: 47.4 days<br>
  Gap: 13 days — outcome is predictable
</div>

<ul style="font-size:0.7em; margin-top:6px; line-height:1.4;">
  <li>Lost deals linger and slow before the final outcome</li>
  <li>Won deals close decisively in under 50 days</li>
  <li>Every day past 50 days increases loss probability</li>
</ul>

---

## Recommendation

<div class="rec-box">
  <span class="action">Implement a structured 5-day follow-up sequence for all open deals exceeding 50 days in any stage</span>
  <br><br>
  → <span class="outcome">Expected to reduce average cycle time from 60 to under 50 days and shift stalling deals toward Closed Won within one quarter</span>
</div>

<ul style="font-size:0.72em; margin-top:8px; line-height:1.4;">
  <li>Data shows a clear 50-day threshold separating wins from losses</li>
  <li>Timed intervention addresses drop-off before it becomes a closed loss</li>
  <li>Targets the exact velocity gap the diagnostic analysis identified</li>
</ul>

---

<p style="font-size:0.55em; color:#4fc3f7; text-transform:uppercase; letter-spacing:2px; margin:0 0 6px 0;">Skills Demonstrated</p>

<div style="font-size:0.62em;">

| JD Requirement | Project Evidence |
|---|---|
| SQL + cloud data warehouse | Snowflake + dbt staging and mart models |
| Dashboard and report building | Streamlit + Plotly, live and deployed |
| Data pipeline + modeling | GitHub Actions cron · dbt star schema · dbt tests |
| Non-technical communication | Takeaway titles, callouts, plain-language insights |

</div>

