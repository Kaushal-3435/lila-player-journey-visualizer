import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import plotly.graph_objects as go

st.title("LILA Player Journey Explorer")

# -----------------------------
# Map images
# -----------------------------

MAP_IMAGES = {
    "AmbroseValley": "AmbroseValley_Minimap.png",
    "GrandRift": "GrandRift_Minimap.png",
    "Lockdown": "Lockdown_Minimap.jpg"
}

# -----------------------------
# Map configs
# -----------------------------

MAP_CONFIG = {
    "AmbroseValley": {"scale":900,"origin_x":-370,"origin_z":-473},
    "GrandRift": {"scale":581,"origin_x":-290,"origin_z":-290},
    "Lockdown": {"scale":1000,"origin_x":-500,"origin_z":-500}
}

# -----------------------------
# Map selector
# -----------------------------

map_id = st.selectbox("Select Map", list(MAP_IMAGES.keys()))

# -----------------------------
# Generate sample gameplay data
# -----------------------------

num_points = st.slider("Number of player events", 100, 2000, 500)

df = pd.DataFrame({
    "x": np.random.uniform(-500,500,num_points),
    "z": np.random.uniform(-500,500,num_points),
    "event": np.random.choice(["kill","death","loot","storm"],num_points),
    "player_type": np.random.choice(["Human","Bot"],num_points)
})

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
# Coordinate conversion
# -----------------------------

config = MAP_CONFIG[map_id]

df["u"] = (df["x"] - config["origin_x"]) / config["scale"]
df["v"] = (df["z"] - config["origin_z"]) / config["scale"]

df["px"] = df["u"] * 1024
df["py"] = (1 - df["v"]) * 1024

# -----------------------------
# Load map image
# -----------------------------

img = Image.open(MAP_IMAGES[map_id])

# -----------------------------
# Heatmap toggle
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
            marker=dict(size=6,color="red"),
            text=df["event"]
        )
    )

fig.update_yaxes(autorange="reversed")

fig.update_layout(
    width=900,
    height=900,
    title=f"Player Activity — {map_id}"
)

st.plotly_chart(fig)
