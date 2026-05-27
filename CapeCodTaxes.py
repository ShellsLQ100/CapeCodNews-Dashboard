#CapeCodNews Taxes and Rates Simulation
# Cape Cod Town Dashboard Simulation
# Run with: streamlit run app.py

import pandas as pd
import streamlit as st
import plotly.express as px
from zipcodes import matching


st.set_page_config(page_title="Cape Cod Town Dashboard", layout="wide")

st.title("Cape Cod Town Dashboard Simulation")
st.write(
    "Simulation using 2024 population as the baseline and 2026 mil rate as the current rate. "
    "Use the sliders to test possible population and mil rate changes."
)

# Load data
df = pd.read_csv("Cape Cod Dashboard - Towns.csv", header=1)

# Rename first column
df = df.rename(columns={df.columns[0]: "Town"})

# Load ZIP code file
zip_df = pd.read_csv("Cape Cod Dashboard - Zip Codes.csv")


# Rename for matching
zip_df = zip_df.rename(columns={"Town Location": "Town"})

# Keep useful columns
df = df[["Town", "Population (2024)", "Mil Rate (2026)", "Form of Government"]].copy()

# Clean numbers
df["Population (2024)"] = (
    df["Population (2024)"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .astype(float)
)

df["Mil Rate (2026)"] = (
    df["Mil Rate (2026)"]
    .astype(str)
    .str.replace("%", "", regex=False)
    .astype(float)
)

# Keep only the MAIN ZIP per town
main_zip_map = {
    "Barnstable": "02601",
    "Bourne": "02532",
    "Brewster": "02631",
    "Chatham": "02633",
    "Dennis": "02638",
    "Eastham": "02642",
    "Falmouth": "02540",
    "Harwich": "02645",
    "Mashpee": "02649",
    "Orleans": "02653",
    "Provincetown": "02657",
    "Sandwich": "02563",
    "Truro": "02666",
    "Wellfleet": "02667",
    "Yarmouth": "02664"
}

main_zip_df = pd.DataFrame(
    list(main_zip_map.items()),
    columns=["Town", "Zip Code"]
)

# Merge ZIPs into main dataset
df = df.merge(main_zip_df, on="Town", how="left")

# Convert ZIP codes into latitude/longitude

def get_lat(zip_code):
    result = matching(str(zip_code))
    if result:
        return float(result[0]["lat"])
    return None

def get_lon(zip_code):
    result = matching(str(zip_code))
    if result:
        return float(result[0]["long"])
    return None

df["Latitude"] = df["Zip Code"].apply(get_lat)
df["Longitude"] = df["Zip Code"].apply(get_lon)

# Sidebar simulation controls
st.sidebar.header("2024 to 2026 Simulation Controls")

pop_change = st.sidebar.slider(
    "Population change from 2024 to 2026 (%)",
    min_value=-10.0,
    max_value=15.0,
    value=1.0,
    step=0.5
)

mil_rate_change = st.sidebar.slider(
    "Mil rate adjustment from current 2026 rate (%)",
    min_value=-20.0,
    max_value=30.0,
    value=0.0,
    step=0.5
)

# Simulated 2026 values
df["Simulated Population (2026)"] = (
    df["Population (2024)"] * (1 + pop_change / 100)
)

df["Adjusted Mil Rate (2026)"] = (
    df["Mil Rate (2026)"] * (1 + mil_rate_change / 100)
)

# Combined simulation index
df["2024 Baseline Index"] = (
    df["Population (2024)"] * df["Mil Rate (2026)"]
)

df["2026 Simulated Index"] = (
    df["Simulated Population (2026)"] * df["Adjusted Mil Rate (2026)"]
)

# Metric cards
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total 2024 Population",
    f"{df['Population (2024)'].sum():,.0f}"
)

col2.metric(
    "Simulated 2026 Population",
    f"{df['Simulated Population (2026)'].sum():,.0f}"
)

col3.metric(
    "Current 2026 Mil Rate",
    f"{df['Mil Rate (2026)'].mean():.2f}%"
)

col4.metric(
    "Adjusted 2026 Mil Rate",
    f"{df['Adjusted Mil Rate (2026)'].mean():.2f}%"
)

st.divider()

# Cape Cod map visualization
st.subheader("Cape Cod Town Map")

map_metric = st.selectbox(
    "Choose what controls the circle size:",
    [
        "Population (2024)",
        "Mil Rate (2026)",
        "Simulated Population (2026)",
        "Adjusted Mil Rate (2026)"
    ]
)

color_metric = st.selectbox(
    "Choose what controls the darker/lighter tone:",
    [
        "Mil Rate (2026)",
        "Adjusted Mil Rate (2026)",
        "Population (2024)",
        "Simulated Population (2026)"
    ]
)

fig_map = px.scatter_mapbox(
    df,
    lat="Latitude",
    lon="Longitude",
    size=map_metric,
    color=color_metric,
    hover_name="Town",
    hover_data={
        "Population (2024)": ":,.0f",
        "Simulated Population (2026)": ":,.0f",
        "Mil Rate (2026)": ":.2f",
        "Adjusted Mil Rate (2026)": ":.2f",
        "Latitude": False,
        "Longitude": False
    },
    zoom=8.3,
    height=600,
    title="Cape Cod Town Comparison Map",
    mapbox_style="carto-positron"
)

fig_map.update_layout(
    margin={"r":0,"t":40,"l":0,"b":0}
)

st.plotly_chart(fig_map, use_container_width=True)

# Charts
left, right = st.columns(2)

with left:
    fig_pop = px.bar(
        df.sort_values("Population (2024)", ascending=False),
        x="Town",
        y="Population (2024)",
        title="2024 Population by Town"
    )
    st.plotly_chart(fig_pop, use_container_width=True)

with right:
    fig_mil = px.bar(
        df.sort_values("Mil Rate (2026)", ascending=True),
        x="Mil Rate (2026)",
        y="Town",
        orientation="h",
        title="2026 Mil Rate by Town"
    )

    fig_mil.update_layout(
        yaxis_title="Town",
        xaxis_title="Mil Rate (2026)"
    )

    st.plotly_chart(fig_mil, use_container_width=True)

left2, right2 = st.columns(2)

with left2:
    fig_sim_pop = px.bar(
        df.sort_values("Simulated Population (2026)", ascending=False),
        x="Town",
        y="Simulated Population (2026)",
        title="Simulated 2026 Population by Town"
    )
    st.plotly_chart(fig_sim_pop, use_container_width=True)

with right2:
    fig_sim_index = px.scatter(
        df,
        x="Simulated Population (2026)",
        y="Adjusted Mil Rate (2026)",
        size="2026 Simulated Index",
        hover_name="Town",
        color="Form of Government",
        title="2026 Simulated Population vs. Mil Rate"
    )
    st.plotly_chart(fig_sim_index, use_container_width=True)

st.divider()

st.subheader("Town-Level Simulation Table")
st.dataframe(df, use_container_width=True)

