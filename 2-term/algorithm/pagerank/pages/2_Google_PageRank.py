# pages/02_Power_Iteration_PageRank.py
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import networkx as nx
import plotly.graph_objects as go


st.set_page_config(page_title="Power Iteration — PageRank", layout="wide")

# ----------------------
# Tiny demo graph (unweighted PageRank)
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
    "Cooking": {"F":0.80, "J":0.20},
    "General": {"J":0.50, "C":0.30, "I":0.20},
}

TRUSTRANK_GOOD_SEEDS = ["I", "J", "D"]

# Order nodes, build index maps
NODE_IDS = sorted(NODES.keys())
IDX = {n:i for i,n in enumerate(NODE_IDS)}
n = len(NODE_IDS)


# ----------------------
# Sidebar: configuration
# ----------------------
st.sidebar.header("Controls")

# st.sidebar.write("----")

use_damping_factor = st.sidebar.checkbox("Use damping factor", value=False)
if use_damping_factor:
    alpha = st.sidebar.slider("Damping factor ($\\alpha$)", 0.0, 1.0, 0.85, 0.05)
else:
    alpha = 1.0

use_topic_teleport = st.sidebar.checkbox("Use topic teleport", value=False)
if use_topic_teleport:
    topic_choice = st.sidebar.selectbox("Topic select", list(TOPIC_TELEPORT.keys()), index=0)

use_seed_pages = st.sidebar.checkbox("Use TrustRank seeds", value=False)
if use_seed_pages:
    seed_pages = st.sidebar.text_input("Seed pages", value="I,J,D")

use_edge_weights = st.sidebar.checkbox("Use edge weights", value=False)

st.sidebar.divider()
tol = st.sidebar.number_input("Stop tolerance (L1 distance)", min_value=1e-10, max_value=1.0, value=1e-6, step=1e-6, format="%.0e")
max_iter = st.sidebar.slider("Max iterations", 1, 500, 100)

# Build unweighted transition matrix P (row-stochastic, dangling -> uniform)
A = np.zeros((n, n), dtype=float)
for u, v, w in EDGES:
    if use_edge_weights:
        A[IDX[v], IDX[u]] += float(w)
    else:
        A[IDX[v], IDX[u]] += 1

col_sums = A.sum(axis=0, keepdims=True)
A = np.where(col_sums > 0, A / col_sums, 1.0/n)

p = np.zeros(n, dtype=float)
if use_topic_teleport:
    for node, prob in TOPIC_TELEPORT.get(topic_choice, {}).items():
        p[IDX[node]] = prob
    if p.sum() == 0:
        p[:] = 1.0 / n
    else:
        p /= p.sum()
else:
    p[:] = 1.0 / n

if use_seed_pages:
    seed_ids = [s.strip() for s in seed_pages.split(",") if s.strip() in IDX]
    s = np.zeros(n, dtype=float)
    for nid in seed_ids:
        s[IDX[nid]] = 1.0
    if s.sum() > 0:
        # Project p onto the seed set; if topic teleport gives zero to seeds, use uniform over seeds
        t = p * s
        if t.sum() == 0:
            t = s / s.sum()
        else:
            t /= t.sum()
    else:
        t = p
else:
    t = p

G = alpha * A + (1 - alpha) * np.outer(np.ones(n), t)

# ----------------------
# Session state initialization
# ----------------------
def reset_state():
    st.session_state.pi_alpha = alpha
    st.session_state.pi_tol = tol
    st.session_state.pi_max = max_iter
    st.session_state.pi_k = 0
    r0 = np.ones(n) / n  # uniform start
    st.session_state.pi_hist = [r0]  # list of vectors
    st.session_state.pi_converged = False
    st.session_state.pi_last_delta = None

if "pi_hist" not in st.session_state:
    reset_state()

# Reset if parameters changed
if (st.session_state.get("pi_alpha") != alpha or
    st.session_state.get("pi_tol") != tol or
    st.session_state.get("pi_max") != max_iter):
    reset_state()

# --- One-time graph + fixed positions (put after P is created) ---
# Build a simple unweighted DiGraph for visualization
G_vis = nx.DiGraph()
G_vis.add_nodes_from(NODE_IDS)
G_vis.add_edges_from([(u, v) for (u, v, _w) in EDGES])

# Persist node positions across iterations so layout stays fixed
if "pi_pos" not in st.session_state:
    # Spring layout with a fixed seed for reproducibility
    st.session_state.pi_pos = nx.spring_layout(G_vis, seed=42, k=None)  # tweak k if you want spacing
pos = st.session_state.pi_pos

# --- Helper to build a Plotly figure with node sizes from current scores ---
def graph_pr_figure(scores: np.ndarray) -> go.Figure:
    # Normalize scores to a readable marker size
    s = np.array(scores, dtype=float)
    if s.max() > 0:
        s_norm = (s - s.min()) / (s.max() - s.min() + 1e-12)
    else:
        s_norm = np.zeros_like(s)
    marker_sizes = 12 + 28 * s_norm  # range ≈ [12, 40]

    # Edge traces (as line segments)
    edge_x, edge_y = [], []
    for u, v in G_vis.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode="lines",
        line=dict(width=1, color="rgba(150,150,150,0.6)"),
        hoverinfo="none",
        showlegend=False
    )

    # Node trace
    node_x = [pos[n][0] for n in NODE_IDS]
    node_y = [pos[n][1] for n in NODE_IDS]
    node_text = [f"{n}: {score:.4f}" for n, score in zip(NODE_IDS, s)]
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=NODE_IDS,
        textposition="middle center",
        hovertext=node_text,
        hoverinfo="text",
        textfont=dict(color="white"),
        marker=dict(
            size=marker_sizes,
            line=dict(width=1, color="white"),
            color="rgba(31,119,180,0.85)",
        ),
        showlegend=False
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        # title=f"Power Iteration — Node Sizes = PageRank (k={st.session_state.pi_k})",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=10, r=10, t=40, b=10),
        plot_bgcolor="white",
        hovermode="closest"
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)  # keep aspect ratio
    return fig


# ----------------------
# Power iteration helpers
# ----------------------
def step_once():
    """Compute one power-iteration step and append to history."""
    k = st.session_state.pi_k
    r = st.session_state.pi_hist[k]
    # Teleport vector v: uniform
    v = np.ones(n) / n
    # Next iterate: r_{k+1}^T = α r_k^T P + (1-α) v^T
    # r_next = alpha * (r @ G) + (1 - alpha) * v
    r_next = G @ r
    # Normalize defensively
    r_next = r_next / r_next.sum()
    delta = np.abs(r_next - r).sum()
    st.session_state.pi_hist.append(r_next)
    st.session_state.pi_k = k + 1
    st.session_state.pi_last_delta = float(delta)
    if delta < tol or st.session_state.pi_k >= max_iter:
        st.session_state.pi_converged = True

def step_prev():
    """Move back one iteration if possible."""
    if st.session_state.pi_k > 0:
        st.session_state.pi_k -= 1

def run_all():
    """Run until converge or reach max_iter."""
    # If we are not at the end of the history, jump to end first
    st.session_state.pi_k = len(st.session_state.pi_hist) - 1
    while not st.session_state.pi_converged and st.session_state.pi_k < max_iter:
        step_once()

# ----------------------
# UI: Buttons
# ----------------------
colA, colB, _, colC, colD = st.columns([2,2,1,3,3])
with colA:
    if st.button("◀ Prev", use_container_width=True):
        step_prev()
    if st.button("Reset", use_container_width=True, type="primary"):
        reset_state()
with colB:
    if st.button("Next ▶", use_container_width=True):
        # If we're at the tail, compute a new step; otherwise move cursor forward
        if st.session_state.pi_k == len(st.session_state.pi_hist) - 1:
            step_once()
        else:
            st.session_state.pi_k += 1
    if st.button("Run all", use_container_width=True, type="primary"):
        run_all()

# ----------------------
# Display: iteration status and current rank vector
# ----------------------
k = st.session_state.pi_k
r_k = st.session_state.pi_hist[k]
delta = st.session_state.pi_last_delta if k > 0 else None

# Metrics row
# st.divider()
# col1, col2, col3 = st.columns(3)
with colC:
    st.metric("Iteration", f"k = {k}")
with colD:
    status, color = ('✅ Converged', 'normal') if st.session_state.pi_converged else ('⏳ In progress', 'off')
    if delta is None:
        st.metric("L1 change", 0)
    else:
        st.metric("L1 change", f"{delta:.2e}", delta=status, delta_color=color)
st.divider()


col1, col2 = st.columns(2)
with col1:
    st.subheader("Graph View")
    fig_graph = graph_pr_figure(r_k)
    st.plotly_chart(fig_graph, use_container_width=True)
with col2:
    st.subheader("PageRank Scores")
    df_rank = pd.DataFrame({
        "node": NODE_IDS,
        "score": r_k
    }).sort_values("score", ascending=False).reset_index(drop=True)
    fig = px.bar(df_rank, y="node", x="score")
    fig.update_layout(yaxis_tickformat=".4f")
    st.plotly_chart(fig, use_container_width=True)


# ----------------------
# (Optional) Show last 5 iterations as a mini history
# ----------------------
with st.expander("Show recent iteration history (last 5)"):
    hist = np.vstack(st.session_state.pi_hist)
    last = min(hist.shape[0], 5)
    df_hist = pd.DataFrame(
        hist[-last:, :],
        index=[f"k={i}" for i in range(hist.shape[0]-last, hist.shape[0])],
        columns=NODE_IDS
    ).T
    st.dataframe(df_hist.style.format("{:.4f}"), use_container_width=True)
