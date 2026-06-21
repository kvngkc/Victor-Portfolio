import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as gr

# ==========================================
# 1. PAGE CONFIGURATION & THEME STYLING
# ==========================================
st.set_page_config(
    page_title="Bellabeat Smart Device Insights",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Bellabeat Earthy Dark Theme
# Background: Deep warm charcoal (#1E1A17), Card: (#2B2420), Accent: Peach (#E29578), Text: Ivory (#F4ECE8)
st.markdown("""
<style>
    /* Main body background and font */
    .stApp {
        background-color: #1E1A17;
        color: #F4ECE8;
        font-family: 'Outfit', 'Inter', sans-serif;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #27211E !important;
        border-right: 1px solid #3A322D;
    }
    
    section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] label {
        color: #E5D3C8 !important;
    }
    
    /* KPI Metric Card containers */
    div[data-testid="stMetricValue"] {
        color: #E29578 !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #E5D3C8 !important;
        font-size: 0.95rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Card box wrapper */
    .kpi-card {
        background-color: #2B2420;
        border: 1px solid #3A322D;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }
    
    /* Marketing product recommendations cards */
    .product-card {
        background-color: #2B2420;
        border-left: 5px solid #E29578;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
    }
    
    .product-title {
        color: #E29578;
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .product-subtitle {
        color: #DF9E8A;
        font-size: 0.9rem;
        font-style: italic;
        margin-bottom: 12px;
    }
    
    /* Tabs active/inactive styles */
    button[data-baseweb="tab"] {
        color: #E5D3C8 !important;
        font-size: 1.05rem !important;
        font-weight: 500 !important;
        background-color: transparent !important;
        border: none !important;
        padding: 12px 20px !important;
    }
    
    button[aria-selected="true"] {
        color: #E29578 !important;
        border-bottom: 3px solid #E29578 !important;
        font-weight: 600 !important;
    }
    
    /* Divider custom styling */
    hr {
        border-color: #3A322D !important;
    }
</style>
""", unsafe_allow_html=True)

# Color Constants for Plotly
BB_DARK = "#1E1A17"
BB_CARD = "#2B2420"
BB_PEACH = "#E29578"
BB_ROSE = "#DF9E8A"
BB_GOLD = "#F1D3B3"
BB_IVORY = "#F4ECE8"
BB_SAND = "#E5D3C8"
BB_MUTED = "#6B5B52"
BB_COLORS = [BB_PEACH, BB_ROSE, BB_GOLD, BB_SAND, BB_MUTED]

# ==========================================
# 2. DATA INGESTION & FILTERING (LAZY LOADING)
# ==========================================
@st.cache_data
def load_data():
    daily = pd.read_csv('processed_data/daily_engineered.csv')
    hourly = pd.read_csv('processed_data/hourly_engineered.csv')

    # Fix dates
    daily['date'] = pd.to_datetime(daily['date'])
    hourly['activity_hour'] = pd.to_datetime(hourly['activity_hour'])

    # Derive time-based columns the Streamlit app needs (not persisted in CSV)
    hourly['hour'] = hourly['activity_hour'].dt.hour
    hourly['day_of_week'] = hourly['activity_hour'].dt.day_name()
    return daily, hourly

try:
    df_daily, df_hourly = load_data()
except Exception as e:
    st.error(f"Error loading engineered datasets: {e}. Please ensure data_processing.py and run_notebook.py have run successfully.")
    st.stop()

# ==========================================
# 3. SIDEBAR FILTERS (TIME & ACTIVITY BASED)
# ==========================================
st.sidebar.markdown("<div style='text-align:center; font-size:2.5rem; margin-bottom:4px;'>🌸</div>", unsafe_allow_html=True)
st.sidebar.markdown("<h2 style='text-align: center; color: #E29578;'>BELLABEAT</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; font-style: italic; color: #E5D3C8;'>Smart Device Marketing Portal</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Filter 1: Date Range
min_date = df_daily['date'].min().to_pydatetime()
max_date = df_daily['date'].max().to_pydatetime()
start_date, end_date = st.sidebar.slider(
    "Select Analysis Period",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD"
)

# Filter 2: Day of Week
all_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
selected_days = st.sidebar.multiselect(
    "Filter by Days of Week",
    options=all_days,
    default=all_days
)

# Filter 3: Activity Level Tiers
activity_tiers = list(df_daily['activity_tier'].unique())
selected_activity = st.sidebar.multiselect(
    "Filter by Activity Tiers",
    options=activity_tiers,
    default=activity_tiers
)

# Filter 4: Wear Consistency
wear_tiers = list(df_daily['wear_tier'].dropna().unique())
selected_wear = st.sidebar.multiselect(
    "Filter by Wear Consistency",
    options=wear_tiers,
    default=wear_tiers
)

# Apply filters
filtered_daily = df_daily[
    (df_daily['date'] >= pd.Timestamp(start_date)) &
    (df_daily['date'] <= pd.Timestamp(end_date)) &
    (df_daily['day_name'].isin(selected_days)) &
    (df_daily['activity_tier'].isin(selected_activity)) &
    (df_daily['wear_tier'].isin(selected_wear))
]

# Map hourly dates to daily filter boundaries
filtered_hourly = df_hourly[
    (df_hourly['activity_hour'] >= pd.Timestamp(start_date)) &
    (df_hourly['activity_hour'] <= pd.Timestamp(end_date)) &
    (df_hourly['day_of_week'].isin(selected_days)) &
    (df_hourly['id'].isin(filtered_daily['id'].unique()))
]

# ==========================================
# 4. DASHBOARD HEADER
# ==========================================
st.markdown("<h1 style='color: #F4ECE8; margin-bottom: 5px;'>Smart Device Usage & Engagement Analysis</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #DF9E8A; font-size: 1.1rem; margin-bottom: 25px;'>Unlocking consumer trends to position Bellabeat's marketing for premium wellness acquisition.</p>", unsafe_allow_html=True)

# Tabs Navigation
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 User Engagement & Profile", 
    "💤 Sleep & Health Correlation", 
    "⏰ Hourly & Daily Rhythms", 
    "💡 Act: Marketing Recommendations"
])

# ==========================================
# TAB 1: USER ENGAGEMENT & PROFILE
# ==========================================
with tab1:
    st.markdown("### Executive Performance Summary")
    
    # KPI metrics row
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    
    total_users = filtered_daily['id'].nunique()
    avg_steps = int(filtered_daily['total_steps'].mean()) if len(filtered_daily) > 0 else 0
    avg_sleep = round(filtered_daily['total_minutes_asleep'].mean() / 60, 1) if filtered_daily['total_minutes_asleep'].count() > 0 else 0.0
    avg_sedentary = round(filtered_daily['sedentary_minutes'].mean() / 60, 1) if len(filtered_daily) > 0 else 0.0
    total_records = len(filtered_daily)
    
    with kpi1:
        st.markdown(f"<div class='kpi-card'><h6>Unique Wearers</h6><h2>{total_users}</h2><span style='color:#DF9E8A'>FitBit Sample</span></div>", unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"<div class='kpi-card'><h6>Average Steps</h6><h2>{avg_steps:,}</h2><span style='color:#DF9E8A'>Steps / Day</span></div>", unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"<div class='kpi-card'><h6>Average Sleep</h6><h2>{avg_sleep}h</h2><span style='color:#DF9E8A'>Hours / Night</span></div>", unsafe_allow_html=True)
    with kpi4:
        st.markdown(f"<div class='kpi-card'><h6>Sedentary Hours</h6><h2>{avg_sedentary}h</h2><span style='color:#DF9E8A'>Inactive / Day</span></div>", unsafe_allow_html=True)
    with kpi5:
        st.markdown(f"<div class='kpi-card'><h6>Total Log Days</h6><h2>{total_records}</h2><span style='color:#DF9E8A'>Aggregated Days</span></div>", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts: Profiles & Consistency
    col1, col2 = st.columns(2)
    
    with col1:
        # Donut Chart for User Wear Consistency
        wear_data = filtered_daily.groupby('id')['wear_tier'].first().value_counts().reset_index()
        wear_data.columns = ['tier', 'count']
        
        fig_wear = px.pie(
            wear_data, 
            values='count', 
            names='tier',
            hole=0.5,
            color_discrete_sequence=[BB_PEACH, BB_ROSE, BB_GOLD],
            title="<b>Wear Consistency Profile</b><br><sup>Most users are moderate trackers (logging 50-80% of days)</sup>"
        )
        fig_wear.update_layout(
            paper_bgcolor=BB_DARK,
            plot_bgcolor=BB_DARK,
            font=dict(color=BB_IVORY),
            legend=dict(orientation="h", y=-0.1, x=0),
            margin=dict(t=80, b=50, l=20, r=20)
        )
        st.plotly_chart(fig_wear, use_container_width=True)
        
    with col2:
        # Activity Tiers Bar Chart
        act_data = filtered_daily['activity_tier'].value_counts().reset_index()
        act_data.columns = ['tier', 'count']
        
        # Sort by natural hierarchy
        tier_order = ['Sedentary (<5k steps)', 'Lightly Active (5k-7.5k steps)', 'Fairly Active (7.5k-10k steps)', 'Active / Highly Active (>=10k steps)']
        act_data['tier'] = pd.Categorical(act_data['tier'], categories=tier_order, ordered=True)
        act_data = act_data.sort_values('tier')
        
        fig_act = px.bar(
            act_data,
            x='count',
            y='tier',
            orientation='h',
            color='tier',
            color_discrete_sequence=[BB_MUTED, BB_SAND, BB_GOLD, BB_PEACH],
            title="<b>Daily Activity Tiers Distribution</b><br><sup>Over 36% of tracking days fall under sedentary steps guidelines</sup>"
        )
        fig_act.update_layout(
            paper_bgcolor=BB_DARK,
            plot_bgcolor=BB_DARK,
            font=dict(color=BB_IVORY),
            showlegend=False,
            xaxis=dict(showgrid=False, title="Number of Days"),
            yaxis=dict(title=""),
            margin=dict(t=80, b=50, l=20, r=20)
        )
        st.plotly_chart(fig_act, use_container_width=True)

# ==========================================
# TAB 2: SLEEP & HEALTH CORRELATION
# ==========================================
with tab2:
    st.markdown("### The Sleep-Activity Connection")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Sleep Sufficiency Pie
        sleep_data = filtered_daily['sleep_tier'].dropna().value_counts().reset_index()
        sleep_data.columns = ['tier', 'count']
        
        fig_sleep_pie = px.pie(
            sleep_data,
            values='count',
            names='tier',
            hole=0.5,
            color_discrete_sequence=[BB_PEACH, BB_ROSE, BB_GOLD],
            title="<b>Sleep Sufficiency Breakdown</b><br><sup>Most users fail to meet standard 7-9 hours sleep guidelines</sup>"
        )
        fig_sleep_pie.update_layout(
            paper_bgcolor=BB_DARK,
            plot_bgcolor=BB_DARK,
            font=dict(color=BB_IVORY),
            legend=dict(orientation="h", y=-0.1, x=0),
            margin=dict(t=80, b=50, l=20, r=20)
        )
        st.plotly_chart(fig_sleep_pie, use_container_width=True)
        
    with col2:
        # Sedentary Minutes vs sleep duration scatter plot (McCandless style: narrative driven)
        df_sleep_clean = filtered_daily.dropna(subset=['total_minutes_asleep', 'sedentary_minutes'])
        
        fig_scatter = px.scatter(
            df_sleep_clean,
            x='sedentary_minutes',
            y='total_minutes_asleep',
            color='very_active_minutes',
            color_continuous_scale=[[0, BB_SAND], [0.5, BB_PEACH], [1.0, BB_ROSE]],
            labels={'sedentary_minutes': 'Sedentary Minutes/Day', 'total_minutes_asleep': 'Minutes Asleep/Night', 'very_active_minutes': 'Active Mins'},
            title="<b>The Sedentary Squeeze: More Inactivity Correlates with Poorer Sleep</b><br><sup>A strong negative correlation (-0.53) links sedentary time to shorter sleep duration</sup>"
        )
        fig_scatter.update_layout(
            paper_bgcolor=BB_DARK,
            plot_bgcolor=BB_DARK,
            font=dict(color=BB_IVORY),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False),
            coloraxis_colorbar=dict(title="Vigorous Mins"),
            margin=dict(t=80, b=50, l=20, r=20)
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

# ==========================================
# TAB 3: HOURLY & DAILY RHYTHMS
# ==========================================
with tab3:
    st.markdown("### User Routines and Temporal Cycles")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Weekday vs Weekend Average Steps & Sleep Comparison
        wk_agg = filtered_daily.groupby('is_weekend')[['total_steps', 'total_minutes_asleep']].mean().reset_index()
        wk_agg['day_type'] = wk_agg['is_weekend'].map({0: 'Weekdays', 1: 'Weekends'})
        
        fig_days = gr.Figure()
        
        # Steps Bars
        fig_days.add_trace(gr.Bar(
            name="Steps / Day",
            x=wk_agg['day_type'],
            y=wk_agg['total_steps'],
            marker_color=BB_PEACH,
            yaxis="y"
        ))
        
        # Sleep Bars
        fig_days.add_trace(gr.Bar(
            name="Sleep (Mins)",
            x=wk_agg['day_type'],
            y=wk_agg['total_minutes_asleep'],
            marker_color=BB_ROSE,
            yaxis="y2"
        ))
        
        fig_days.update_layout(
            title="<b>Weekday vs. Weekend Rhythms</b><br><sup>Weekend sleep duration rises (+28 mins) while steps slightly decline</sup>",
            paper_bgcolor=BB_DARK,
            plot_bgcolor=BB_DARK,
            font=dict(color=BB_IVORY),
            barmode='group',
            xaxis=dict(showgrid=False),
            yaxis=dict(title="Steps / Day", showgrid=False),
            yaxis2=dict(title="Minutes Asleep", overlaying="y", side="right", showgrid=False),
            legend=dict(orientation="h", y=-0.1, x=0),
            margin=dict(t=80, b=50, l=20, r=20)
        )
        st.plotly_chart(fig_days, use_container_width=True)
        
    with col2:
        # Hourly Steps profile
        if len(filtered_hourly) > 0:
            hourly_agg = filtered_hourly.groupby('hour')['step_total'].mean().reset_index()
            
            fig_hourly = px.line(
                hourly_agg,
                x='hour',
                y='step_total',
                color_discrete_sequence=[BB_PEACH],
                labels={'hour': 'Hour of the Day', 'step_total': 'Average Steps Taken'},
                title="<b>Daily Active Routine (Hourly Step Distribution)</b><br><sup>Peak activity occurs post-work (5-7 PM) and during lunch (12-2 PM)</sup>"
            )
            # Add shaded regions for peaks and sedentary lulls
            fig_hourly.update_layout(
                paper_bgcolor=BB_DARK,
                plot_bgcolor=BB_DARK,
                font=dict(color=BB_IVORY),
                xaxis=dict(showgrid=False, tickmode='linear', tick0=0, dtick=2),
                yaxis=dict(showgrid=False),
                margin=dict(t=80, b=50, l=20, r=20)
            )
            st.plotly_chart(fig_hourly, use_container_width=True)
        else:
            st.info("No hourly data available for the current filter selections.")

# ==========================================
# TAB 4: MARKETING RECOMMENDATIONS (THE ACT PHASE)
# ==========================================
with tab4:
    st.markdown("### Bellabeat Strategic Pitch Map")
    st.markdown("<p style='font-style:italic; color:#DF9E8A;'>Transforming public tracker insights into direct revenue acquisition strategies for Bellabeat products.</p>", unsafe_allow_html=True)
    
    # 4 Product Cards mapping data insights to actions
    st.markdown("""
    <div class='product-card'>
        <div class='product-title'>🌸 Bellabeat App & Membership</div>
        <div class='product-subtitle'>Insight: 36% of user tracking days are highly sedentary (<5,000 steps), and users sleep +28 mins longer on weekends while step count dips.</div>
        <p style='color:#F4ECE8; font-size:0.95rem;'>
            <b>Action Strategy:</b> Design <i>"Weekend Refocus"</i> and <i>"Midday Movement"</i> in-app push challenges. Since we identified peak sedentary hours around 10:00 AM and 3:00 PM, the app should send soft, mindfulness-aligned nudges to take a 5-minute stretch. Pair this with weekend-specific step streaks to capture the weekend lull.
        </p>
    </div>
    
    <div class='product-card'>
        <div class='product-title'>💍 Leaf & Time Wellness Trackers</div>
        <div class='product-subtitle'>Insight: Average daily steps are 7,247 (well below the active 10,000 threshold), and wear consistency is highly moderate (only 1 user wore the device >=80% days).</div>
        <p style='color:#F4ECE8; font-size:0.95rem;'>
            <b>Action Strategy:</b> Market Leaf and Time as the ultimate <i>"Everyday Elegant Tracker"</i> focusing on lightweight beauty. Pitch a marketing campaign highlighting that <b>smart jewelry doesn't look like a computer on your wrist</b>, motivating high wear-consistency. Program gentle, customizable haptic vibrations (silent nudges) during the daily sedentary lulls.
        </p>
    </div>
    
    <div class='product-card'>
        <div class='product-title'>💧 Spring Smart Water Bottle</div>
        <div class='product-subtitle'>Insight: Hourly activity spikes between 5:00 PM and 7:00 PM. Users need preparation for their high-intensity intervals.</div>
        <p style='color:#F4ECE8; font-size:0.95rem;'>
            <b>Action Strategy:</b> Promote the Spring bottle as a proactive workout-prep tool. Market hydration as a prerequisite to managing the physical demands of peak daily exercise periods. Pitch automated pre-workout alerts (e.g. at 4:30 PM, right before the evening peak) prompting users to drink.
        </p>
    </div>
    
    <div class='product-card'>
        <div class='product-title'>⚖️ Aria Smart Scale</div>
        <div class='product-subtitle'>Insight: Weight logs had the lowest tracking rate (only 13 out of 35 users logged weight, and 90%+ were manually typed).</div>
        <p style='color:#F4ECE8; font-size:0.95rem;'>
            <b>Action Strategy:</b> Leverage this massive gap to acquire new customers. Pitch Aria as the solution to <i>"Zero-Effort Tracking"</i>. Highlight that manually typing weight log info causes tracking burnout, whereas Aria syncs weight, fat, and BMI automatically via Wi-Fi/Bluetooth to the Bellabeat App, eliminating user logging fatigue.
        </p>
    </div>
    """, unsafe_allow_html=True)
