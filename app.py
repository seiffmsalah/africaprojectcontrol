import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Set page config for white background and custom theme
st.set_page_config(page_title="Project Construction Dashboard", layout="wide")
st.markdown("""
    <style>
    .stApp {
        background-color: white;
    }
    .stMetric {
        color: black;
    }
    .stProgress > div > div > div > div {
        background-color: red;
    }
    </style>
""", unsafe_allow_html=True)

# Sample data generation
# List of African countries for the map
african_countries = [
    'Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi', 'Cameroon', 'Cape Verde',
    'Central African Republic', 'Chad', 'Comoros', 'Democratic Republic of the Congo', 'Republic of Congo',
    'Djibouti', 'Egypt', 'Equatorial Guinea', 'Eritrea', 'Eswatini', 'Ethiopia', 'Gabon', 'Gambia',
    'Ghana', 'Guinea', 'Guinea-Bissau', 'Ivory Coast', 'Kenya', 'Lesotho', 'Liberia', 'Libya',
    'Madagascar', 'Malawi', 'Mali', 'Mauritania', 'Mauritius', 'Morocco', 'Mozambique', 'Namibia',
    'Niger', 'Nigeria', 'Rwanda', 'Sao Tome and Principe', 'Senegal', 'Seychelles', 'Sierra Leone',
    'Somalia', 'South Africa', 'South Sudan', 'Sudan', 'Tanzania', 'Togo', 'Tunisia', 'Uganda', 'Zambia', 'Zimbabwe'
]

# Generate sample project data for a subset of countries
selected_countries = np.random.choice(african_countries, size=10, replace=False)
data = pd.DataFrame({
    'Country': selected_countries,
    'Revenue': np.random.randint(1000000, 5000000, size=10),
    'Budget Cost': np.random.randint(800000, 4000000, size=10),
    'Actual Costs': np.random.randint(500000, 3000000, size=10),
    'Achieved Revenue': np.random.randint(400000, 2000000, size=10),
    'POC': np.random.uniform(0.2, 0.9, size=10),  # Percentage of Completion
    'Planned Progress': np.random.uniform(0.3, 0.95, size=10),
    'Actual Progress': np.random.uniform(0.25, 0.85, size=10),
    'Total Float': np.random.randint(10, 100, size=10)  # Days
})

# Calculations
data['GP%'] = ((data['Revenue'] - data['Budget Cost']) / data['Revenue']) * 100
data['EAC'] = data['Budget Cost'] / data['POC']  # Simplified Estimate at Completion
data['ETC'] = data['EAC'] - data['Actual Costs']  # Estimate to Complete

# Full map data (including all African countries, with NaN for no data)
map_data = pd.DataFrame({'Country': african_countries})
map_data = map_data.merge(data, on='Country', how='left')
map_data['Has Data'] = ~map_data['Revenue'].isna()

# Sidebar for selection
st.sidebar.title("Filters")
selected_country = st.sidebar.selectbox("Select Country/Project", options=sorted(data['Country'].unique()))

# Main dashboard
st.title("Project Construction Dashboard")

# Interactive Map
st.subheader("Africa Project Map")
fig = px.choropleth(
    map_data,
    locations='Country',
    locationmode='country names',
    color='Has Data',
    color_discrete_map={True: 'red', False: 'grey'},
    scope='africa',
    labels={'Has Data': 'Project Availability'},
    hover_name='Country',
    hover_data={'Revenue': True, 'Budget Cost': True} if 'Revenue' in map_data else None
)
fig.update_layout(
    coloraxis_showscale=False,
    margin={"r":0,"t":0,"l":0,"b":0},
    paper_bgcolor='white',
    geo=dict(bgcolor='white')
)

# Highlight selected country
if selected_country:
    selected_data = map_data[map_data['Country'] == selected_country]
    fig.add_trace(px.choropleth(
        selected_data,
        locations='Country',
        locationmode='country names',
        color_discrete_sequence=['black'],
        scope='africa'
    ).data[0])

st.plotly_chart(fig, use_container_width=True)

# Filter data for selected country
if selected_country:
    project_data = data[data['Country'] == selected_country].iloc[0]
    
    # KPI Metrics in columns
    st.subheader(f"Key Metrics for {selected_country}")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Revenue", f"${project_data['Revenue']:,}")
        st.metric("Budget Cost", f"${project_data['Budget Cost']:,}")
    
    with col2:
        st.metric("GP%", f"{project_data['GP%']:.2f}%")
        st.metric("Actual Costs", f"${project_data['Actual Costs']:,}")
    
    with col3:
        st.metric("Achieved Revenue", f"${project_data['Achieved Revenue']:,}")
        st.metric("POC", f"{project_data['POC']*100:.2f}%")
    
    with col4:
        st.metric("EAC", f"${project_data['EAC']:.0f}")
        st.metric("ETC", f"${project_data['ETC']:.0f}")
    
    # Progress Section
    st.subheader("Progress Overview")
    prog_col1, prog_col2 = st.columns(2)
    
    with prog_col1:
        st.write("Planned Progress")
        st.progress(project_data['Planned Progress'], text=f"{project_data['Planned Progress']*100:.2f}%")
        
        st.write("Actual Progress")
        st.progress(project_data['Actual Progress'], text=f"{project_data['Actual Progress']*100:.2f}%")
    
    with prog_col2:
        # Simple bar chart for comparison
        progress_df = pd.DataFrame({
            'Type': ['Planned', 'Actual'],
            'Progress': [project_data['Planned Progress'], project_data['Actual Progress']]
        })
        bar_fig = px.bar(
            progress_df,
            x='Type',
            y='Progress',
            color='Type',
            color_discrete_map={'Planned': 'grey', 'Actual': 'red'},
            labels={'Progress': 'Progress %'},
            height=300
        )
        bar_fig.update_layout(
            paper_bgcolor='white',
            plot_bgcolor='white',
            showlegend=False,
            yaxis_tickformat='.0%'
        )
        st.plotly_chart(bar_fig, use_container_width=True)
    
    # Total Float
    st.subheader("Schedule")
    st.metric("Total Float", f"{project_data['Total Float']} days")
    
    # Interactive elements: Slider for scenario analysis
    st.subheader("Scenario Analysis")
    adjusted_poc = st.slider("Adjust POC for What-If Analysis", 0.0, 1.0, project_data['POC'])
    adjusted_eac = project_data['Budget Cost'] / adjusted_poc if adjusted_poc > 0 else 0
    adjusted_etc = adjusted_eac - project_data['Actual Costs']
    st.metric("Adjusted EAC", f"${adjusted_eac:.0f}")
    st.metric("Adjusted ETC", f"${adjusted_etc:.0f}")
else:
    st.info("Select a country from the sidebar to view project details.")
