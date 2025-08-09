# app.py
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt

st.set_page_config(page_title="Tourism Dashboard — Charts Only", layout="wide")


@st.cache_data
def load_data(csv_path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found at {csv_path}. Please provide a valid path.")
            
    df["date"] = pd.to_datetime(dict(year=df["year"], month=df["month"], day=1))
    # Helpful string month label for monthly groupings
    df["month_name"] = df["date"].dt.strftime("%b")
    df["year_month"] = df["date"].dt.to_period("M").astype(str)
    return df

csv_path = "https://raw.githubusercontent.com/<your-username>/<your-repo-name>/master/Data/tourism_with_temps.csv"
df = load_data(csv_path)


st.sidebar.header("Filters")
years = sorted(df["year"].dropna().unique().tolist())
year_min, year_max = int(min(years)), int(max(years))
year_range = st.sidebar.slider("Year range", year_min, year_max, (year_min, year_max))


if "visitPurposeEn" in df:
    purposes = sorted(df["visitPurposeEn"].dropna().unique().tolist())
else:
    purposes = []
purpose_selected = st.sidebar.multiselect("Visit purpose", purposes, default=purposes)

mask = df["year"].between(year_range[0], year_range[1])
if purpose_selected:
    mask &= df["visitPurposeEn"].isin(purpose_selected)
fdf = df.loc[mask].copy()


# Create 6 KPI columns
col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)


# Make sure key columns are numeric (avoids errors from CSV strings)
for c in ["trips", "spendSAR", "nights", "destination_temp"]:
    fdf[c] = pd.to_numeric(fdf[c], errors="coerce")

# ====== KPI CALCULATIONS ======
trips_sum = fdf["trips"].sum()
nights_sum = fdf["nights"].sum()

# 1) Total Trips
total_trips_fmt = f"{int(trips_sum):,}" if trips_sum else "0"

# 2) Total Spend (SAR)
spend_sum = fdf["spendSAR"].sum()
total_spend_fmt = f"{int(spend_sum):,}" if spend_sum else "0"

# 3) Avg. Nights per Trip
avg_nights_per_trip = nights_sum / trips_sum if trips_sum else 0
avg_nights_fmt = f"{avg_nights_per_trip:.2f}"

# 4) Most Popular Destination
most_popular = (
    fdf["destinationProvinceNameEn"].mode()[0]
    if not fdf.empty and fdf["destinationProvinceNameEn"].notna().any()
    else "No data"
)

# 5) Hottest Destination
temps = fdf["destination_temp"]
if not fdf.empty and temps.notna().any():
    hottest_row = fdf.loc[temps.idxmax()]
    hottest_dest = f"{hottest_row['destinationProvinceNameEn']} ({hottest_row['destination_temp']}°C)"
else:
    hottest_dest = "No data"

# 6) Coolest Destination
if not fdf.empty and temps.notna().any():
    coolest_row = fdf.loc[temps.idxmin()]
    coolest_dest = f"{coolest_row['destinationProvinceNameEn']} ({coolest_row['destination_temp']}°C)"
else:
    coolest_dest = "No data"

# ====== KPI DISPLAY ======
with col1:
    st.metric("Total Trips", total_trips_fmt)
with col2:
    st.metric("Total Spend (SAR)", total_spend_fmt)
with col3:
    st.metric("Avg. Nights/Trip", avg_nights_fmt)
with col4:
    st.metric("Most Popular Destination", most_popular)
with col5:
    st.metric("Hottest Destination", hottest_dest)
with col6:
    st.metric("Coolest Destination", coolest_dest)



st.title("Tourism Dashboard")


st.subheader("1) Trips & Spending Over Time (dual-axis)")
st.caption("Shows monthly totals; dual y-axes let you compare different scales directly.")

ts = (
    fdf.groupby("date", as_index=False)
       .agg(trips=("trips","sum"), spendSAR=("spendSAR","sum"))
)

if not ts.empty:
    base = alt.Chart(ts).properties(height=360)

    trips_line = base.mark_line(point=True).encode(
        x=alt.X("date:T", title="Month"),
        y=alt.Y("trips:Q", title="Trips"),
        tooltip=[alt.Tooltip("date:T", title="Month"), "trips:Q", alt.Tooltip("spendSAR:Q", format=",")]
    )

    spend_line = base.mark_line(point=True).encode(
        x="date:T",
        y=alt.Y("spendSAR:Q", title="Spend (SAR)", axis=alt.Axis(orient="right")),
        tooltip=[alt.Tooltip("date:T", title="Month"), alt.Tooltip("spendSAR:Q", format=","), "trips:Q"]
    )

    dual_axis = alt.layer(trips_line, spend_line).resolve_scale(y="independent")
    st.altair_chart(dual_axis, use_container_width=True)
else:
    st.info("No data for selected filters.")

st.divider()



st.subheader("2) Top Destination Provinces by Total Trips")
rank_n = st.slider("Show top N destinations", 3, 13, 10)

if {"destinationProvinceNameEn","trips"}.issubset(fdf.columns) and not fdf.empty:
    top_dest = (
        fdf.groupby("destinationProvinceNameEn", as_index=False)["trips"].sum()
           .sort_values("trips", ascending=False)
           .head(rank_n)
    )
    bar = (
        alt.Chart(top_dest)
        .mark_bar()
        .encode(
            x=alt.X("trips:Q", title="Total Trips"),
            y=alt.Y("destinationProvinceNameEn:N", sort="-x", title="Destination"),
            tooltip=["destinationProvinceNameEn:N", "trips:Q"]
        )
        .properties(height=max(280, 20 * len(top_dest)))
    )
    st.altair_chart(bar, use_container_width=True)
else:
    st.info("Need columns: destinationProvinceNameEn, trips.")

st.divider()


st.subheader("3) Spending vs. Nights (bubble size = trips, color = purpose)")
if {"spendSAR","nights","trips"}.issubset(fdf.columns) and not fdf.empty:
    scatter = (
        alt.Chart(fdf)
        .mark_circle(opacity=0.7)
        .encode(
            x=alt.X("nights:Q", title="Nights"),
            y=alt.Y("spendSAR:Q", title="Spend (SAR)"),
            size=alt.Size("trips:Q", title="Trips", legend=None),
            color=alt.Color("visitPurposeEn:N", title="Purpose") if "visitPurposeEn" in fdf else alt.value("steelblue"),
            tooltip=[
                alt.Tooltip("destinationProvinceNameEn:N", title="Destination"),
                alt.Tooltip("originProvinceNameEn:N", title="Origin"),
                alt.Tooltip("visitPurposeEn:N", title="Purpose"),
                alt.Tooltip("year:O"),
                alt.Tooltip("month:O"),
                alt.Tooltip("nights:Q"),
                alt.Tooltip("trips:Q"),
                alt.Tooltip("spendSAR:Q", format=","),
            ],
        )
        .properties(height=420)
    )
    st.altair_chart(scatter, use_container_width=True)
else:
    st.info("Need columns: spendSAR, nights, trips (and preferably visitPurposeEn).")

st.divider()


st.subheader("4) Trip Flow Matrix (Origin → Destination)")
st.caption("Intensity = number of trips between origin and destination.")

if {"originProvinceNameEn","destinationProvinceNameEn","trips"}.issubset(fdf.columns) and not fdf.empty:
    flow = (
        fdf.groupby(["originProvinceNameEn","destinationProvinceNameEn"], as_index=False)
           .agg(trips=("trips","sum"))
    )

    heat = (
        alt.Chart(flow)
        .mark_rect()
        .encode(
            x=alt.X("originProvinceNameEn:N", title="Origin", sort=alt.SortField("originProvinceNameEn")),
            y=alt.Y("destinationProvinceNameEn:N", title="Destination", sort=alt.SortField("destinationProvinceNameEn")),
            color=alt.Color("trips:Q", title="Trips"),
            tooltip=[
                alt.Tooltip("originProvinceNameEn:N", title="Origin"),
                alt.Tooltip("destinationProvinceNameEn:N", title="Destination"),
                alt.Tooltip("trips:Q", title="Trips")
            ],
        )
        .properties(height=420)
    )
    st.altair_chart(heat, use_container_width=True)
else:
    st.info("Need columns: originProvinceNameEn, destinationProvinceNameEn, trips.")

st.divider()


st.subheader("5) Trips vs. Avg Destination Temperature by Month (dual-axis)")
st.caption("Bars = total trips per month; Line = average destination_temp per month.")

if {"trips","destination_temp","date"}.issubset(fdf.columns) and not fdf.empty:
    monthly = (
        fdf.groupby("date", as_index=False)
           .agg(trips=("trips","sum"), avg_dest_temp=("destination_temp","mean"))
    )

    base = alt.Chart(monthly).properties(height=360)

    trips_bars = base.mark_bar().encode(
        x=alt.X("date:T", title="Month"),
        y=alt.Y("trips:Q", title="Trips"),
        tooltip=[alt.Tooltip("date:T", title="Month"), "trips:Q", alt.Tooltip("avg_dest_temp:Q", title="Avg Temp (°C)", format=".1f")]
    )

    temp_line = base.mark_line(point=True).encode(
        x="date:T",
        y=alt.Y("avg_dest_temp:Q", title="Avg Destination Temp (°C)", axis=alt.Axis(orient="right")),
        tooltip=[alt.Tooltip("date:T", title="Month"), alt.Tooltip("avg_dest_temp:Q", title="Avg Temp (°C)", format=".1f")]
    )

    dual = alt.layer(trips_bars, temp_line).resolve_scale(y="independent")
    st.altair_chart(dual, use_container_width=True)
else:
    st.info("Need columns: trips, destination_temp, date.")

