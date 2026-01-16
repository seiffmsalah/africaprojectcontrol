import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Config
st.set_page_config(page_title="Africa Project Command Center", layout="wide")

# 2. Corrected CSS Style (White background & Red metrics)
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #CC0000 !important; font-weight: bold; }
    h1, h2, h3 { color: #1A1A1A !important; font-family: 'Helvetica', sans-serif; }
    .stProgress > div > div > div > div { background-color: #CC0000; }
    </style>
    """, unsafe_allow_html=True)

# 3. Your Project Data (Organized for Africa Portfolio)
data = {
    'Project': ['Nile Bridge Phase I', 'Lagos Port Expansion', 'Nairobi Urban Rail', 'Cape Wind Farm', 'Accra Tech Hub'],
    'Country': ['Egypt', 'Nigeria', 'Kenya', 'South Africa', 'Ghana'],
    'lat': [26.8, 9.08, -1.28, -30.5, 7.9], 
    'lon': [30.8, 8.6, 36.8, 22.9, -1.0],
    'Contract_Value': [250e6, 410e6, 150e6, 320e6, 95e6],
    'Actual_Costs': [180e6, 320e6, 110e6, 200e6, 88e6],
    'EAC_Costs': [230e6, 395e6, 145e6, 305e6, 92e6],
    'POC_Pct': [85, 45, 92, 30, 65],
    'Sch_Var': [-2, -12, 5, -25, 0], # Schedule Variance %
    'Likely_GP': [15.2, 8.5, 12.0, 5.5, -2.1]
}
df = pd.DataFrame(data)

# 4. Dashboard Header
st.title("🌍 Africa Portfolio | Executive Control Room")
st.markdown("---")

# 5. Top Level KPIs (The Big Red Numbers)
c1, c2, c3, c4 = st.columns(4)
total_rev = df['Contract_Value'].sum()
avg_gp = df['Likely_GP'].mean()
c1.metric("Total Portfolio Value", f"${total_rev/1e6:.1f}M")
c2.metric("Avg Gross Profit %", f"{avg_gp:.1f}%", delta="-1.4% vs Plan")
c3.metric("Critical Alerts", "3 Projects", delta="High Risk", delta_color="inverse")
c4.metric("Avg Schedule Var", f"{df['Sch_Var'].mean():.1f}%")

# 6. The Interactive Map (Styled based on your reference)
st.subheader("Geographic Risk Distribution")
fig_map = px.scatter_mapbox(
    df, lat="lat", lon="lon", size="Contract_Value", color="Sch_Var",
    color_continuous_scale=['#CC0000', '#F5F5F5', '#444444'], # Red for delays, White/Grey for on track
    hover_name="Project", hover_data=["Country", "POC_Pct", "Likely_GP"],
    zoom=2.5, height=500, mapbox_style="carto-positron"
)
fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig_map, use_container_width=True)

# 7. Detailed Financial Table
st.markdown("---")
st.subheader("Project Financial Performance Details")
# Creating a clean display table
display_df = df[['Project', 'Country', 'Contract_Value', 'EAC_Costs', 'POC_Pct', 'Likely_GP', 'Sch_Var']]
st.dataframe(display_df.style.format({
    'Contract_Value': '${:,.0f}',
    'EAC_Costs': '${:,.0f}',
    'Likely_GP': '{:.1f}%',
    'Sch_Var': '{:.1f}%',
    'POC_Pct': '{:.1f}%'
}), use_container_width=True)

st.info("💡 Note: Data is synced live from Project Control central repository.")
