import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Setup
st.set_page_config(page_title="Elsewedy Project Controls", layout="wide")

# 2. Elsewedy Branding (White, Red, Black)
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    h1, h2, h3 { color: #000000 !important; font-family: 'Arial', sans-serif; font-weight: bold; }
    [data-testid="stMetricValue"] { color: #CC0000 !important; }
    .stDataFrame { border: 1px solid #EEEEEE; }
    /* Style the sidebar to be sleek black/grey */
    [data-testid="stSidebar"] { background-color: #F8F9FA; border-right: 2px solid #CC0000; }
    </style>
    """, unsafe_allow_html=True)

# 3. Your Full Project Data (EAC, Budget, POC, etc.)
# You can edit these numbers right here!
data = {
    'Project': ['Nile Power Plant', 'Lagos Substation', 'Nairobi Grid', 'Tanzania Dam', 'Algeria Solar'],
    'Country': ['Egypt', 'Nigeria', 'Kenya', 'Tanzania', 'Algeria'],
    'lat': [30.04, 6.52, -1.29, -6.36, 36.75], 
    'lon': [31.23, 3.37, 36.82, 34.88, 3.05],
    'Budget_Cost': [500000000, 120000000, 85000000, 900000000, 45000000],
    'Actual_Cost': [350000000, 95000000, 20000000, 400000000, 10000000],
    'EAC': [480000000, 125000000, 82000000, 890000000, 42000000],
    'POC_Percentage': [72, 80, 25, 45, 15],
    'Currency': ['USD', 'USD', 'USD', 'USD', 'USD']
}
df = pd.DataFrame(data)

# Calculations
df['Variance'] = df['Budget_Cost'] - df['EAC']

# 4. Header
st.image("https://upload.wikimedia.org/wikipedia/commons/b/b2/Elsewedy_Electric_Logo.png", width=200) # Placeholder for logo
st.title("🌍 Africa Portfolio Executive Dashboard")
st.markdown("---")

# 5. Top KPIs
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Portfolio (Budget)", f"${df['Budget_Cost'].sum()/1e6:.1f}M")
c2.metric("Total Actual Spend", f"${df['Actual_Cost'].sum()/1e6:.1f}M")
c3.metric("Avg POC %", f"{df['POC_Percentage'].mean():.1f}%")
c4.metric("EAC Forecast", f"${df['EAC'].sum()/1e6:.1f}M")

# 6. Interactive Map (Clicking triggers info)
st.subheader("Project Map (Click dots to view stats)")
fig = px.scatter_mapbox(
    df, lat="lat", lon="lon", 
    size="Budget_Cost", 
    color="POC_Percentage",
    color_continuous_scale=['#000000', '#CC0000'], # Black to Elsewedy Red
    hover_name="Project",
    hover_data={
        "lat": False, "lon": False, 
        "Budget_Cost": ":$,.0f", 
        "Actual_Cost": ":$,.0f", 
        "EAC": ":$,.0f", 
        "POC_Percentage": ":.1f%"
    },
    zoom=2.8, height=600
)

fig.update_layout(
    mapbox_style="carto-positron",
    margin={"r":0,"t":0,"l":0,"b":0},
    clickmode='event+select'
)

st.plotly_chart(fig, use_container_width=True)

# 7. Financial Table (The "Hard Data")
st.markdown("---")
st.subheader("Project Financial Summary")
st.dataframe(df.drop(['lat', 'lon'], axis=1), use_container_width=True)
