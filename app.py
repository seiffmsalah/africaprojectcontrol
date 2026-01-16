import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ────────────────────────────────────────────────
# Page config + forced readable styling
# ────────────────────────────────────────────────
st.set_page_config(page_title="Project Construction Dashboard", layout="wide")

st.markdown("""
    <style>
    /* Force white background */
    .stApp, .main, .block-container {
        background-color: white !important;
    }

    /* Make ALL text dark by default */
    body, div, span, p, h1, h2, h3, h4, h5, h6, label, .stMarkdown, .stText, 
    .stExpander, .stSidebar, .stSelectbox, .stSlider, .stNumberInput {
        color: #1a1a1a !important;          /* very dark grey-black */
    }

    /* Metrics - big numbers & labels */
    .stMetric label, .stMetric .metric-value {
        color: black !important;
    }
    .stMetric .metric-delta {
        color: #b22222 !important;          /* red for delta if used */
    }

    /* Progress bars */
    .stProgress > div > div > div {
        background-color: #d32f2f !important;   /* nice visible red */
    }
    .stProgress > div {
        background-color: #e0e0e0 !important;   /* light grey track */
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
        color: black !important;
    }

    /* Make sure headers & titles are very visible */
    h1, h2, h3 {
        color: black !important;
    }
    </style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# Sample data (same as before)
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

np.random.seed(42)  # for reproducibility during testing
selected_countries = np.random.choice(african_countries, size=12, replace=False)
data = pd.DataFrame({
    'Country': selected_countries,
    'Revenue': np.random.randint(1200000, 6200000, size=12),
    'Budget Cost': np.random.randint(900000, 4800000, size=12),
    'Actual Costs': np.random.randint(600000, 3800000, size=12),
    'Achieved Revenue': np.random.randint(500000, 3200000, size=12),
    'POC': np.random.uniform(0.15, 0.92, size=12),
    'Planned Progress': np.random.uniform(0.25, 0.98, size=12),
    'Actual Progress': np.random.uniform(0.10, 0.89, size=12),
    'Total Float': np.random.randint(5, 120, size=12)
})

data['GP%'] = ((data['Revenue'] - data['Budget Cost']) / data['Revenue']) * 100
data['EAC'] = data['Budget Cost'] / np.maximum(data['POC'], 0.01)  # avoid div by zero
data['ETC'] = data['EAC'] - data['Actual Costs']

# Full map data
map_data = pd.DataFrame({'Country': african_countries})
map_data = map_data.merge(data, on='Country', how='left')
map_data['Has Data'] = ~map_data['Revenue'].isna()

# ────────────────────────────────────────────────
# UI
# ────────────────────────────────────────────────
st.title("Project Construction Dashboard")
st.markdown("Africa – Construction Project Overview", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Controls")
selected_country = st.sidebar.selectbox(
    "Select Country / Project",
    options=["(All)"] + sorted(data['Country'].unique().tolist())
)

# ───── Interactive Map ─────
st.subheader("Project Locations – Africa")
fig = px.choropleth(
    map_data,
    locations='Country',
    locationmode='country names',
    color='Has Data',
    color_discrete_map={True: 'red', False: 'lightgrey'},
    scope='africa',
    hover_name='Country',
    hover_data={
        'Revenue': ':,.0f',
        'Budget Cost': ':,.0f',
        'Has Data': False
    }
)
fig.update_layout(
    coloraxis_showscale=False,
    margin=dict(r=0, t=30, l=0, b=0),
    paper_bgcolor='white',
    geo=dict(bgcolor='white')
)

# Highlight selected country
if selected_country != "(All)":
    sel = map_data[map_data['Country'] == selected_country]
    fig.add_trace(px.choropleth(
        sel,
        locations='Country',
        locationmode='country names',
        color_discrete_sequence=['black'],
        scope='africa'
    ).data[0])

st.plotly_chart(fig, use_container_width=True)

# ───── Detail view ─────
if selected_country == "(All)":
    st.info("Select a country from the sidebar to see detailed metrics.")
else:
    row = data[data['Country'] == selected_country].iloc[0]

    st.subheader(f"Project: {selected_country}")

    cols = st.columns([1,1,1,1])
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
        st.metric("Estimate at Completion", f"${row['EAC']:,.0f}")
        st.metric("Estimate to Complete", f"${row['ETC']:,.0f}")

    st.divider()

    # Progress comparison
    st.subheader("Progress Comparison")
    prog_cols = st.columns([2, 3])

    with prog_cols[0]:
        st.caption("Planned vs Actual Progress")
        st.progress(row['Planned Progress'], text=f"Planned: {row['Planned Progress']*100:.0f}%")
        st.progress(row['Actual Progress'], text=f"Actual:   {row['Actual Progress']*100:.0f}%")

    with prog_cols[1]:
        df_prog = pd.DataFrame({
            'Category': ['Planned Progress', 'Actual Progress'],
            'Value': [row['Planned Progress'], row['Actual Progress']]
        })
        bar = px.bar(
            df_prog,
            x='Category',
            y='Value',
            color='Category',
            color_discrete_map={'Planned Progress': 'grey', 'Actual Progress': 'red'},
            text_auto='.0%'
        )
        bar.update_layout(
            yaxis_tickformat='.0%',
            showlegend=False,
            paper_bgcolor='white',
            plot_bgcolor='white',
            height=320,
            margin=dict(l=20, r=20, t=10, b=60)
        )
        st.plotly_chart(bar, use_container_width=True)

    st.divider()

    st.metric("Total Float (Schedule Buffer)", f"{row['Total Float']} days", delta_color="normal")

    # What-if slider
    st.subheader("What-If Analysis")
    adj_poc = st.slider("Simulate different % Complete", 1, 100, int(row['POC']*100), format="%d%%") / 100
    adj_eac = row['Budget Cost'] / max(adj_poc, 0.01)
    adj_etc = adj_eac - row['Actual Costs']
    st.metric("Adjusted EAC", f"${adj_eac:,.0f}")
    st.metric("Adjusted ETC", f"${adj_etc:,.0f}")
