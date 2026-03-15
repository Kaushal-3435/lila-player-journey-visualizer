import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import plotly.graph_objects as go
import os

# ── 1. Config ────────────────────────────────────────────────────────────────

st.title("LILA Player Journey Explorer")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MAP_IMAGES = {
    "AmbroseValley": os.path.join(BASE_DIR, "maps", "AmbroseValley_Minimap.png"),
    "GrandRift":     os.path.join(BASE_DIR, "maps", "GrandRift_Minimap.png"),
    "Lockdown":      os.path.join(BASE_DIR, "maps", "Lockdown_Minimap.jpg"),
}

MAP_CONFIG = {
    "AmbroseValley": {"scale": 900,  "origin_x": -370, "origin_z": -473},
    "GrandRift":     {"scale": 581,  "origin_x": -290, "origin_z": -290},
    "Lockdown":      {"scale": 1000, "origin_x": -500, "origin_z": -500},
}

map_id = st.selectbox("Select Map", list(MAP_IMAGES.keys()))
config = MAP_CONFIG[map_id]

# ── 2. Data Generation ───────────────────────────────────────────────────────

NUM_POINTS = 300

df = pd.DataFrame({
    "x":         np.random.randint(-500, 500, NUM_POINTS),
    "z":         np.random.randint(-500, 500, NUM_POINTS),
    "event":     np.random.choice(["kill", "death", "loot", "storm_death"], NUM_POINTS),
    "user_id":   np.random.choice(["playerA", "playerB", "playerC", "12345", "9999"], NUM_POINTS),
    "match_id":  np.random.choice(["match_1", "match_2", "match_3"], NUM_POINTS),
    "timestamp": np.random.randint(0, 500, NUM_POINTS),
})

df["player_type"] = df["user_id"].apply(
    lambda x: "Bot" if str(x).isdigit() else "Human"
)

# ── 3. Filters ───────────────────────────────────────────────────────────────

event_filter  = st.multiselect("Filter Events", df["event"].unique(),       default=list(df["event"].unique()))
player_filter = st.multiselect("Player Type",   df["player_type"].unique(), default=list(df["player_type"].unique()))
match         = st.selectbox("Select Match",    df["match_id"].unique())

df = df[df["event"].isin(event_filter)]
df = df[df["player_type"].isin(player_filter)]
df = df[df["match_id"] == match]

time_min, time_max = int(df["timestamp"].min()), int(df["timestamp"].max())
selected_time = st.slider("Timeline", time_min, time_max, time_max)
df = df[df["timestamp"] <= selected_time]

# ── 4. Coordinate Transform ──────────────────────────────────────────────────

df["u"]  = (df["x"] - config["origin_x"]) / config["scale"]
df["v"]  = (df["z"] - config["origin_z"]) / config["scale"]
df["px"] = df["u"] * 1024
df["py"] = (1 - df["v"]) * 1024

# ── 5. Visualization ─────────────────────────────────────────────────────────

img          = Image.open(MAP_IMAGES[map_id])
show_heatmap = st.checkbox("Show Heatmap")

fig = go.Figure()

fig.add_layout_image(dict(
    source=img, x=0, y=0, sizex=1024, sizey=1024,
    xref="x", yref="y", sizing="stretch", layer="below",
))

if show_heatmap:
    fig.add_trace(go.Histogram2d(
        x=df["px"], y=df["py"],
        colorscale="Hot", nbinsx=40, nbinsy=40,
    ))
else:
    fig.add_trace(go.Scatter(
        x=df["px"], y=df["py"],
        mode="markers",
        marker=dict(size=7, color="red"),
        text=df["event"], name="Events",
    ))

fig.update_yaxes(autorange="reversed")
fig.update_layout(width=900, height=900, title=f"Player Activity — {map_id}")

# ── 6. Output ────────────────────────────────────────────────────────────────

st.plotly_chart(fig)
fig.update_layout(width=900, height=900, title=f"Player Activity — {map_id}")

# ── 6. Output ────────────────────────────────────────────────────────────────

st.plotly_chart(fig)
