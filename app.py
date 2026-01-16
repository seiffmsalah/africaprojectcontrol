import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ────────────────────────────────────────────────
# 1. Page Config
# ────────────────────────────────────────────────
st.set_page_config(page_title="Elsewedy T&D Command Center", layout="wide")

# ────────────────────────────────────────────────
# 2. Professional CSS (No Cartoons, Just Tech)
# ────────────────────────────────────────────────
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    
    /* Tactical Metric Cards */
    [data-testid="stMetric"] {
        background-color: #fcfcfc;
        border: 1px solid #e0e0e0;
        border-left: 5px solid #d32f2f;
        padding: 20px;
        border-radius: 0px; /* Sharp corners look more industrial */
        position: relative;
        overflow: hidden;
    }
    
    /* The 'Scanner' Animation - subtle data-loading look */
    [data-testid="stMetric"]::after {
        content: "";
        position: absolute;
        top: 0; left: -100%;
        width: 100%; height: 2px;
        background: linear-gradient(90deg, transparent, #d32f2f, transparent);
        animation: scan 3s linear infinite;
    }
    @keyframes scan {
        0% { left: -100%; }
        100% { left: 100%; }
    }

    /* Pulse Dot for Site Status */
    .status-box {
        display: flex;
        align-items: center;
        background: #1a1a1a;
        color: white;
        padding: 5px 15px;
        border-radius: 2px;
        width: fit-content;
        margin-bottom: 20px;
    }
    .pulse-dot {
        width: 8px; height: 8px; background: #ff0000; border-radius: 50%;
        margin-right: 10px;
        box-shadow: 0 0 8px #ff0000;
        animation: alert-pulse 1.2s ease-out infinite;
    }
    @keyframes alert-pulse {
        0% { opacity: 1; }
        50% { opacity: 0.3; }
        100% { opacity: 1; }
    }
    </style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# 3. Data Logic
# ────────────────────────────────────────────────
country_to_iso = {
    'Algeria': 'DZA', 'Angola': 'AGO', 'Egypt': 'EGY', 'Ethiopia': 'ETH', 
    'Ghana': 'GHA', 'Kenya': 'KEN', 'Morocco': 'MAR', 'Nigeria': 'NGA', 
    'South Africa': 'ZAF', 'Tanzania': 'TZA', 'Uganda': 'UGA', 'Zambia': 'ZMB'
}

np.random.seed(99)
data = pd.DataFrame({
    'Country': list(country_to_iso.keys()),
    'ISO': list(country_to_iso.values()),
    'Revenue': np.random.randint(2500000, 8500000, size=len(country_to_iso)),
    'GP%': np.random.uniform(18.5, 32.0, size=len(country_to_iso)),
    'POC': np.random.uniform(0.2, 0.95, size=len(country_to_iso)),
    'Float': np.random.randint(10, 90, size=len(country_to_iso))
})

# ────────────────────────────────────────────────
# 4. Dashboard Header
# ────────────────────────────────────────────────
st.image("https://logos-world.net/wp-content/uploads/2023/04/Elsewedy-Electric-Logo.png", width=250)
st.markdown("### T&D PROJECT CONTROL CENTER | AFRICA")
st.divider()

if 'selected_country' not in st.session_state:
    st.session_state.selected_country = None

# ────────────────────────────────────────────────
# 5. Main Content
# ────────────────────────────────────────────────
left_col, right_col = st.columns([5, 5])

with left_col:
    # Sidebar selection for redundancy
    sb = st.sidebar.selectbox("SITE SELECTOR", ["-- SELECT SITE --"] + sorted(data['Country'].tolist()))
    if sb != "-- SELECT SITE --":
        st.session_state.selected_country = sb

    if st.session_state.selected_country:
        res = data[data['Country'] == st.session_state.selected_country].iloc[0]
        
        st.markdown(f"""
            <div class="status-box">
                <div class="pulse-dot"></div>
                LIVE TELEMETRY: {st.session_state.selected_country.upper()}
            </div>
        """, unsafe_allow_html=True)

        m1, m2 = st.columns(2)
        m1.metric("CONTRACT REVENUE", f"${res['Revenue']:,.0f}")
        m2.metric("GROSS MARGIN", f"{res['GP%']:.2f}%")
        
        m3, m4 = st.columns(2)
        m3.metric("PHYSICAL COMPLETE", f"{res['POC']*100:.1f}%")
        m4.metric("TOTAL FLOAT", f"{res['Float']} DAYS")

        # Technical Progress Chart
        st.write("#### PROJECT EXECUTION CURVE")
        fig_curve = go.Figure()
        fig_curve.add_trace(go.Scatter(
            x=[0, 1, 2, 3, 4], y=[0, 20, 45, 75, 100], 
            name="Baseline", line=dict(color='black', dash='dash')
        ))
        fig_curve.add_trace(go.Scatter(
            x=[0, 1, 2], y=[0, 18, res['POC']*100], 
            name="Actual", line=dict(color='#d32f2f', width=4)
        ))
        fig_curve.update_layout(
            height=250, margin=dict(t=20, b=20, l=0, r=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            paper_bgcolor='white', plot_bgcolor='white'
        )
        st.plotly_chart(fig_curve, use_container_width=True)
    else:
        st.info("AWAITING SITE SELECTION. INTERACT WITH GLOBAL MAP TO INITIALIZE DATA.")

with right_col:
    # HIGH-CONTRAST MAP
    fig_map = px.choropleth(
        data,
        locations="ISO",
        color="Revenue",
        hover_name="Country",
        color_continuous_scale=["#f2f2f2", "#d32f2f", "#8b0000"],
        scope="africa",
        projection="natural earth"
    )

    fig_map.update_geos(
        showframe=False, showcoastlines=True,
        landcolor="#ffffff",
        countrycolor="#cccccc",
        coastlinecolor="#1a1a1a"
    )

    # Highlight selected country on map
    if st.session_state.selected_country:
        selected_iso = data[data['Country'] == st.session_state.selected_country]['ISO'].iloc[0]
        fig_map.add_trace(go.Choropleth(
            locations=[selected_iso],
            z=[100],
            colorscale=[[0, 'black'], [1, 'black']],
            showscale=False,
            marker_line_color='#ff0000',
            marker_line_width=3,
            hoverinfo='skip'
        ))

    fig_map.update_layout(
        height=600,
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_showscale=False
    )

    # Map Event Handling
    map_click = st.plotly_chart(fig_map, use_container_width=True, on_select="rerun")
    
    if map_click and map_click.get("selection"):
        pts = map_click["selection"].get("points")
        if pts:
            iso = pts[0].get("location")
            if iso:
                st.session_state.selected_country = data[data['ISO'] == iso]['Country'].values[0]
                st.rerun()

st.sidebar.markdown("---")
if st.sidebar.button("RESET SYSTEM"):
    st.session_state.selected_country = None
    st.rerun()
