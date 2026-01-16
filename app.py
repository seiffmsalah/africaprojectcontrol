import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import time

# ────────────────────────────────────────────────
# Page config
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="Elsewedy T&D Project Dashboard",
    layout="wide"
)

# ────────────────────────────────────────────────
# Styling + Animations
# ────────────────────────────────────────────────
st.markdown("""
<style>

/* Page fade-in */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

.stApp {
    animation: fadeIn 0.8s ease-in-out;
    background: linear-gradient(120deg, #ffffff, #f7f7f7, #ffffff);
    background-size: 300% 300%;
    animation: gradientMove 18s ease infinite;
}

/* Subtle background motion */
@keyframes gradientMove {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Typography */
body, div, span, p, h1, h2, h3, h4, h5, h6, label {
    color: #1a1a1a !important;
}

/* Metric cards */
[data-testid="stMetric"] {
    background-color: white;
    border-radius: 12px;
    padding: 14px;
    animation: fadeIn 0.6s ease-in-out;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 22px rgba(0,0,0,0.08);
}

/* Progress bar */
.stProgress > div > div > div {
    background-color: #d32f2f !important;
}
.stProgress > div {
    background-color: #e0e0e0 !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #f8f9fa !important;
}

/* Logo */
.logo-container {
    text-align: center;
    margin: 1.5rem 0 2rem 0;
}
.logo-container img {
    max-width: 400px;
}

/* Flag pulse */
.country-flag {
    font-size: 2.2rem;
    margin-left: 0.5rem;
    animation: pulse 2.5s infinite;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.6; }
    100% { opacity: 1; }
}

</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# Logo
# ────────────────────────────────────────────────
st.markdown(
    '<div class="logo-container">'
    '<img src="https://logos-world.net/wp-content/uploads/2023/04/Elsewedy-Electric-Logo.png">'
    '</div>',
    unsafe_allow_html=True
)

# ────────────────────────────────────────────────
# Country flags
# ────────────────────────────────────────────────
country_to_code = {
    'Algeria': 'DZ', 'Angola': 'AO', 'Benin': 'BJ', 'Botswana': 'BW',
    'Burkina Faso': 'BF', 'Burundi': 'BI', 'Cameroon': 'CM', 'Cape Verde': 'CV',
    'Central African Republic': 'CF', 'Chad': 'TD', 'Comoros': 'KM',
    'Democratic Republic of the Congo': 'CD', 'Republic of Congo': 'CG',
    'Djibouti': 'DJ', 'Egypt': 'EG', 'Equatorial Guinea': 'GQ', 'Eritrea': 'ER',
    'Eswatini': 'SZ', 'Ethiopia': 'ET', 'Gabon': 'GA', 'Gambia': 'GM',
    'Ghana': 'GH', 'Guinea': 'GN', 'Guinea-Bissau': 'GW', 'Ivory Coast': 'CI',
    'Kenya': 'KE', 'Lesotho': 'LS', 'Liberia': 'LR', 'Libya': 'LY',
    'Madagascar': 'MG', 'Malawi': 'MW', 'Mali': 'ML', 'Mauritania': 'MR',
    'Mauritius': 'MU', 'Morocco': 'MA', 'Mozambique': 'MZ', 'Namibia': 'NA',
    'Niger': 'NE', 'Nigeria': 'NG', 'Rwanda': 'RW', 'Sao Tome and Principe': 'ST',
    'Senegal': 'SN', 'Seychelles': 'SC', 'Sierra Leone': 'SL', 'Somalia': 'SO',
    'South Africa': 'ZA', 'South Sudan': 'SS', 'Sudan': 'SD', 'Tanzania': 'TZ',
    'Togo': 'TG', 'Tunisia': 'TN', 'Uganda': 'UG', 'Zambia': 'ZM', 'Zimbabwe': 'ZW'
}

def get_flag_emoji(country):
    code = country_to_code.get(country)
    return ''.join(chr(ord(c) + 0x1F1E6 - ord('A')) for c in code) if code else ""

# ────────────────────────────────────────────────
# Sample Data
# ────────────────────────────────────────────────
np.random.seed(42)
countries = list(country_to_code.keys())
selected = np.random.choice(countries, 15, replace=False)

data = pd.DataFrame({
    "Country": selected,
    "Revenue": np.random.randint(1_200_000, 7_200_000, 15),
    "Budget Cost": np.random.randint(900_000, 5_500_000, 15),
    "Actual Costs": np.random.randint(600_000, 4_200_000, 15),
    "Achieved Revenue": np.random.randint(500_000, 3_800_000, 15),
    "POC": np.random.uniform(0.15, 0.95, 15),
    "Planned Progress": np.random.uniform(0.25, 0.99, 15),
    "Actual Progress": np.random.uniform(0.10, 0.92, 15),
    "Total Float": np.random.randint(5, 140, 15)
})

data["GP%"] = (data["Revenue"] - data["Budget Cost"]) / data["Revenue"] * 100
data["EAC"] = data["Budget Cost"] / np.maximum(data["POC"], 0.01)
data["ETC"] = data["EAC"] - data["Actual Costs"]

# ────────────────────────────────────────────────
# Session state
# ────────────────────────────────────────────────
if "selected_country" not in st.session_state:
    st.session_state.selected_country = None

# ────────────────────────────────────────────────
# Layout
# ────────────────────────────────────────────────
st.title("Elsewedy Electric T&D – Project Construction Dashboard")
st.markdown("**Africa – Project Overview & Control**")

left, right = st.columns([6, 4])

# ────────────────────────────────────────────────
# Sidebar
# ────────────────────────────────────────────────
st.sidebar.title("Controls")

choice = st.sidebar.selectbox(
    "Jump to Country / Project",
    ["(Click map or select)"] + sorted(data["Country"].tolist())
)

if choice != "(Click map or select)":
    st.session_state.selected_country = choice

if st.sidebar.button("Clear Selection"):
    st.session_state.selected_country = None
    st.rerun()

# ────────────────────────────────────────────────
# Left Panel
# ────────────────────────────────────────────────
with left:
    if st.session_state.selected_country:
        row = data[data["Country"] == st.session_state.selected_country].iloc[0]
        flag = get_flag_emoji(st.session_state.selected_country)

        st.markdown(
            f"### Project: {st.session_state.selected_country} "
            f"<span class='country-flag'>{flag}</span>",
            unsafe_allow_html=True
        )

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Revenue", f"${row['Revenue']:,.0f}")
        c1.metric("Budget Cost", f"${row['Budget Cost']:,.0f}")
        c2.metric("Gross Profit %", f"{row['GP%']:.1f}%")
        c2.metric("Actual Costs", f"${row['Actual Costs']:,.0f}")
        c3.metric("Achieved Revenue", f"${row['Achieved Revenue']:,.0f}")
        c3.metric("Physical % Complete", f"{row['POC']*100:.1f}%")
        c4.metric("EAC", f"${row['EAC']:,.0f}")
        c4.metric("ETC", f"${row['ETC']:,.0f}")

        st.divider()
        st.subheader("Project Progress")

        d1, d2 = st.columns(2)

        for label, value, color, col in [
            ("Planned Progress", row["Planned Progress"], "grey", d1),
            ("Actual Progress", row["Actual Progress"], "#d32f2f", d2)
        ]:
            pct = value * 100
            fig = go.Figure(go.Pie(
                values=[pct, 100 - pct],
                hole=0.65,
                marker_colors=[color, "#f0f0f0"],
                textinfo="none"
            ))
            fig.update_layout(
                title=label,
                showlegend=False,
                height=280,
                transition=dict(duration=800, easing="cubic-in-out"),
                annotations=[dict(text=f"{pct:.0f}%", x=0.5, y=0.5, font_size=38)]
            )
            col.plotly_chart(fig, use_container_width=True)

        st.subheader("Construction Progress")
        bar = st.progress(0)
        for i in range(int(row["Actual Progress"] * 100) + 1):
            bar.progress(i / 100)
            time.sleep(0.01)

    else:
        st.info("Select a country from the sidebar or click a **red** country on the map.")

# ────────────────────────────────────────────────
# Right Panel – Map
# ────────────────────────────────────────────────
with right:
    map_df = pd.DataFrame({"Country": countries})
    map_df["Has Data"] = map_df["Country"].isin(data["Country"])

    fig = px.choropleth(
        map_df,
        locations="Country",
        locationmode="country names",
        color="Has Data",
        color_discrete_map={True: "red", False: "lightgrey"},
        scope="africa"
    )

    fig.update_layout(
        height=650,
        margin=dict(l=0, r=0, t=30, b=0),
        transition=dict(duration=600)
    )

    st.plotly_chart(fig, use_container_width=True)

# ────────────────────────────────────────────────
# Footer
# ────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "Elsewedy Electric T&D – Project Control Dashboard • "
    "Sample Data • Executive Animated Version"
)
