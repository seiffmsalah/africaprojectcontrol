import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. AI Theme Setup
st.set_page_config(page_title="AI Project Command", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for "Out of this World" look (Dark Glassmorphism)
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FFFFFF; }
    .stMetric { 
        background: rgba(255, 255, 255, 0.05); 
        padding: 20px; border-radius: 15px; 
        border: 1px solid rgba(204, 0, 0, 0.3);
        box-shadow: 0 4px 15px rgba(204, 0, 0, 0.2);
    }
    [data-testid="stMetricValue"] { color: #FF0000 !important; font-family: 'Courier New'; }
    .stDataFrame { border: 1px solid #444; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Advanced Project Data
data = {
    'Project': ['Nile Bridge I', 'Lagos Port', 'Nairobi Rail', 'Cape Wind', 'Accra Tech'],
    'Country': ['Egypt', 'Nigeria', 'Kenya', 'South Africa', 'Ghana'],
    'lat': [26.8, 9.08, -1.28, -30.5, 7.9], 
    'lon': [30.8, 8.6, 36.8, 22.9, -1.0],
    'Value': [250, 410, 150, 320, 95], # In Millions
    'POC': [85, 45, 92, 30, 65],
    'Risk_Level': ['Low', 'High', 'Low', 'Medium', 'Critical']
}
df = pd.DataFrame(data)

# 3. Sidebar Selection (AI pill interaction)
st.title("🛰️ AFRICA AI COMMAND CENTER")
st.write("### Portfolio Intelligence & Geospatial Analytics")

selected_project = st.selectbox("🎯 Target Project for Analysis:", df['Project'])
project_data = df[df['Project'] == selected_project].iloc[0]

# 4. Top Interactive Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Project Focus", project_data['Project'])
col2.metric("Contract Value", f"${project_data['Value']}M")
col3.metric("Completion (POC)", f"{project_data['POC']}%")
col4.metric("Risk Status", project_data['Risk_Level'])

# 5. 3D Animated Globe
st.markdown("### 🌐 Global Geospatial Positioning")

fig = go.Figure()

# Add all projects as glowing points
fig.add_trace(go.Scattergeo(
    lon = df['lon'], lat = df['lat'],
    text = df['Project'],
    marker = dict(
        size = 12, color = '#FF0000', symbol = 'circle',
        line = dict(width=2, color='white'),
        opacity = 0.8
    ),
    name = "Active Projects"
))

# Highlight selected project with a "Radar Pulse" effect
fig.add_trace(go.Scattergeo(
    lon = [project_data['lon']], lat = [project_data['lat']],
    marker = dict(size = 25, color = 'rgba(255, 0, 0, 0.4)', symbol = 'circle'),
    name = "Target Focus"
))

# Configure the 3D Globe
fig.update_geos(
    projection_type="orthographic", # Makes it a 3D Globe
    showcountries=True, countrycolor="#444",
    showocean=True, oceancolor="#000814",
    showlakes=True, lakecolor="#000814",
    bgcolor='rgba(0,0,0,0)',
    # Fly-to effect: center the globe on the selected project
    projection_rotation=dict(lon=project_data['lon'], lat=project_data['lat'], roll=0)
)

fig.update_layout(
    height=600, margin={"r":0,"t":0,"l":0,"b":0},
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# 6. AI Interaction Panel
st.markdown("---")
left, right = st.columns([1, 2])

with left:
    st.write("### 🤖 AI Insight")
    if project_data['Risk_Level'] == 'Critical':
        st.error(f"Attention: {project_data['Project']} shows a GP slippage of 4%. Immediate intervention required in {project_data['Country']}.")
    else:
        st.success(f"System Check: {project_data['Project']} is performing within parameters. No immediate risk detected.")

with right:
    st.write("### 📊 Financial Timeline")
    st.line_chart(df['Value']) # Placeholder for actual historical data
