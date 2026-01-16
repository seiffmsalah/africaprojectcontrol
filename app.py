import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ────────────────────────────────────────────────
# Page config + ORIGINAL styling
# ────────────────────────────────────────────────
st.set_page_config(page_title="Elsewedy T&D Project Dashboard", layout="wide")

st.markdown("""
<style>
.stApp, .main, .block-container {
    background-color: white !important;
}

body, div, span, p, h1, h2, h3, h4, h5, h6, label,
.stMarkdown, .stText, .stExpander, .stSidebar,
.stSelectbox, .stSlider, .stNumberInput {
    color: #1a1a1a !important;
}

.stMetric label, .stMetric .metric-value {
    color: black !important;
}

.stMetric .metric-delta {
    color: #b22222 !important;
}

.stProgress > div > div > div {
    background-color: #d32f2f !important;
}

.stProgress > div {
    background-color: #e0e0e0 !important;
}

section[data-testid="stSidebar"] {
    background-color: #f8f9fa !important;
}

h1, h2, h3 {
    color: black !important;
}

.logo-container {
    text-align: center;
    margin: 1.5rem 0 2rem 0;
}

.logo-container img {
    max-width: 400px;
    height: auto;
}

.country-flag {
    font-size: 2.2rem;
    margin-left: 0.5rem;
}

/* ───── MINIMAL RED GLOW (ADDED ONLY) ───── */

/* KPI subtle glow */
[data-testid="stMetric"] {
    border-radius: 8px;
    box-shadow: 0 0 0 rgba(211,47,47,0);
    animation: kpiGlow 3.5s ease-in-out infinite;
}

@keyframes kpiGlow {
    0%   { box-shadow: 0 0 0 rgba(211,47,47,0); }
    50%  { box-shadow: 0 0 12px rgba(211,47,47,0.25); }
    100% { box-shadow: 0 0 0 rgba(211,47,47,0); }
}

/* Selected country title glow */
.country-glow {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 6px;
    box-shadow: 0 0 10px rgba(211,47,47,0.35);
}

</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# Logo (ORIGINAL)
# ────────────────────────────────────────────────
st.markdown(
    '<div class="logo-container">'
    '<img src="https://logos-world.net/wp-content/uploads/2023/04/Elsewedy-Electric-Logo.png">'
    '</div>',
    unsafe_allow_html=True
)

# ────────────────────────────────────────────────
# Country → ISO Alpha-2 code mapping
# ────────────────────────────────────────────────
country_to_code = {
    'Algeria':'DZ','Angola':'AO','Benin':'BJ','Botswana':'BW','Burkina Faso':'BF',
    'Burundi':'BI','Cameroon':'CM','Cape Verde':'CV','Central African Republic':'CF',
    'Chad':'TD','Comoros':'KM','Democratic Republic of the Congo':'CD',
    'Republic of Congo':'CG','Djibouti':'DJ','Egypt':'EG','Equatorial Guinea':'GQ',
    'Eritrea':'ER','Eswatini':'SZ','Ethiopia':'ET','Gabon':'GA','Gambia':'GM',
    'Ghana':'GH','Guinea':'GN','Guinea-Bissau':'GW','Ivory Coast':'CI',
    'Kenya':'KE','Lesotho':'LS','Liberia':'LR','Libya':'LY','Madagascar':'MG',
    'Malawi':'MW','Mali':'ML','Mauritania':'MR','Mauritius':'MU','Morocco':'MA',
    'Mozambique':'MZ','Namibia':'NA','Niger':'NE','Nigeria':'NG','Rwanda':'RW',
    'Sao Tome and Principe':'ST','Senegal':'SN','Seychelles':'SC',
    'Sierra Leone':'SL','Somalia':'SO','South Africa':'ZA','South Sudan':'SS',
    'Sudan':'SD','Tanzania':'TZ','Togo':'TG','Tunisia':'TN','Uganda':'UG',
    'Zambia':'ZM','Zimbabwe':'ZW'
}

def get_flag_emoji(country_name):
    code = country_to_code.get(country_name)
    if code:
        return ''.join(chr(ord(c) + 0x1F1E6 - ord('A')) for c in code)
    return ""

# ────────────────────────────────────────────────
# Sample data (ORIGINAL)
# ────────────────────────────────────────────────
african_countries = list(country_to_code.keys())

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
    lambda r: f"{r['Country']}<br>{'Has project data' if r['Has Data'] else 'No project data'}",
    axis=1
)

# ────────────────────────────────────────────────
# Session state (ORIGINAL)
# ────────────────────────────────────────────────
if 'selected_country' not in st.session_state:
    st.session_state.selected_country = None

# ────────────────────────────────────────────────
# Layout (ORIGINAL)
# ────────────────────────────────────────────────
st.title("Elsewedy Electric T&D – Project Construction Dashboard")
st.markdown("Africa – Project Overview & Control")

left_col, right_col = st.columns([6, 4])

# ────────────────────────────────────────────────
# Sidebar (ORIGINAL)
# ────────────────────────────────────────────────
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

# ────────────────────────────────────────────────
# Left panel – project details (ORIGINAL + glow)
# ────────────────────────────────────────────────
with left_col:
    if st.session_state.selected_country:
        country = st.session_state.selected_country
        if country in data['Country'].values:
            row = data[data['Country'] == country].iloc[0]
            flag = get_flag_emoji(country)

            st.markdown(
                f"<h3 class='country-glow'>Project: {country} {flag}</h3>",
                unsafe_allow_html=True
            )

            cols = st.columns(4)
            cols[0].metric("Revenue", f"${row['Revenue']:,.0f}")
            cols[0].metric("Budget Cost", f"${row['Budget Cost']:,.0f}")
            cols[1].metric("Gross Profit %", f"{row['GP%']:.1f}%")
            cols[1].metric("Actual Costs", f"${row['Actual Costs']:,.0f}")
            cols[2].metric("Achieved Revenue", f"${row['Achieved Revenue']:,.0f}")
            cols[2].metric("Physical % Complete", f"{row['POC']*100:.1f}%")
            cols[3].metric("EAC", f"${row['EAC']:,.0f}")
            cols[3].metric("ETC", f"${row['ETC']:,.0f}")

            st.divider()

            st.metric("Total Float (Schedule Buffer)", f"{row['Total Float']} days")

    else:
        st.info("Select a country from the sidebar or click a **red** country on the map.")

# ────────────────────────────────────────────────
# Right panel – MAP (100% ORIGINAL)
# ────────────────────────────────────────────────
with right_col:
    st.subheader("Project Locations – Africa")

    fig = px.choropleth(
        map_data,
        locations='Country',
        locationmode='country names',
        color='Has Data',
        color_discrete_map={True: 'red', False: 'lightgrey'},
        scope='africa',
        hover_name='hover_text'
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
        clickmode='event+select',
        height=650
    )

    chart = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

    if chart and 'selection' in chart and chart['selection']:
        points = chart['selection'].get('points', [])
        if points:
            clicked_country = points[0].get('location')
            if clicked_country and clicked_country in data['Country'].values:
                st.session_state.selected_country = clicked_country

# ────────────────────────────────────────────────
# Footer
# ────────────────────────────────────────────────
st.markdown("---")
st.caption("Elsewedy Electric T&D – Project Control Dashboard • Minimal Live Glow Edition")
