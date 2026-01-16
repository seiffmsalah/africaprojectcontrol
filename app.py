import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ────────────────────────────────────────────────
# Page config
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="Elsewedy T&D Project Dashboard",
    layout="wide"
)

# ────────────────────────────────────────────────
# SAFE Styling + Red Live Glow (NO BREAKING CSS)
# ────────────────────────────────────────────────
st.markdown("""
<style>

/* Soft page fade-in */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}

.stApp {
    animation: fadeIn 0.6s ease-in-out;
}

/* Metric cards – red live glow */
@keyframes redGlow {
    0%   { box-shadow: 0 0 0 rgba(211,47,47,0.0); }
    50%  { box-shadow: 0 0 14px rgba(211,47,47,0.35); }
    100% { box-shadow: 0 0 0 rgba(211,47,47,0.0); }
}

[data-testid="stMetric"] {
    border-radius: 10px;
    padding: 12px;
    animation: redGlow 3.5s infinite;
    transition: transform 0.2s ease;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
}

/* Selected country title glow */
.country-glow {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 8px;
    animation: redGlow 2.8s infinite;
}

/* Donut chart container glow */
.plot-container {
    padding: 6px;
    border-radius: 14px;
    animation: redGlow 4s infinite;
}

</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# Logo
# ────────────────────────────────────────────────
st.markdown(
    """
    <div style="text-align:center; margin: 1.5rem 0 2rem 0;">
        <img src="https://logos-world.net/wp-content/uploads/2023/04/Elsewedy-Electric-Logo.png" width="380">
    </div>
    """,
    unsafe_allow_html=True
)

# ────────────────────────────────────────────────
# Country → ISO code (flags)
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

def get_flag(country):
    code = country_to_code.get(country)
    return ''.join(chr(ord(c)+127397) for c in code) if code else ""

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

# Map data
map_df = pd.DataFrame({"Country": countries})
map_df = map_df.merge(data, on="Country", how="left")
map_df["Has Data"] = ~map_df["Revenue"].isna()
map_df["hover_text"] = map_df.apply(
    lambda r: f"{r['Country']}<br>{'Has project data' if r['Has Data'] else 'No project data'}",
    axis=1
)

# ────────────────────────────────────────────────
# Session State
# ────────────────────────────────────────────────
if "selected_country" not in st.session_state:
    st.session_state.selected_country = None

# ────────────────────────────────────────────────
# Layout
# ────────────────────────────────────────────────
st.title("Elsewedy Electric T&D – Project Construction Dashboard")
st.markdown("Africa – Project Overview & Control")

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
# LEFT PANEL – DETAILS
# ────────────────────────────────────────────────
with left:
    if st.session_state.selected_country:
        row = data[data["Country"] == st.session_state.selected_country].iloc[0]
        flag = get_flag(st.session_state.selected_country)

        st.markdown(
            f"""
            <h3 class="country-glow">
                Project: {st.session_state.selected_country} {flag}
            </h3>
            """,
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

        for col, title, value, color in [
            (d1, "Planned Progress", row["Planned Progress"], "grey"),
            (d2, "Actual Progress", row["Actual Progress"], "#d32f2f")
        ]:
            pct = value * 100
            fig = go.Figure(go.Pie(
                values=[pct, 100-pct],
                hole=0.65,
                marker_colors=[color, "#f0f0f0"],
                textinfo="none"
            ))
            fig.update_layout(
                title=title,
                showlegend=False,
                height=280,
                paper_bgcolor="white",
                transition=dict(duration=600),
                annotations=[dict(text=f"{pct:.0f}%", x=0.5, y=0.5, font_size=38)]
            )

            col.markdown('<div class="plot-container">', unsafe_allow_html=True)
            col.plotly_chart(fig, use_container_width=True)
            col.markdown('</div>', unsafe_allow_html=True)

        st.metric("Total Float (Schedule Buffer)", f"{row['Total Float']} days")

    else:
        st.info("Select a country from the sidebar or click a **red** country on the map.")

# ────────────────────────────────────────────────
# RIGHT PANEL – MAP (UNCHANGED LOGIC)
# ────────────────────────────────────────────────
with right:
    st.subheader("Project Locations – Africa")

    fig = px.choropleth(
        map_df,
        locations="Country",
        locationmode="country names",
        color="Has Data",
        color_discrete_map={True: "red", False: "lightgrey"},
        scope="africa",
        hover_name="hover_text"
    )

    fig.update_traces(
        marker_line_width=0.8,
        marker_line_color="black",
        hovertemplate="%{hovertext}<extra></extra>"
    )

    fig.update_layout(
        height=650,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor="white",
        geo=dict(bgcolor="white"),
        clickmode="event+select"
    )

    chart = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

    if chart and "selection" in chart and chart["selection"]:
        pts = chart["selection"].get("points", [])
        if pts:
            clicked = pts[0].get("location")
            if clicked in data["Country"].values:
                st.session_state.selected_country = clicked

# ────────────────────────────────────────────────
# Footer
# ────────────────────────────────────────────────
st.markdown("---")
st.caption("Elsewedy Electric T&D – Project Control Dashboard • Live Glow Edition")
