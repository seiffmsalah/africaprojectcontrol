import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Force Clean White Theme & Branding
st.set_page_config(page_title="Elsewedy Project Command", layout="wide")

st.markdown("""
    <style>
    /* Force background to white and text to black */
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #CC0000 !important; font-weight: bold; }
    [data-testid="stMetricLabel"] { color: #555555 !important; }
    .project-card {
        padding: 20px; border-radius: 10px; background: #F8F9FA;
        border-left: 5px solid #CC0000; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Comprehensive Project Data (Budget, Actuals, EAC, POC)
data = {
    'Project': ['Nile Power 1', 'Lagos Substation', 'Nairobi Grid', 'Tanzania Dam', 'Algeria Solar'],
    'Country': ['Egypt', 'Nigeria', 'Kenya', 'Tanzania', 'Algeria'],
    'lat': [30.04, 6.52, -1.29, -6.36, 36.75], 
    'lon': [31.23, 3.37, 36.82, 34.88, 3.05],
    'Budget_Cost': [500000000, 120000000, 85000000, 900000000, 45000000],
    'Actual_Cost': [350000000, 95000000, 20000000, 400000000, 10000000],
    'EAC': [480000000, 125000000, 82000000, 890000000, 42000000],
    'POC_Percentage': [72, 80, 25, 45, 15]
}
df = pd.DataFrame(data)

# 3. Header & Navigation
st.title("🔴 ELSEWEDY ELECTRIC | Africa Portfolio")
st.markdown("### Executive Project Control Dashboard")

# 4. The Smart Map (Using Mapbox Light Style)
st.subheader("Interactive Geographic Intelligence")
fig = px.scatter_mapbox(
    df, lat="lat", lon="lon", 
    size="Budget_Cost", 
    color="POC_Percentage",
    color_continuous_scale=['#000000', '#CC0000'], # Black to Red
    hover_name="Project",
    hover_data={"lat": False, "lon": False, "Budget_Cost": True, "POC_Percentage": True},
    zoom=2.8, height=550
)

# Use 'light' or 'carto-positron' for a clean, professional "smart" look
fig.update_layout(
    mapbox_style="light", 
    mapbox_accesstoken="pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNqdnBvNDM4ZTAxZTM0M2lsMSNoMzY3dXoifQ.8px9Z3YBT88_6U_R6mN8tA", # Public token
    margin={"r":0,"t":0,"l":0,"b":0}
)

# Render the map and capture the click
st.plotly_chart(fig, use_container_width=True)

# 5. Smart Interaction: Project Spotlight
st.markdown("---")
st.subheader("🎯 Selection Analysis")
selected_name = st.selectbox("Select a project for deep-dive analysis:", df['Project'])
p = df[df['Project'] == selected_name].iloc[0]

# Detailed Card with all metrics
with st.container():
    st.markdown(f"""<div class="project-card">
    <h3>{p['Project']} - {p['Country']}</h3>
    </div>""", unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Budget Cost", f"${p['Budget_Cost']/1e6:.1f}M")
    m2.metric("Actual Cost", f"${p['Actual_Cost']/1e6:.1f}M")
    m3.metric("EAC Forecast", f"${p['EAC']/1e6:.1f}M")
    m4.metric("POC Completion", f"{p['POC_Percentage']}%")

# 6. Full Data Table at the bottom
with st.expander("View Full Data Inventory"):
    st.dataframe(df.style.highlight_max(axis=0, color='#FFCCCC'), use_container_width=True)
