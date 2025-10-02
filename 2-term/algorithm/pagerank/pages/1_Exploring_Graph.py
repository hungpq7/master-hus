# app.py
import streamlit as st
import pandas as pd
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


# ----------------------
# 1) Table of pages
# ----------------------
st.subheader("Pages")
rows = []
for nid, attrs in NODES.items():
    rows.append({
        "pageid": nid,
        "page name": attrs["name"],
        "page topic(s)": ", ".join(attrs["topics"]) if attrs["topics"] else "(none)",
        "is_seed": nid in TRUSTRANK_GOOD_SEEDS
    })
df_nodes = pd.DataFrame(rows).sort_values("pageid").reset_index(drop=True)
st.dataframe(df_nodes, use_container_width=True)

# ----------------------
# 2) Graph (Graphviz)
# ----------------------
st.subheader("Link Graph (nodes labeled by pageid)")
dot = Digraph(graph_attr={"rankdir": "LR", "fontsize": "12", "labelloc":"t", "label": "Toy Web Graph"})
dot.attr("node", shape="circle", style="filled", fontname="Helvetica", fontsize='14')

for nid, a in NODES.items():
    # color scheme: green = TrustRank seed, red = spam, lightgray = normal
    fill = "#b7e1cd" if nid in TRUSTRANK_GOOD_SEEDS else ("#f4c7c3" if a["is_spam"] else "#e5e5e5")
    # label by pageid; add name in tooltip-like comment via xlabel for readability
    label = nid
    xlabel = a["name"]
    dot.node(nid, label=label, fillcolor=fill, xlabel=xlabel)

for u, v, w in EDGES:
    if show_edge_weights:
        dot.edge(u, v, label=str(w))
    else:
        dot.edge(u, v)

st.graphviz_chart(dot, use_container_width=True)

# ----------------------
# 3) Topic teleport
# ----------------------
st.subheader("Topic-Sensitive Teleport Distribution")
col1, col2 = st.columns([1, 2])
with col1:
    topic_choice = st.sidebar.selectbox("Topic teleport to view", list(TOPIC_TELEPORT.keys()), index=0)
    st.markdown(f"**Topic:** `{topic_choice}`")
with col2:
    tp_series = pd.Series(TOPIC_TELEPORT[topic_choice]).sort_values(ascending=False)
    st.bar_chart(tp_series)

st.caption("Seeds for TrustRank are highlighted in green; spam pages in red. Edge labels (optional) show weights for Weighted PageRank.")
