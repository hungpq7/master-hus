# app.py
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from graphviz import Digraph

st.set_page_config(page_title="PR Variants — Toy Graph", layout="wide")

# ----------------------
# Data (from our toy set)
# ----------------------
NODES = {
    "A": {"name": "TechBlog",     "topics": ["Tech"],                    "is_spam": False},
    "B": {"name": "TechForum",    "topics": ["Tech"],                    "is_spam": False},
    "C": {"name": "SearchEngine", "topics": ["Tech","Sports"],           "is_spam": False},
    "D": {"name": "SportsNews",   "topics": ["Sports"],                  "is_spam": False},
    "E": {"name": "SportsForum",  "topics": ["Sports"],                  "is_spam": False},
    "F": {"name": "CookingBlog",  "topics": ["Cooking"],                 "is_spam": False},
    "G": {"name": "CheapPills",   "topics": [],                          "is_spam": True},
    "H": {"name": "Casino",       "topics": [],                          "is_spam": True},
    "I": {"name": "University",   "topics": ["Tech"],                    "is_spam": False},
    "J": {"name": "Wikipedia",    "topics": ["Tech","Sports","Cooking"], "is_spam": False},
}

EDGES = [
    ("A","B",5), ("A","C",2), ("A","J",1),
    ("B","A",3), ("B","C",2), ("B","G",1),
    ("C","A",2), ("C","D",2), ("C","J",4), ("C","I",3),
    ("D","E",4), ("D","C",1), ("D","J",2),
    ("E","D",2), ("E","C",1), ("E","H",1),
    ("F","C",1), ("F","J",3),
    ("G","C",1), ("G","H",2), ("G","A",1),
    ("H","G",2), ("H","C",1),
    ("I","C",3), ("I","J",5),
    ("J","A",2), ("J","D",2), ("J","F",1), ("J","I",3),
]

TOPIC_TELEPORT = {
    "Tech":    {"A":0.25, "B":0.25, "C":0.20, "I":0.15, "J":0.15},
    "Sports":  {"D":0.35, "E":0.25, "C":0.20, "J":0.20},
    "Cooking": {"F":0.60, "J":0.40},
    "General": {"J":0.50, "C":0.30, "I":0.20},
}

TRUSTRANK_GOOD_SEEDS = ["I", "J", "D"]

# ----------------------
# Sidebar controls
# ----------------------
st.sidebar.header("Controls")
show_edge_weights = st.sidebar.checkbox("Show edge weights", value=True)
use_topic_teleport = st.sidebar.checkbox("Use topic teleport", value=True)
alpha = st.sidebar.slider("Damping factor ($\\alpha$)", 0.0, 1.0, 0.85, 0.01)
topic_choice = st.sidebar.selectbox("Topic teleport to view", list(TOPIC_TELEPORT.keys()), index=0)

# Build ordered node list and indices
node_ids = sorted(NODES.keys())
idx = {n: i for i, n in enumerate(node_ids)}
n = len(node_ids)

# Weighted adjacency A (rows: from, cols: to)
A = np.zeros((n, n), dtype=float)
for u, v, w in EDGES:
    A[idx[u], idx[v]] += float(w)

# Row-normalized transition P (uniform row if dangling)
row_sums = A.sum(axis=1, keepdims=True)
P = np.where(row_sums > 0, A / row_sums, 1.0 / n)

# Topic teleport vector v (falls back to uniform if empty)
v = np.zeros(n, dtype=float)
if use_topic_teleport:
    for node, prob in TOPIC_TELEPORT.get(topic_choice, {}).items():
        v[idx[node]] = prob
    if v.sum() == 0:
        v[:] = 1.0 / n
    else:
        v /= v.sum()
else:
    v[:] = 1.0 / n


# Google matrix G(α) = αP + (1-α) 1 v^T
G = alpha * P + (1 - alpha) * np.outer(np.ones(n), v)
df_G = pd.DataFrame(G, index=node_ids, columns=node_ids).round(2)

# ----------------------
# 1) Table of pages
# ----------------------
st.subheader("Pages")
rows = []
for nid, attrs in NODES.items():
    rows.append({
        "PageID": nid,
        "PageName": attrs["name"],
        "PageTopic": ", ".join(attrs["topics"]) if attrs["topics"] else "",
        "SeedPage": nid in TRUSTRANK_GOOD_SEEDS
    })
df_nodes = pd.DataFrame(rows).sort_values("PageID").reset_index(drop=True)
st.dataframe(df_nodes, use_container_width=False)

# ----------------------
# 2) Graph (Graphviz)
# ----------------------
st.subheader("Link Graph")
dot = Digraph(graph_attr={"rankdir": "LR", "fontsize": "12", "labelloc":"t", "label": "Toy Web Graph"})
dot.attr("node", shape="circle", style="filled", fontname="Helvetica", fontsize='14')

for nid, a in NODES.items():
    # color scheme: green = TrustRank seed, red = spam, lightgray = normal
    fill = "#b7e1cd" if nid in TRUSTRANK_GOOD_SEEDS else ("#f4c7c3" if a["is_spam"] else "#e5e5e5")
    # label by page_id; add name in tooltip-like comment via xlabel for readability
    label = nid
    xlabel = a["name"]
    dot.node(nid, label=label, fillcolor=fill, xlabel=xlabel)

for u, v, w in EDGES:
    if show_edge_weights:
        dot.edge(u, v, label=str(w))
    else:
        dot.edge(u, v)

st.graphviz_chart(dot, use_container_width=True)
st.caption("Seeds for TrustRank are highlighted in green; spam pages in red. Edge labels (optional) show weights for Weighted PageRank.")

# ----------------------
# 3) Adjacency, Transition, Google Matrices
# ----------------------
st.subheader("Topic-Sensitive Teleport & Damped Transition Matrix")

left, right = st.columns([2, 3])
with left:
    st.markdown(f"**Topic teleport:** `{topic_choice}`")
    # Build series in node order for consistent labeling
    tp_series = pd.Series(
        {n: TOPIC_TELEPORT.get(topic_choice, {}).get(n, 0.0) for n in node_ids}
    ).reindex(node_ids).fillna(0.0)

    df_tp = tp_series.rename("probability").reset_index().rename(columns={"index": "node"})

    fig = px.pie(
        df_tp, values="probability", names="node",
        title="Teleport distribution",
        hole=0.0
    )
    # Show percentages on slices; keep a clean hover
    fig.update_traces(
        textposition="inside",
        texttemplate="%{percent}",
        hovertemplate="Node %{label}<br>p=%{value:.2f}<extra></extra>"
    )
    fig.update_layout(showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown("**Heatmap**")
    palette = sns.diverging_palette(20, 220, n=20)[10:]  # per your spec
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        df_G.astype(float), square=True, annot=True,
        cmap=palette, vmin=0, vmax=1, cbar=True, ax=ax,
        fmt=".0%", linewidths=0.5, linecolor="white"
    )
    ax.set_xlabel("To")
    ax.set_ylabel("From")
    st.pyplot(fig, clear_figure=True, dpi=500)
