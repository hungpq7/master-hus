# pages/02_Power_Iteration_PageRank.py
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

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

# Order nodes, build index maps
NODE_IDS = sorted(NODES.keys())
IDX = {n:i for i,n in enumerate(NODE_IDS)}
n = len(NODE_IDS)

# Build unweighted transition matrix P (row-stochastic, dangling -> uniform)
A = np.zeros((n, n), dtype=float)
for u, v, _w in EDGES:
    A[IDX[u], IDX[v]] = 1.0  # unweighted connectivity

row_sums = A.sum(axis=1, keepdims=True)
P = np.where(row_sums > 0, A / row_sums, 1.0/n)

# ----------------------
# Sidebar: configuration
# ----------------------
st.sidebar.header("Power Iteration Settings")
alpha = st.sidebar.slider("Damping factor (α)", 0.0, 1.0, 0.85, 0.01)
tol = st.sidebar.number_input("Stop tolerance (L1 distance)", min_value=1e-10, max_value=1.0, value=1e-6, step=1e-6, format="%.0e")
max_iter = st.sidebar.slider("Max iterations", 1, 500, 100)

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
    r_next = alpha * (r @ P) + (1 - alpha) * v
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
colA, colB, colC = st.columns([1,1,2])
with colA:
    if st.button("◀ Prev", use_container_width=True):
        step_prev()
with colB:
    if st.button("Next ▶", use_container_width=True):
        # If we're at the tail, compute a new step; otherwise move cursor forward
        if st.session_state.pi_k == len(st.session_state.pi_hist) - 1:
            step_once()
        else:
            st.session_state.pi_k += 1
with colC:
    if st.button("Run all (until converge)", use_container_width=True):
        run_all()

# ----------------------
# Display: iteration status and current rank vector
# ----------------------
k = st.session_state.pi_k
r_k = st.session_state.pi_hist[k]
delta = st.session_state.pi_last_delta if k > 0 else None

st.markdown(f"### Iteration **k = {k}**  |  α = **{alpha:.2f}**")
status = "✅ Converged" if st.session_state.pi_converged else "⏳ In progress"
st.write(f"Status: {status}")
if delta is not None:
    st.write(f"L1 change from k-1 → k: **{delta:.3e}**  (tol = {tol:.1e})")

# Table view (sorted by rank desc)
df_rank = pd.DataFrame({
    "node": NODE_IDS,
    "score": r_k
}).sort_values("score", ascending=False).reset_index(drop=True)
st.dataframe(df_rank.style.format({"score": "{:.6f}"}), use_container_width=True)

# Bar chart
fig = px.bar(df_rank, x="node", y="score", title=f"PageRank Scores at Iteration k={k}")
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
