import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go

# Page config + readable dark text on white background
st.set_page_config(page_title="Project Construction Dashboard", layout="wide")

st.markdown("""
    <style>
    .stApp, .main, .block-container { background-color: white !important; }
    body, div, span, p, h1, h2, h3, h4, h5, h6, label, .stMarkdown, .stText,
    .stExpander, .stSidebar, .stSelectbox, .stSlider, .stNumberInput {
        color: #1a1a1a !important;
    }
    .stMetric label, .stMetric .metric-value { color: black !important; }
    .stMetric .metric-delta { color: #b22222 !important; }
    .stProgress > div > div > div { background-color: #d32f2f !important; }
    .stProgress > div { background-color: #e0e0e0 !important; }
    section[data-testid="stSidebar"] { background-color: #f8f9fa !important; }
    h1, h2, h3 { color: black !important; }
    </style>
""", unsafe_allow_html=True)

# Sample data generation
african_countries = [
    'Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi', 'Cameroon', 'Cape Verde',
    'Central African Republic', 'Chad', 'Comoros', 'Democratic Republic of the Congo', 'Republic of Congo',
    'Djibouti', 'Egypt', 'Equatorial Guinea', 'Eritrea', 'Eswatini', 'Ethiopia', 'Gabon', 'Gambia',
    'Ghana', 'Guinea', 'Guinea-Bissau', 'Ivory Coast', 'Kenya', 'Lesotho', 'Liberia', 'Libya',
    'Madagascar', 'Malawi', 'Mali', 'Mauritania', 'Mauritius', 'Morocco', 'Mozambique', 'Namibia',
    'Niger', 'Nigeria', 'Rwanda', 'Sao Tome and Principe', 'Senegal', 'Seychelles', 'Sierra Leone',
    'Somalia', 'South Africa', 'South Sudan', 'Sudan', 'Tanzania', 'Togo', 'Tunisia', 'Uganda', 'Zambia', 'Zimbabwe'
]

np.random.seed(42)
selected_countries = np.random.choice(african_countries, size=15, replace=False)
data = pd.DataFrame({
    'Country': selected_countries,
    'Revenue': np.random.randint(1200000, 7200000, size=15),
    'Budget Cost': np.random.randint(900000, 5500000, size=15),
    'Actual Costs': np.random.randint(600000, 4200000, size=15),
    'Achieved Revenue': np.random.randint(500000, 3800000, size=15),
    'POC': np.random.uniform(0.15, 0.95, size=15),
    'Planned Progress': np.random.uniform(0.25, 0.99, size=15),
    'Actual Progress': np.random.uniform(0.10, 0.92, size=15),
    'Total Float': np.random.randint(5, 140, size=15)
})

data['GP%'] = ((data['Revenue'] - data['Budget Cost']) / data['Revenue']) * 100
data['EAC'] = data['Budget Cost'] / np.maximum(data['POC'], 0.005)
data['ETC'] = data['EAC'] - data['Actual Costs']

# Prepare map dataset
map_data = pd.DataFrame({'Country': african_countries})
map_data = map_data.merge(data, on='Country', how='left')
map_data['Has Data'] = ~map_data['Revenue'].isna()
map_data['hover_text'] = map_data.apply(
    lambda r: f"{r['Country']}<br>{'Has project data' if r['Has Data'] else 'No project data'}", axis=1
)

# Session state to track selected country from map click
if 'selected_country' not in st.session_state:
    st.session_state.selected_country = None

# Main UI
st.title("Project Construction Dashboard")
st.markdown("Africa – Construction Project Overview & Control")

# Sidebar controls
st.sidebar.title("Controls")
sidebar_country = st.sidebar.selectbox(
    "Jump to Country / Project",
    options=["(Click map or select)"] + sorted(data['Country'].unique().tolist())
)

if sidebar_country != "(Click map or select)":
    st.session_state.selected_country = sidebar_country

st.sidebar.markdown("---")
if st.sidebar.button("Clear Selection"):
    st.session_state.selected_country = None
    st.rerun()

# Interactive Africa Map
st.subheader("Project Locations – Africa")

fig = px.choropleth(
    map_data,
    locations='Country',
    locationmode='country names',
    color='Has Data',
    color_discrete_map={True: 'red', False: 'lightgrey'},
    scope='africa',
    hover_name='hover_text',
    hover_data={
        'Revenue': ':,.0f',
        'Budget Cost': ':,.0f',
        'Has Data': False,
        'Country': False
    }
)

fig.update_traces(
    marker_line_width=0.8,
    marker_line_color='darkgrey',
    hovertemplate="%{hovertext}<extra></extra>"
)

fig.update_layout(
    coloraxis_showscale=False,
    margin=dict(r=0, t=30, l=0, b=0),
    paper_bgcolor='white',
    geo=dict(bgcolor='white'),
    clickmode='event+select'
)

# Highlight selected country with black border
if st.session_state.selected_country:
    sel = map_data[map_data['Country'] == st.session_state.selected_country]
    if not sel.empty:
        fig.add_trace(go.Choropleth(
            locations=sel['Country'],
            locationmode='country names',
            z=[1],
            colorscale=[[0, 'black'], [1, 'black']],
            showscale=False,
            marker_line_width=2.5,
            marker_line_color='black',
            hoverinfo='skip'
        ))

# Render chart and capture selection/click
chart = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

# Handle map click event
if chart and 'selection' in chart and chart['selection']:
    points = chart['selection'].get('points', [])
    if points:
        clicked_country = points[0].get('location')
        if clicked_country and clicked_country in data['Country'].values:
            st.session_state.selected_country = clicked_country

# Display project details when selected
if st.session_state.selected_country:
    country = st.session_state.selected_country
    if country in data['Country'].values:
        row = data[data['Country'] == country].iloc[0]

        st.subheader(f"Project Details: {country}")
        st.markdown(f"**Selected via map click / sidebar**")

        cols = st.columns(4)
        with cols[0]:
            st.metric("Revenue", f"${row['Revenue']:,.0f}")
            st.metric("Budget Cost", f"${row['Budget Cost']:,.0f}")
        with cols[1]:
            st.metric("Gross Profit %", f"{row['GP%']:.1f}%")
            st.metric("Actual Costs", f"${row['Actual Costs']:,.0f}")
        with cols[2]:
            st.metric("Achieved Revenue", f"${row['Achieved Revenue']:,.0f}")
            st.metric("Physical % Complete", f"{row['POC']*100:.1f}%")
        with cols[3]:
            st.metric("EAC", f"${row['EAC']:,.0f}")
            st.metric("ETC", f"${row['ETC']:,.0f}")

        st.divider()

        st.subheader("Progress Comparison")
        prog_cols = st.columns([2, 3])

        with prog_cols[0]:
            st.caption("Planned vs Actual Progress")
            st.progress(row['Planned Progress'], text=f"Planned: {row['Planned Progress']*100:.0f}%")
            st.progress(row['Actual Progress'], text=f"Actual:   {row['Actual Progress']*100:.0f}%")

        with prog_cols[1]:
            df_prog = pd.DataFrame({
                'Category': ['Planned Progress', 'Actual Progress'],
                'Value (%)': [row['Planned Progress']*100, row['Actual Progress']*100]
            })
            bar = px.bar(
                df_prog,
                x='Category',
                y='Value (%)',
                color='Category',
                color_discrete_map={'Planned Progress': 'grey', 'Actual Progress': 'red'},
                text_auto='.0f'
            )
            bar.update_layout(
                yaxis_title="Progress (%)",
                showlegend=False,
                paper_bgcolor='white',
                plot_bgcolor='white',
                height=340,
                margin=dict(l=20, r=20, t=10, b=60)
            )
            st.plotly_chart(bar, use_container_width=True)

        st.divider()
        st.metric("Total Float (Schedule Buffer)", f"{row['Total Float']} days")

        # What-if analysis
        st.subheader("What-If: Simulate Different % Complete")
        adj_poc_pct = st.slider(
            "Adjusted Physical % Complete",
            1, 100,
            int(row['POC']*100),
            format="%d%%",
            key=f"slider_{country}"
        )
        adj_poc = adj_poc_pct / 100.0
        adj_eac = row['Budget Cost'] / max(adj_poc, 0.005)
        adj_etc = adj_eac - row['Actual Costs']
        st.metric("Adjusted EAC", f"${adj_eac:,.0f}")
        st.metric("Adjusted ETC", f"${adj_etc:,.0f}")

    else:
        st.warning(f"No project data available for {country}.")
else:
    st.info("Click a **red** country on the map to view detailed project metrics.")

st.markdown("---")
st.caption("Dashboard colors: white background • grey/black/red accents • Sample data only")
