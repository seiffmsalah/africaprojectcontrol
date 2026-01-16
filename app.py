import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import requests
from streamlit_lottie import st_lottie

# ────────────────────────────────────────────────
# 1. Page Config (Must be the very first Streamlit command)
# ────────────────────────────────────────────────
st.set_page_config(page_title="Elsewedy T&D Project Dashboard", layout="wide")

# ────────────────────────────────────────────────
# 2. Enhanced Styling & Animations
# ────────────────────────────────────────────────
st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    /* Animated Metric Card Effect */
    [data-testid="stMetric"] {
        background-color: #f8f9fa;
        border-left: 5px solid #d32f2f;
        padding: 15px;
        border-radius: 8px;
        transition: all 0.3s ease-in-out;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0px 4px 15px rgba(211, 47, 47, 0.15);
        background-color: #fffafa;
    }

    /* Pulsing Status Dot */
    .pulse-container { display: flex; align-items: center; gap: 12px; margin-bottom: 5px; }
    .pulse-dot {
        width: 12px; height: 12px; background: #d32f2f; border-radius: 50%;
        box-shadow: 0 0 0 rgba(211, 47, 47, 0.4);
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(211, 47, 47, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(211, 47, 47, 0); }
        100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(211, 47, 47, 0); }
    }

    /* Progress Bar Color */
    .stProgress > div > div > div { background-color: #d32f2f !important; }
    .logo-container { text-align: center; margin-bottom: 2rem; }
    .logo-container img { max-width: 350px; height: auto; }
    </style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# 3. Data & Assets
# ────────────────────────────────────────────────
@st.cache_data
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Industrial/Energy Animation Link
lottie_url = "https://assets5.lottiefiles.com/packages/lf20_V9t630.json"
lottie_data = load_lottieurl(lottie_url)

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

# Generate Mock Data
np.random.seed(42)
data = pd.DataFrame({
    'Country': list(country_to_code.keys()),
    'Revenue': np.random.randint(1200000, 7200000, size=len(country_to_code)),
    'Budget Cost': np.random.randint(900000, 5500000, size=len(country_to_code)),
    'Actual Costs': np.random.randint(600000, 4200000, size=len(country_to_code)),
    'POC': np.random.uniform(0.15, 0.95, size=len(country_to_code)),
    'Planned Progress': np.random.uniform(0.25, 0.99, size=len(country_to_code)),
    'Actual Progress': np.random.uniform(0.10, 0.92, size=len(country_to_code)),
    'Total Float': np.random.randint(5, 140, size=len(country_to_code))
})
data['GP%'] = ((data['Revenue'] - data['Budget Cost']) / data['Revenue']) * 100

# ────────────────────────────────────────────────
# 4. Main Layout
# ────────────────────────────────────────────────
st.markdown(
    '<div class="logo-container">'
    '<img src="https://logos-world.net/wp-content/uploads/2023/04/Elsewedy-Electric-Logo.png" alt="Elsewedy Logo">'
    '</div>',
    unsafe_allow_html=True
)

if 'selected_country' not in st.session_state:
    st.session_state.selected_country = None

left_col, right_col = st.columns([6, 4])

with left_col:
    # Sidebar Logic
    sidebar_country = st.sidebar.selectbox(
        "Navigation",
        options=["(Select Project)"] + sorted(data['Country'].unique().tolist())
    )
    if sidebar_country != "(Select Project)":
        st.session_state.selected_country = sidebar_country

    if st.session_state.selected_country:
        row = data[data['Country'] == st.session_state.selected_country].iloc[0]
        
        # Dashboard Header with Pulse
        h_col1, h_col2 = st.columns([0.85, 0.15])
        with h_col1:
            st.markdown(f"""
                <div class="pulse-container">
                    <div class="pulse-dot"></div>
                    <h1 style='margin:0;'>{st.session_state.selected_country} Site {get_flag_emoji(st.session_state.selected_country)}</h1>
                </div>
            """, unsafe_allow_html=True)
            st.caption("Active Project Data • Live Stream Enabled")
        
        with h_col2:
            if lottie_data:
                st_lottie(lottie_data, height=70, key="header_anim")
            else:
                st.write("🏗️")

        # Top Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Contract Value", f"${row['Revenue']:,.0f}")
        m2.metric("Gross Profit Margin", f"{row['GP%']:.1f}%")
        m3.metric("Schedule Buffer", f"{row['Total Float']} Days")

        st.divider()

        # Progress Visuals
        d1, d2 = st.columns(2)
        prog_configs = [
            (d1, "Planned Progress", row['Planned Progress'], "#6c757d", "p1"),
            (d2, "Actual (Physical)", row['Actual Progress'], "#d32f2f", "p2")
        ]
        
        for col, title, val, color, k in prog_configs:
            with col:
                fig = go.Figure(go.Pie(
                    values=[val*100, 100-(val*100)],
                    hole=0.75,
                    marker_colors=[color, "#f0f2f6"],
                    textinfo='none'
                ))
                fig.update_layout(
                    title=dict(text=title, x=0.5, font=dict(size=14)),
                    height=220, margin=dict(t=40, b=0, l=0, r=0),
                    showlegend=False,
                    annotations=[dict(text=f"{val*100:.0f}%", x=0.5, y=0.5, font_size=24, showarrow=False)]
                )
                st.plotly_chart(fig, use_container_width=True, key=k)

    else:
        st.info("Select a project to view metrics.")
        if lottie_data:
            st_lottie(lottie_data, height=350, key="main_idle")

with right_col:
    st.subheader("Regional Project Map")
    fig_map = px.choropleth(
        data,
        locations='Country',
        locationmode='country names',
        color='Revenue',
        color_continuous_scale='Reds',
        scope='africa',
        template='plotly_white'
    )
    fig_map.update_layout(
        margin=dict(r=0, t=0, l=0, b=0),
        coloraxis_showscale=False,
        geo=dict(bgcolor='white', lakecolor='white')
    )
    
    selected_map = st.plotly_chart(fig_map, use_container_width=True, on_select="rerun")
    
    if selected_map and selected_map.get("selection"):
        points = selected_map["selection"].get("points")
        if points:
            st.session_state.selected_country = points[0].get("location")
            st.rerun()

st.markdown("---")
st.caption("Elsewedy T&D Digital Control Center • 2026")
