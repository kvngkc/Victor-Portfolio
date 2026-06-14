import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---------------------------------------------------------------------------
# Page configuration — MUST be the very first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Cyclistic Q1 2026 · Dashboard",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Premium CSS Injection
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Page background ── */
.stApp {
    background: #0D1117;
    color: #E6EDF3;
}

/* ── Main headings ── */
h1 {
    font-family: 'Outfit', sans-serif;
    font-size: 2.1rem !important;
    font-weight: 800 !important;
    color: #F0F6FC !important;
    letter-spacing: -0.5px;
}
h2 {
    font-family: 'Outfit', sans-serif;
    font-size: 1.35rem !important;
    font-weight: 700 !important;
    color: #58A6FF !important;
    border-left: 4px solid #1F6FEB;
    padding-left: 10px;
    margin-top: 2.5rem !important;
    margin-bottom: 0.5rem !important;
}
h3 {
    font-family: 'Outfit', sans-serif;
    color: #C9D1D9 !important;
    font-weight: 600 !important;
}

/* ── Subtitle text ── */
.dash-subtitle {
    color: #8B949E;
    font-size: 0.95rem;
    margin-top: -0.6rem;
    margin-bottom: 1.5rem;
}

/* ── KPI metric cards ── */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #161B22 0%, #1C2128 100%);
    border: 1px solid #30363D;
    border-radius: 14px;
    padding: 22px 20px !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}
div[data-testid="metric-container"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 28px rgba(31, 111, 235, 0.2);
    border-color: #1F6FEB;
}
div[data-testid="metric-container"] label {
    color: #8B949E !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #F0F6FC !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
}

/* ── Chart section cards ── */
.chart-card {
    background: #161B22;
    border: 1px solid #21262D;
    border-radius: 14px;
    padding: 6px 8px 6px 8px;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.35);
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D1117 0%, #0D1117 100%);
    border-right: 1px solid #21262D;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #F0F6FC !important;
}
section[data-testid="stSidebar"] label {
    color: #C9D1D9 !important;
    font-weight: 500 !important;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stSlider label {
    color: #8B949E !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}

/* ── Divider ── */
hr {
    border-color: #21262D !important;
    margin: 2rem 0 !important;
}

/* ── Filter pill badge ── */
.filter-badge {
    display: inline-block;
    background: #1F6FEB22;
    border: 1px solid #1F6FEB55;
    color: #58A6FF;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-right: 4px;
    margin-top: 4px;
}

/* ── Info / warning boxes ── */
.stAlert {
    background: #161B22 !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Constants & Colour Palette
# ---------------------------------------------------------------------------
DATA_PATH = "cyclistic_2026_q1_clean.csv"

DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Accessible, modern two-colour palette (member=blue, casual=coral)
PALETTE = {
    "member": "#1F6FEB",   # GitHub-blue
    "casual": "#F78166",   # Warm coral
}
PLOTLY_TEMPLATE = "plotly_dark"   # Dark base; we'll override paper/plot bg per chart

# Shared chart layout defaults applied to every figure
CHART_LAYOUT = dict(
    template=PLOTLY_TEMPLATE,
    paper_bgcolor="rgba(22,27,34,1)",
    plot_bgcolor="rgba(22,27,34,1)",
    font=dict(family="Inter, sans-serif", color="#C9D1D9"),
    title_font=dict(family="Outfit, sans-serif", size=16, color="#F0F6FC"),
    legend=dict(
        bgcolor="rgba(22,27,34,0.8)",
        bordercolor="#30363D",
        borderwidth=1,
        font=dict(size=12),
    ),
    margin=dict(l=50, r=30, t=55, b=50),
    hoverlabel=dict(
        bgcolor="#1C2128",
        bordercolor="#30363D",
        font=dict(family="Inter, sans-serif", size=13, color="#F0F6FC"),
    ),
)

GRIDCOLOR = "#21262D"

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="⏳  Loading Cyclistic Q1 2026 dataset…")
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["started_at"] = pd.to_datetime(df["started_at"])
    df["ended_at"]   = pd.to_datetime(df["ended_at"])
    df["hour"]       = df["started_at"].dt.hour
    # Ensure day_of_week is properly categorised for ordering
    if "day_of_week" in df.columns:
        df["day_of_week"] = pd.Categorical(df["day_of_week"], categories=DAY_ORDER, ordered=True)
    return df

df_raw = load_data(DATA_PATH)

# ---------------------------------------------------------------------------
# Sidebar — control panel
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("# 🚲 Control Panel")
    st.markdown('<p style="color:#8B949E;font-size:0.83rem;margin-top:-0.5rem;">All filters cascade to every chart in real-time</p>', unsafe_allow_html=True)
    st.divider()

    # ── 1. User Segment ──
    st.markdown("**USER SEGMENT**")
    all_user_types = sorted(df_raw["member_casual"].unique().tolist())
    selected_users = st.multiselect(
        "Select user types",
        options=all_user_types,
        default=all_user_types,
        help="Toggle member / casual riders",
    )

    st.divider()

    # ── 2. Bike Type ──
    st.markdown("**BIKE TYPE**")
    all_bike_types = sorted(df_raw["rideable_type"].unique().tolist())
    selected_bikes = st.multiselect(
        "Select bike types",
        options=all_bike_types,
        default=all_bike_types,
    )

    st.divider()

    # ── 3. Day of Week ──
    st.markdown("**DAY OF WEEK**")
    available_days = [d for d in DAY_ORDER if d in df_raw["day_of_week"].unique()]
    selected_days = st.multiselect(
        "Select days",
        options=available_days,
        default=available_days,
    )

    st.divider()

    # ── 4. Hour of Day ──
    st.markdown("**HOUR OF DAY**")
    hour_range = st.slider(
        "Start hour range (24h)",
        min_value=0,
        max_value=23,
        value=(0, 23),
        format="%d:00",
    )

    st.divider()

    # Active filters summary
    st.markdown("**ACTIVE FILTERS**")
    for u in (selected_users or ["none"]):
        st.markdown(f'<span class="filter-badge">👤 {u}</span>', unsafe_allow_html=True)
    st.markdown(f'<span class="filter-badge">🕐 {hour_range[0]}:00 – {hour_range[1]}:00</span>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Apply sidebar filters to the dataframe
# ---------------------------------------------------------------------------
df = df_raw.copy()

if selected_users:
    df = df[df["member_casual"].isin(selected_users)]

if selected_bikes:
    df = df[df["rideable_type"].isin(selected_bikes)]

if selected_days:
    df = df[df["day_of_week"].isin(selected_days)]

df = df[(df["hour"] >= hour_range[0]) & (df["hour"] <= hour_range[1])]

# ---------------------------------------------------------------------------
# Dashboard header
# ---------------------------------------------------------------------------
st.title("🚲 Cyclistic Q1 2026 Bike-Share Dashboard")
st.markdown('<p class="dash-subtitle">Interactive visual analytics — filter via the left panel to explore member vs. casual rider behaviour</p>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Guard: empty state
# ---------------------------------------------------------------------------
if df.empty:
    st.warning("⚠️  No records match your current filter criteria. Widen your selection in the sidebar.")
    st.stop()

# ---------------------------------------------------------------------------
# KPI Row
# ---------------------------------------------------------------------------
total_rides  = len(df)
avg_ride_len = df["ride_length"].mean()
member_cnt   = (df["member_casual"] == "member").sum()
casual_cnt   = (df["member_casual"] == "casual").sum()
member_pct   = member_cnt / total_rides * 100 if total_rides else 0
casual_pct   = casual_cnt / total_rides * 100 if total_rides else 0
peak_day     = df["day_of_week"].mode().iloc[0] if not df.empty else "N/A"
peak_hour_val = int(df["hour"].value_counts().idxmax()) if not df.empty else 0

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("🚴 Total Rides",        f"{total_rides:,}")
k2.metric("⏱ Avg Ride Length",    f"{avg_ride_len:.1f} min")
k3.metric("🔵 Member Share",       f"{member_pct:.1f}%")
k4.metric("🟠 Casual Share",       f"{casual_pct:.1f}%")
k5.metric("📅 Peak Day",           str(peak_day))

st.divider()

# ============================================================================
# HELPER — apply common layout to every figure
# ============================================================================
def apply_layout(fig, title: str, xaxis_title: str = "", yaxis_title: str = "",
                 xgrid: bool = True, ygrid: bool = True):
    fig.update_layout(
        **CHART_LAYOUT,
        title_text=title,
        xaxis=dict(
            title=xaxis_title,
            gridcolor=GRIDCOLOR if xgrid else "rgba(0,0,0,0)",
            gridwidth=1,
            zeroline=False,
            linecolor="#30363D",
        ),
        yaxis=dict(
            title=yaxis_title,
            gridcolor=GRIDCOLOR if ygrid else "rgba(0,0,0,0)",
            gridwidth=1,
            zeroline=False,
            linecolor="#30363D",
        ),
    )
    return fig

# ============================================================================
# Section 1 — Ride Length & Weekday Profiles
# ============================================================================
st.header("1 · Ride Lengths & Weekday Profiles")

# ── Chart 1a: Avg & Median Ride Length (grouped bar) ──────────────────────
st.markdown('<div class="chart-card">', unsafe_allow_html=True)
summary = (
    df.groupby("member_casual")["ride_length"]
    .agg(Mean="mean", Median="median")
    .reset_index()
)
summary_melted = summary.melt(id_vars="member_casual", value_vars=["Mean", "Median"],
                               var_name="Metric", value_name="Minutes")
summary_melted["member_casual"] = summary_melted["member_casual"].str.capitalize()

fig1 = px.bar(
    summary_melted,
    x="member_casual",
    y="Minutes",
    color="Metric",
    barmode="group",
    text_auto=".1f",
    color_discrete_sequence=["#1F6FEB", "#F78166"],
    labels={"member_casual": "User Type", "Minutes": "Ride Length (min)", "Metric": "Statistic"},
)
fig1.update_traces(textposition="outside", textfont=dict(size=12))
apply_layout(fig1,
             title="Average & Median Ride Length — Members vs. Casual Riders",
             xaxis_title="User Type",
             yaxis_title="Ride Length (minutes)")
st.plotly_chart(fig1, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Chart 1b: Avg Ride Length by Day of Week (line chart) ─────────────────
st.markdown('<div class="chart-card">', unsafe_allow_html=True)
active_days = [d for d in DAY_ORDER if d in df["day_of_week"].unique()]
pivot_day = (
    df.groupby(["member_casual", "day_of_week"], observed=True)["ride_length"]
    .mean()
    .reset_index()
    .rename(columns={"ride_length": "avg_ride_length", "member_casual": "User Type"})
)
pivot_day["day_of_week"] = pd.Categorical(pivot_day["day_of_week"], categories=DAY_ORDER, ordered=True)
pivot_day = pivot_day.sort_values("day_of_week")
pivot_day["User Type"] = pivot_day["User Type"].str.capitalize()

fig2 = px.line(
    pivot_day,
    x="day_of_week",
    y="avg_ride_length",
    color="User Type",
    markers=True,
    color_discrete_map={"Member": "#1F6FEB", "Casual": "#F78166"},
    labels={"day_of_week": "Day of Week", "avg_ride_length": "Avg Ride Length (min)", "User Type": "User Type"},
    hover_data={"avg_ride_length": ":.1f"},
)
fig2.update_traces(line=dict(width=3), marker=dict(size=9))
apply_layout(fig2,
             title="Average Ride Length by Day of Week",
             xaxis_title="Day of Week",
             yaxis_title="Avg Ride Length (minutes)")
st.plotly_chart(fig2, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ============================================================================
# Section 2 — Ride Distribution: Weekly & Hourly
# ============================================================================
st.header("2 · Ride Distribution — Weekly & Hourly Profiles")

# ── Chart 2a: Total Rides by Day of Week (grouped bar) ────────────────────
st.markdown('<div class="chart-card">', unsafe_allow_html=True)
ride_counts_day = (
    df.groupby(["member_casual", "day_of_week"], observed=True)
    .size()
    .reset_index(name="Ride Count")
)
ride_counts_day["day_of_week"] = pd.Categorical(ride_counts_day["day_of_week"], categories=DAY_ORDER, ordered=True)
ride_counts_day = ride_counts_day.sort_values("day_of_week")
ride_counts_day["member_casual"] = ride_counts_day["member_casual"].str.capitalize()

fig3 = px.bar(
    ride_counts_day,
    x="day_of_week",
    y="Ride Count",
    color="member_casual",
    barmode="group",
    color_discrete_map={"Member": "#1F6FEB", "Casual": "#F78166"},
    labels={"day_of_week": "Day of Week", "Ride Count": "Number of Rides", "member_casual": "User Type"},
    text_auto=",d",
)
fig3.update_traces(textposition="outside", textfont=dict(size=10))
apply_layout(fig3,
             title="Total Rides by Day of Week",
             xaxis_title="Day of Week",
             yaxis_title="Number of Rides")
st.plotly_chart(fig3, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Chart 2b: Hourly Ride Distribution (area chart) ───────────────────────
st.markdown('<div class="chart-card">', unsafe_allow_html=True)
hourly = (
    df.groupby(["member_casual", "hour"])
    .size()
    .reset_index(name="Ride Count")
)
hourly["member_casual"] = hourly["member_casual"].str.capitalize()

fig4 = px.area(
    hourly,
    x="hour",
    y="Ride Count",
    color="member_casual",
    color_discrete_map={"Member": "#1F6FEB", "Casual": "#F78166"},
    labels={"hour": "Hour of Day (24h)", "Ride Count": "Number of Rides", "member_casual": "User Type"},
    markers=True,
    hover_data={"Ride Count": ":,"},
)
fig4.update_traces(opacity=0.75, line=dict(width=2.5), marker=dict(size=6))
fig4.update_xaxes(tickmode="linear", tick0=0, dtick=1)
apply_layout(fig4,
             title="Hourly Ride Distribution — Members vs. Casual Riders",
             xaxis_title="Hour of Day (24-hour clock)",
             yaxis_title="Number of Rides")
st.plotly_chart(fig4, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ============================================================================
# Section 3 — Bike Preferences & Station Behaviour
# ============================================================================
st.header("3 · Ride Preferences & Station Behaviour")

# ── Chart 3a: Bike Type Preferences (100 % stacked bar) ───────────────────
st.markdown('<div class="chart-card">', unsafe_allow_html=True)
bike_prefs_raw = (
    df.groupby(["member_casual", "rideable_type"])
    .size()
    .reset_index(name="count")
)
bike_totals = bike_prefs_raw.groupby("member_casual")["count"].transform("sum")
bike_prefs_raw["pct"] = bike_prefs_raw["count"] / bike_totals * 100
bike_prefs_raw["member_casual"] = bike_prefs_raw["member_casual"].str.capitalize()
bike_prefs_raw["rideable_type"] = bike_prefs_raw["rideable_type"].str.replace("_", " ").str.title()

fig5 = px.bar(
    bike_prefs_raw,
    x="member_casual",
    y="pct",
    color="rideable_type",
    text_auto=".1f",
    color_discrete_sequence=["#1F6FEB", "#3FB950", "#F78166"],
    labels={"member_casual": "User Type", "pct": "Share of Rides (%)", "rideable_type": "Bike Type"},
)
fig5.update_traces(texttemplate="%{y:.1f}%", textposition="inside",
                   insidetextanchor="middle")
apply_layout(fig5,
             title="Bike Type Preferences — Share of Rides by User Type",
             xaxis_title="User Type",
             yaxis_title="Share of Rides (%)")
st.plotly_chart(fig5, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Chart 3b: Round-trip Percentage ───────────────────────────────────────
st.markdown('<div class="chart-card">', unsafe_allow_html=True)
df_nd = df[
    (df["start_station_name"] != "On-Street (Dockless)") &
    (df["end_station_name"]   != "On-Street (Dockless)")
].copy()

if not df_nd.empty:
    df_nd["is_round_trip"] = df_nd["start_station_name"] == df_nd["end_station_name"]
    rt_pct = (
        df_nd.groupby("member_casual")["is_round_trip"]
        .mean()
        .mul(100)
        .reset_index(name="Round Trip %")
    )
    rt_pct["member_casual"] = rt_pct["member_casual"].str.capitalize()

    fig6 = px.bar(
        rt_pct,
        x="member_casual",
        y="Round Trip %",
        color="member_casual",
        text_auto=".2f",
        color_discrete_map={"Member": "#1F6FEB", "Casual": "#F78166"},
        labels={"member_casual": "User Type", "Round Trip %": "Round Trip Rate (%)"},
    )
    fig6.update_traces(texttemplate="%{y:.2f}%", textposition="outside",
                       textfont=dict(size=13), showlegend=False)
    apply_layout(fig6,
                 title="Round Trip Rate by User Type (Excluding Dockless Rides)",
                 xaxis_title="User Type",
                 yaxis_title="Round Trip Rate (%)")
    st.plotly_chart(fig6, use_container_width=True)
else:
    st.info("ℹ️  Filter selection does not contain any named-station rides.")
st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ============================================================================
# Section 4 — Distance, Speed & Top Routes
# ============================================================================
st.header("4 · Distance, Speed & Route Profiles")

# ── Chart 4a: Mean Distance & Speed (side-by-side bars in one row) ─────────
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return R * 2 * np.arcsin(np.sqrt(a))

df_coords = df.dropna(subset=["start_lat", "start_lng", "end_lat", "end_lng"]).copy()

if not df_coords.empty:
    df_coords["distance_km"] = haversine(
        df_coords["start_lat"], df_coords["start_lng"],
        df_coords["end_lat"],   df_coords["end_lng"]
    )
    df_coords["speed_kmh"] = df_coords["distance_km"] / (df_coords["ride_length"] / 60)

    dist_stats  = df_coords.groupby("member_casual")["distance_km"].mean().reset_index(name="value")
    speed_stats = df_coords.groupby("member_casual")["speed_kmh"].mean().reset_index(name="value")

    dist_stats["metric"]  = "Distance (km)"
    speed_stats["metric"] = "Speed (km/h)"

    combined = pd.concat([dist_stats, speed_stats], ignore_index=True)
    combined["member_casual"] = combined["member_casual"].str.capitalize()

    # ── Chart 4a-i: Distance ──
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    fig7a = px.bar(
        combined[combined["metric"] == "Distance (km)"],
        x="member_casual",
        y="value",
        color="member_casual",
        text_auto=".2f",
        color_discrete_map={"Member": "#1F6FEB", "Casual": "#F78166"},
        labels={"member_casual": "User Type", "value": "Avg Distance (km)"},
    )
    fig7a.update_traces(texttemplate="%{y:.2f} km", textposition="outside",
                        showlegend=False, textfont=dict(size=13))
    apply_layout(fig7a,
                 title="Mean Straight-Line Distance by User Type",
                 xaxis_title="User Type",
                 yaxis_title="Average Distance (km)")
    st.plotly_chart(fig7a, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Chart 4a-ii: Speed ──
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    fig7b = px.bar(
        combined[combined["metric"] == "Speed (km/h)"],
        x="member_casual",
        y="value",
        color="member_casual",
        text_auto=".2f",
        color_discrete_map={"Member": "#1F6FEB", "Casual": "#F78166"},
        labels={"member_casual": "User Type", "value": "Avg Speed (km/h)"},
    )
    fig7b.update_traces(texttemplate="%{y:.2f} km/h", textposition="outside",
                        showlegend=False, textfont=dict(size=13))
    apply_layout(fig7b,
                 title="Mean Estimated Riding Speed by User Type",
                 xaxis_title="User Type",
                 yaxis_title="Average Speed (km/h)")
    st.plotly_chart(fig7b, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("ℹ️  No GPS coordinates available for the current filter selection.")

# ── Chart 4b: Top Routes (horizontal bar, one per user type) ───────────────
df_vs = df[
    (df["start_station_name"] != "On-Street (Dockless)") &
    (df["end_station_name"]   != "On-Street (Dockless)")
].copy()

if not df_vs.empty:
    df_vs["route"] = df_vs["start_station_name"] + " → " + df_vs["end_station_name"]

    for utype, colour in [("member", "#1F6FEB"), ("casual", "#F78166")]:
        if utype not in df_vs["member_casual"].values:
            continue
        top = (
            df_vs[df_vs["member_casual"] == utype]["route"]
            .value_counts()
            .head(10)
            .reset_index()
        )
        top.columns = ["Route", "Rides"]
        top = top.sort_values("Rides")  # ascending so longest bar is at top

        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        fig_r = px.bar(
            top,
            x="Rides",
            y="Route",
            orientation="h",
            text="Rides",
            color_discrete_sequence=[colour],
            labels={"Rides": "Number of Rides", "Route": ""},
        )
        fig_r.update_traces(textposition="outside", textfont=dict(size=12),
                            marker_color=colour)
        apply_layout(fig_r,
                     title=f"Top 10 Routes — {utype.capitalize()} Riders",
                     xaxis_title="Number of Rides",
                     yaxis_title="")
        fig_r.update_layout(
            height=420,
            yaxis=dict(autorange=True, gridcolor=GRIDCOLOR),
        )
        st.plotly_chart(fig_r, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("ℹ️  No named-station route data in the current filter selection.")

st.divider()

# ============================================================================
# Section 5 — Geographic Map
# ============================================================================
st.header("5 · Geospatial Start Location Distribution")
st.markdown('<p class="dash-subtitle">Ride start points plotted on an interactive map. Filter the sidebar to slice by user type, bike type, or time window.</p>', unsafe_allow_html=True)

df_map = df.dropna(subset=["start_lat", "start_lng"]).copy()

if df_map.empty:
    st.warning("⚠️  No GPS coordinates available for the current filter.")
else:
    MAP_LIMIT = 8_000
    if len(df_map) > MAP_LIMIT:
        df_map = df_map.sample(n=MAP_LIMIT, random_state=42)
        st.caption(f"Showing a random sample of {MAP_LIMIT:,} rides for browser performance.")
    else:
        st.caption(f"Showing all {len(df_map):,} coordinate points.")

    df_map["member_casual_label"] = df_map["member_casual"].str.capitalize()

    fig_map = px.scatter_mapbox(
        df_map,
        lat="start_lat",
        lon="start_lng",
        color="member_casual_label",
        color_discrete_map={"Member": "#1F6FEB", "Casual": "#F78166"},
        opacity=0.55,
        zoom=11,
        mapbox_style="carto-darkmatter",
        hover_data={"start_lat": False, "start_lng": False,
                    "rideable_type": True, "hour": True,
                    "member_casual_label": False},
        labels={"member_casual_label": "User Type"},
        size_max=6,
    )
    map_layout = {
        **CHART_LAYOUT,
        "margin": dict(l=0, r=0, t=40, b=0),
        "height": 520,
        "title_text": "Ride Start Locations — Q1 2026",
        "legend": dict(
            bgcolor="rgba(22,27,34,0.9)",
            bordercolor="#30363D",
            borderwidth=1,
        ),
    }
    fig_map.update_layout(**map_layout)
    st.plotly_chart(fig_map, use_container_width=True)

    st.subheader("Top 10 Start Stations by Ride Volume")
    top_st = (
        df["start_station_name"]
        .value_counts()
        .head(10)
        .reset_index()
    )
    top_st.columns = ["Station Name", "Rides Started"]
    st.dataframe(
        top_st.style.background_gradient(subset=["Rides Started"], cmap="Blues"),
        use_container_width=True,
        hide_index=True,
    )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.markdown(
    '<p style="text-align:center;color:#444D56;font-size:0.78rem;">'
    'Cyclistic Q1 2026 · Built with Streamlit & Plotly · Data filtered in real-time'
    '</p>',
    unsafe_allow_html=True,
)
