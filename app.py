import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ────────────────────────────────────────────────
# Page config + styling
# ────────────────────────────────────────────────
st.set_page_config(page_title="Elsewedy T&D Project Dashboard", layout="wide")

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
    .logo-container { text-align: center; margin: 1.5rem 0 2rem 0; }
    .logo-container img { max-width: 400px; height: auto; }
    </style>
""", unsafe_allow_html=True)

# Logo – switched to reliable PNG from seeklogo (allows embedding)
st.markdown(
    '<div class="logo-container">'
    '<img src="https://seeklogo.com/images/E/elsewedy-electric-logo-0E0E0E0E0E-seeklogo.com.png" alt="Elsewedy Electric Logo">'
    '</div>',
    unsafe_allow_html=True
)

# ────────────────────────────────────────────────
# Sample data
# ────────────────────────────────────────────────
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

map_data = pd.DataFrame({'Country': african_countries})
map_data = map_data.merge(data, on='Country', how='left')
map_data['Has Data'] = ~map_data['Revenue'].isna()
map_data['hover_text'] = map_data.apply(
    lambda r: f"{r['Country']}<br>{'Has project data' if r['Has Data'] else 'No project data'}", axis=1
)

# Session state
if 'selected_country' not in st.session_state:
    st.session_state.selected_country = None

# ────────────────────────────────────────────────
# UI
# ────────────────────────────────────────────────
st.title("Elsewedy Electric T&D – Project Construction Dashboard")
st.markdown("Africa – Project Overview & Control")

# Sidebar
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

# Map
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

chart = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

if chart and 'selection' in chart and chart['selection']:
    points = chart['selection'].get('points', [])
    if points:
        clicked_country = points[0].get('location')
        if clicked_country and clicked_country in data['Country'].values:
            st.session_state.selected_country = clicked_country

# ────────────────────────────────────────────────
# Project Details + two donut charts
# ────────────────────────────────────────────────
if st.session_state.selected_country:
    country = st.session_state.selected_country
    if country in data['Country'].values:
        row = data[data['Country'] == country].iloc[0]

        st.subheader(f"Project: {country}")
        st.markdown("**Selected via map or sidebar**")

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

        # Progress – two donut charts
        st.subheader("Project Progress")

        donut_cols = st.columns(2)

        with donut_cols[0]:
            planned_pct = row['Planned Progress'] * 100
            fig_planned = go.Figure(data=[go.Pie(
                values=[planned_pct, 100 - planned_pct],
                labels=['Progress', 'Remaining'],
                hole=0.65,
                marker_colors=['grey', '#f0f0f0'],
                textinfo='none',
                hoverinfo='label+percent',
                pull=[0.02, 0]
            )])
            fig_planned.update_layout(
                title_text=f"Planned Progress",
                title_x=0.5,
                title_font=dict(size=16, color='black'),
                showlegend=False,
                paper_bgcolor='white',
                margin=dict(t=50, b=20, l=20, r=20),
                height=280,
                annotations=[dict(
                    text=f"{planned_pct:.0f}%",
                    x=0.5, y=0.5,
                    font_size=40,
                    font_color='black',
                    showarrow=False
                )]
            )
            st.plotly_chart(fig_planned, use_container_width=True)

        with donut_cols[1]:
            actual_pct = row['Actual Progress'] * 100
            fig_actual = go.Figure(data=[go.Pie(
                values=[actual_pct, 100 - actual_pct],
                labels=['Progress', 'Remaining'],
                hole=0.65,
                marker_colors=['#d32f2f', '#f0f0f0'],
                textinfo='none',
                hoverinfo='label+percent',
                pull=[0.02, 0]
            )])
            fig_actual.update_layout(
                title_text=f"Actual Progress",
                title_x=0.5,
                title_font=dict(size=16, color='black'),
                showlegend=False,
                paper_bgcolor='white',
                margin=dict(t=50, b=20, l=20, r=20),
                height=280,
                annotations=[dict(
                    text=f"{actual_pct:.0f}%",
                    x=0.5, y=0.5,
                    font_size=40,
                    font_color='black',
                    showarrow=False
                )]
            )
            st.plotly_chart(fig_actual, use_container_width=True)

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
    st.info("Click a **red** country on the map to view project details.")

st.markdown("---")
st.caption("Elsewedy Electric T&D – Project Control Dashboard • Sample data • Colors: white / grey / black / red")
