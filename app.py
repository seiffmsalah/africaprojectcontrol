import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import requests
from streamlit_lottie import st_lottie

# ────────────────────────────────────────────────
# Page config + styling
# ────────────────────────────────────────────────
st.set_page_config(page_title="Elsewedy T&D Project Dashboard", layout="wide")

# Enhanced CSS with Animations
st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    /* 1. Animated Metric Cards */
    [data-testid="stMetric"] {
        background-color: #f8f9fa;
        border-left: 5px solid #d32f2f;
        padding: 15px;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
        background-color: #fffafa;
    }

    /* 2. Pulsing Status Indicator */
    .pulse-container {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;
    }
    .pulse-dot {
        width: 12px;
        height: 12px;
        background: #d32f2f;
        border-radius: 50%;
        box-shadow: 0 0 0 rgba(211, 47, 47, 0.4);
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(211, 47, 47, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(211, 47, 47, 0); }
        100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(211, 47, 47, 0); }
    }

    /* Standard Styling */
    .stProgress > div > div > div { background-color: #d32f2f !important; }
    .logo-container { text-align: center; margin-bottom: 2rem; }
    .logo-container img { max-width: 350px; }
    </style>
""", unsafe_allow_html=True)

# Helper function for Lottie
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200: return None
    return r.json()

lottie_industrial = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_m6cu98v2.json")

# Logo
st.markdown(
    '<div class="logo-container">'
    '<img src="https://logos-world.net/wp-content/uploads/2023/04/Elsewedy-Electric-Logo.png" alt="Elsewedy Electric Logo">'
    '</div>',
    unsafe_allow_html=True
)

# ────────────────────────────────────────────────
# Logic & Data
# ────────────────────────────────────────────────
country_to_code = {
    'Algeria': 'DZ', 'Angola': 'AO', 'Egypt': 'EG', 'Ethiopia': 'ET', 
    'Ghana': 'GH', 'Kenya': 'KE', 'Morocco': 'MA', 'Nigeria': 'NG', 
    'South Africa': 'ZA', 'Tanzania': 'TZ', 'Uganda': 'UG', 'Zambia': 'ZM'
}

def get_flag_emoji(country_name):
    code = country_to_code.get(country_name)
    if code:
        return ''.join(chr(ord(c) + 0x1F1E6 - ord('A')) for c in code.upper())
    return "🌍"

african_countries = list(country_to_code.keys())
np.random.seed(42)
data = pd.DataFrame({
    'Country': african_countries,
    'Revenue': np.random.randint(1200000, 7200000, size=len(african_countries)),
    'Budget Cost': np.random.randint(900000, 5500000, size=len(african_countries)),
    'Actual Costs': np.random.randint(600000, 4200000, size=len(african_countries)),
    'POC': np.random.uniform(0.15, 0.95, size=len(african_countries)),
    'Planned Progress': np.random.uniform(0.25, 0.99, size=len(african_countries)),
    'Actual Progress': np.random.uniform(0.10, 0.92, size=len(african_countries)),
    'Total Float': np.random.randint(5, 140, size=len(african_countries))
})
data['GP%'] = ((data['Revenue'] - data['Budget Cost']) / data['Revenue']) * 100

if 'selected_country' not in st.session_state:
    st.session_state.selected_country = None

# ────────────────────────────────────────────────
# Layout
# ────────────────────────────────────────────────
left_col, right_col = st.columns([6, 4])

with left_col:
    st.sidebar.title("Project Controls")
    sidebar_country = st.sidebar.selectbox(
        "Select Project Site",
        options=["(Click map or select)"] + sorted(data['Country'].unique().tolist())
    )

    if sidebar_country != "(Click map or select)":
        st.session_state.selected_country = sidebar_country

    if st.session_state.selected_country:
        row = data[data['Country'] == st.session_state.selected_country].iloc[0]
        
        # Header with Animation
        head1, head2 = st.columns([0.8, 0.2])
        with head1:
            st.markdown(f"""
                <div class="pulse-container">
                    <div class="pulse-dot"></div>
                    <h2 style='margin:0;'>{st.session_state.selected_country} Project Site {get_flag_emoji(st.session_state.selected_country)}</h2>
                </div>
            """, unsafe_allow_html=True)
            st.caption("Live Status: Active Construction Phase")
        with head2:
            st_lottie(lottie_industrial, height=80, key="nav_anim")

        # Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Contract Value", f"${row['Revenue']:,.0f}")
        m2.metric("Gross Profit", f"{row['GP%']:.1f}%")
        m3.metric("Schedule Float", f"{row['Total Float']} Days")

        st.divider()

        # Gauges/Donuts
        d1, d2 = st.columns(2)
        for col, label, val, color in zip([d1, d2], ["Planned", "Actual"], [row['Planned Progress'], row['Actual Progress']], ["#6c757d", "#d32f2f"]):
            with col:
                fig = go.Figure(go.Pie(
                    values=[val*100, 100-(val*100)],
                    hole=0.7,
                    marker_colors=[color, "#eeeeee"],
                    textinfo='none'
                ))
                fig.update_layout(
                    title=f"{label} Progress",
                    height=250, margin=dict(t=30, b=0, l=0, r=0),
                    annotations=[dict(text=f"{val*100:.0f}%", x=0.5, y=0.5, font_size=25, showarrow=False)],
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # What-If Simulation
        with st.expander("📊 Run Cost Sensitivity Analysis"):
            sim_poc = st.slider("Simulate % Completion", 0, 100, int(row['POC']*100))
            st.info(f"Predicted Estimate at Completion (EAC): **${(row['Budget Cost'] / max(sim_poc/100, 0.01)):,.0f}**")

    else:
        st.info("Please select a project from the map or sidebar to view live analytics.")
        st_lottie(lottie_industrial, height=300)

with right_col:
    st.subheader("Regional Footprint")
    
    map_df = data.copy()
    fig = px.choropleth(
        map_df,
        locations='Country',
        locationmode='country names',
        color='Revenue',
        color_continuous_scale='Reds',
        scope='africa',
        height=600
    )
    
    fig.update_layout(
        margin=dict(r=0, t=0, l=0, b=0),
        coloraxis_showscale=False,
        geo=dict(bgcolor='rgba(0,0,0,0)', lakecolor='#ffffff')
    )
    
    # Interaction logic
    selected_map = st.plotly_chart(fig, use_container_width=True, on_select="rerun")
    
    if selected_map and selected_map.get("selection"):
        points = selected_map["selection"].get("points")
        if points:
            st.session_state.selected_country = points[0].get("location")
            st.rerun()

st.markdown("---")
st.caption("Elsewedy T&D Digital Twin Dashboard • Proprietary Internal Data")
