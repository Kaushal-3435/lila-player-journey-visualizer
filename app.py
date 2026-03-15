import streamlit as st
import pandas as pd
import pyarrow.parquet as pq
import os
from PIL import Image
import plotly.graph_objects as go

st.title("LILA Player Journey Explorer")

DATA_FOLDER = "player_data"

MAP_IMAGES = {
    "AmbroseValley": "AmbroseValley_Minimap.png",
    "GrandRift": "GrandRift_Minimap.png",
    "Lockdown": "Lockdown_Minimap.jpg"
}

MAP_CONFIG = {
    "AmbroseValley": {"scale":900,"origin_x":-370,"origin_z":-473},
    "GrandRift": {"scale":581,"origin_x":-290,"origin_z":-290},
    "Lockdown": {"scale":1000,"origin_x":-500,"origin_z":-500}
}

# -----------------------------
# Load data
# -----------------------------

if not os.path.exists(DATA_FOLDER):
    st.error("player_data folder not found")
    st.stop()

days = os.listdir(DATA_FOLDER)

if len(days) == 0:
    st.error("No data inside player_data folder")
    st.stop()

day = st.selectbox("Select Day", days)

files = os.listdir(os.path.join(DATA_FOLDER, day))

if len(files) == 0:
    st.error("No player files found")
    st.stop()

file = st.selectbox("Select Player File", files)

path = os.path.join(DATA_FOLDER, day, file)

table = pq.read_table(path)
df = table.to_pandas()

# decode event names
df["event"] = df["event"].apply(lambda x: x.decode("utf-8") if isinstance(x, bytes) else x)

# identify bots vs humans
df["player_type"] = df["user_id"].apply(lambda x: "Bot" if str(x).isdigit() else "Human")

# -----------------------------
# Filters
# -----------------------------

event_filter = st.multiselect(
    "Filter Events",
    df["event"].unique(),
    default=df["event"].unique()
)

player_filter = st.multiselect(
    "Player Type",
    df["player_type"].unique(),
    default=df["player_type"].unique()
)

df = df[df["event"].isin(event_filter)]
df = df[df["player_type"].isin(player_filter)]

# -----------------------------
# Match Filter
# -----------------------------

matches = df["match_id"].unique()
match = st.selectbox("Select Match", matches)

df = df[df["match_id"] == match]

# -----------------------------
# Optional Timeline
# -----------------------------

if "timestamp" in df.columns:

    time_min = int(df["timestamp"].min())
    time_max = int(df["timestamp"].max())

    selected_time = st.slider(
        "Timeline",
        time_min,
        time_max,
        time_max
    )

    df = df[df["timestamp"] <= selected_time]

# -----------------------------
# Map Setup
# -----------------------------

map_id = df["map_id"].iloc[0]

config = MAP_CONFIG[map_id]

# convert world coords → map coords
df["u"] = (df["x"] - config["origin_x"]) / config["scale"]
df["v"] = (df["z"] - config["origin_z"]) / config["scale"]

df["px"] = df["u"] * 1024
df["py"] = (1 - df["v"]) * 1024

img = Image.open(MAP_IMAGES[map_id])

# -----------------------------
# Heatmap Toggle
# -----------------------------

show_heatmap = st.checkbox("Show Heatmap")

# -----------------------------
# Visualization
# -----------------------------

fig = go.Figure()

fig.add_layout_image(
    dict(
        source=img,
        x=0,
        y=0,
        sizex=1024,
        sizey=1024,
        xref="x",
        yref="y",
        sizing="stretch",
        layer="below"
    )
)

if show_heatmap:

    fig.add_trace(
        go.Histogram2d(
            x=df["px"],
            y=df["py"],
            colorscale="Hot",
            nbinsx=40,
            nbinsy=40
        )
    )

else:

    fig.add_trace(
        go.Scatter(
            x=df["px"],
            y=df["py"],
            mode="markers",
            marker=dict(
                size=7,
                color="red"
            ),
            text=df["event"],
            name="Events"
        )
    )

fig.update_yaxes(autorange="reversed")

fig.update_layout(
    width=900,
    height=900,
    title=f"Player Activity — {map_id}"
)

st.plotly_chart(fig)
