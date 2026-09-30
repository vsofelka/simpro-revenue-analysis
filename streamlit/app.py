import json

import streamlit as st
import pandas as pd
import plotly.express as px

import data_source

st.set_page_config(
    page_title="Simpro RevOps Dashboard",
    page_icon="📊",
    layout="wide",
)


def _secrets():
    # st.secrets raises if no secrets are configured at all; treat that as "none"
    try:
        return st.secrets.to_dict()
    except Exception:
        return {}


@st.cache_data(ttl=3600)
def load_deals():
    # Snowflake when credentials are configured and working, otherwise the
    # saved snapshot (see streamlit/data_source.py)
    return data_source.load_deals(_secrets())


# ── Load data ──────────────────────────────────────────────────────────────────
df, data_source_used = load_deals()

df["created_date"] = pd.to_datetime(df["created_date"])
df["close_date"] = pd.to_datetime(df["close_date"])
df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

# ── Sidebar filters ─────────────────────────────────────────────────────────────
st.sidebar.header("Filters")

min_date = df["created_date"].min().date()
max_date = df["created_date"].max().date()
date_range = st.sidebar.date_input(
    "Created Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

all_stages = sorted(df["stage_name"].dropna().unique().tolist())
selected_stages = st.sidebar.multiselect(
    "Pipeline Stage",
    options=all_stages,
    default=all_stages,
)

# ── Filter ──────────────────────────────────────────────────────────────────────
if len(date_range) == 2:
    fdf = df[
        (df["created_date"].dt.date >= date_range[0])
        & (df["created_date"].dt.date <= date_range[1])
        & (df["stage_name"].isin(selected_stages))
    ]
else:
    fdf = df[df["stage_name"].isin(selected_stages)]

# ── Header ──────────────────────────────────────────────────────────────────────
st.title("Simpro RevOps Pipeline Analytics")
st.caption(
    "Sales pipeline insights powered by HubSpot CRM · Victor Sofelkanik · LMU ISBA 4715"
)
if data_source_used == "snapshot":
    info = json.loads((data_source.SNAPSHOT_PATH.parent / "snapshot_info.json").read_text())
    st.caption(
        f"Showing a saved snapshot of the pipeline output (HubSpot data as of "
        f"{info['built_on']}, {info['deal_count']} deals). The full pipeline loads Snowflake."
    )

# ── KPI row ─────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Deals", f"{len(fdf):,}")
k2.metric("Pipeline Value", f"${fdf['amount'].sum():,.0f}")
k3.metric("Avg Deal Size", f"${fdf['amount'].mean():,.0f}")
win_rate = fdf["is_won"].mean() * 100 if len(fdf) > 0 else 0
k4.metric("Win Rate", f"{win_rate:.1f}%")

st.divider()

# ── Row 1: Pipeline Stage Breakdown + Monthly Volume ───────────────────────────
c1, c2 = st.columns(2)

with c1:
    st.subheader("Pipeline Stage Breakdown")
    stage_agg = (
        fdf.groupby("stage_name", as_index=False)
        .agg(deal_count=("deal_id", "count"), total_value=("amount", "sum"))
        .sort_values("total_value", ascending=True)
    )
    fig1 = px.bar(
        stage_agg,
        x="total_value",
        y="stage_name",
        orientation="h",
        color="deal_count",
        color_continuous_scale="Blues",
        labels={
            "total_value": "Total Value ($)",
            "stage_name": "Stage",
            "deal_count": "Deal Count",
        },
    )
    fig1.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.subheader("Deal Creation Over Time")
    monthly = (
        fdf.assign(month=fdf["created_date"].dt.to_period("M").astype(str))
        .groupby("month", as_index=False)
        .agg(deals=("deal_id", "count"))
    )
    fig2 = px.line(
        monthly,
        x="month",
        y="deals",
        markers=True,
        labels={"month": "Month", "deals": "Deals Created"},
    )
    fig2.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Row 2: Deal Velocity + Outcome Breakdown ────────────────────────────────────
c3, c4 = st.columns(2)

with c3:
    st.subheader("Deal Velocity by Stage")
    closed = fdf[fdf["days_to_close"].notna() & (fdf["days_to_close"] > 0)]
    if len(closed) > 0:
        velocity = (
            closed.groupby("stage_name", as_index=False)
            .agg(avg_days=("days_to_close", "mean"))
            .sort_values("avg_days", ascending=False)
        )
        fig3 = px.bar(
            velocity,
            x="stage_name",
            y="avg_days",
            color="avg_days",
            color_continuous_scale="RdYlGn_r",
            labels={"avg_days": "Avg Days to Close", "stage_name": "Stage"},
        )
        fig3.update_layout(margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No closed deals in the selected filters.")

with c4:
    st.subheader("Deal Outcome Breakdown")
    outcome = pd.DataFrame(
        {
            "Outcome": ["Won", "Lost", "Open"],
            "Count": [
                int(fdf["is_won"].sum()),
                int(fdf["is_lost"].sum()),
                int((~fdf["is_won"] & ~fdf["is_lost"]).sum()),
            ],
        }
    )
    fig4 = px.pie(
        outcome,
        values="Count",
        names="Outcome",
        color="Outcome",
        color_discrete_map={
            "Won": "#2ecc71",
            "Lost": "#e74c3c",
            "Open": "#3498db",
        },
        hole=0.4,
    )
    fig4.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ── Row 3: Deal Size Distribution ──────────────────────────────────────────────
st.subheader("Deal Size Distribution")
nonzero = fdf[fdf["amount"] > 0]
if len(nonzero) > 0:
    fig5 = px.histogram(
        nonzero,
        x="amount",
        nbins=30,
        color_discrete_sequence=["#1f77b4"],
        labels={"amount": "Deal Amount ($)", "count": "Number of Deals"},
    )
    fig5.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig5, use_container_width=True)
else:
    st.info("No deals with non-zero amounts in the selected filters.")

# ── Raw data expander ───────────────────────────────────────────────────────────
with st.expander("View Raw Data"):
    st.dataframe(
        fdf[
            [
                "deal_name",
                "amount",
                "stage_name",
                "created_date",
                "close_date",
                "is_won",
                "days_to_close",
            ]
        ],
        use_container_width=True,
    )
