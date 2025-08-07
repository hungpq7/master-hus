import streamlit as st
import networkx as nx
import time

# Step generators
def bruteforce_steps(graph, k):
    n = graph.number_of_nodes()
    colors = [0] * n
    def is_valid():
        for u, v in graph.edges():
            if colors[u] == colors[v]:
                return False
        return True
    while True:
        if is_valid():
            break
        i = 0
        while i < n:
            colors[i] += 1
            if colors[i] < k:
                break
            colors[i] = 0
            i += 1
        if i == n:
            break
        yield colors.copy()
    yield colors.copy()


def backtracking_steps(graph, k):
    n = graph.number_of_nodes()
    colors = [-1] * n
    v = 0
    while 0 <= v < n:
        colors[v] += 1
        while colors[v] < k and any(colors[v] == colors[u] for u in graph.neighbors(v) if colors[u] != -1):
            colors[v] += 1
        if colors[v] < k:
            v += 1
            if v < n:
                colors[v] = -1
        else:
            colors[v] = -1
            v -= 1
        yield colors.copy()


def greedy_steps(graph):
    n = graph.number_of_nodes()
    colors = [-1] * n
    for v in graph.nodes():
        used = {colors[u] for u in graph.neighbors(v) if colors[u] != -1}
        c = 0
        while c in used:
            c += 1
        colors[v] = c
        yield colors.copy()


def welsh_powell_steps(graph):
    order = sorted(graph.nodes(), key=lambda v: graph.degree(v), reverse=True)
    colors = [-1] * graph.number_of_nodes()
    for v in order:
        used = {colors[u] for u in graph.neighbors(v) if colors[u] != -1}
        c = 0
        while c in used:
            c += 1
        colors[v] = c
        yield colors.copy()


def dsatur_steps(graph):
    n = graph.number_of_nodes()
    colors = [-1] * n
    degrees = dict(graph.degree())
    uncolored = set(graph.nodes())
    while uncolored:
        sat_degrees = {v: len({colors[u] for u in graph.neighbors(v) if colors[u] != -1}) for v in uncolored}
        max_sat = max(sat_degrees.values())
        candidates = [v for v, sat in sat_degrees.items() if sat == max_sat]
        v = max(candidates, key=lambda x: degrees[x])
        used = {colors[u] for u in graph.neighbors(v) if colors[u] != -1}
        c = 0
        while c in used:
            c += 1
        colors[v] = c
        uncolored.remove(v)
        yield colors.copy()

# Sidebar controls
alg = st.sidebar.selectbox("Algorithm", ["Brute Force", "Backtracking", "Greedy", "Welsh-Powell", "DSATUR"])

# Graph selection
graph_option = st.sidebar.selectbox("Graph", ["4-cycle", "Custom"])
if graph_option == "4-cycle":
    G = nx.cycle_graph(4)
else:
    adj = st.sidebar.text_area("Edges (u v per line):", "0 1\n1 2\n2 3\n3 0")
    G = nx.Graph()
    nodes = set()
    for line in adj.splitlines():
        u, v = map(int, line.split())
        nodes.update([u, v])
        G.add_edge(u, v)
    G.add_nodes_from(nodes)

# Color count for exact algorithms
if alg in ["Brute Force", "Backtracking"]:
    k = st.sidebar.number_input("Colors", min_value=1, max_value=10, value=3)

# Generate steps

def get_steps():
    if alg == "Brute Force":
        return list(bruteforce_steps(G, k))
    if alg == "Backtracking":
        return list(backtracking_steps(G, k))
    if alg == "Greedy":
        return list(greedy_steps(G))
    if alg == "Welsh-Powell":
        return list(welsh_powell_steps(G))
    if alg == "DSATUR":
        return list(dsatur_steps(G))

steps = get_steps()
max_steps = len(steps)

# Initialize session state
if 'step_idx' not in st.session_state:
    st.session_state.step_idx = 0
if 'elapsed' not in st.session_state:
    st.session_state.elapsed = 0.0

# Custom button styles
st.markdown("""
<style>
.white-btn .stButton>button { background-color: white; color: black; }
.red-btn .stButton>button { background-color: red; color: white; }
</style>
""", unsafe_allow_html=True)

# Line 1: Navigation & Run All
def run_all():
    start = time.time()
    _ = get_steps()
    st.session_state.elapsed = time.time() - start

ctrl_col1, ctrl_col2 = st.columns([1,1])
with ctrl_col1:
    st.markdown('<div class="white-btn">', unsafe_allow_html=True)
    if st.button("Previous", key="prev"): st.session_state.step_idx = max(st.session_state.step_idx-1, 0)
    if st.button("Next", key="next"): st.session_state.step_idx = min(st.session_state.step_idx+1, max_steps-1)
    st.markdown('</div>', unsafe_allow_html=True)
with ctrl_col2:
    st.markdown('<div class="red-btn">', unsafe_allow_html=True)
    if st.button("Run All", on_click=run_all, key="runall"): pass
    st.markdown('</div>', unsafe_allow_html=True)

# Line 2: Metrics
met_col1, met_col2 = st.columns([1,1])
met_col1.metric("Step", f"{st.session_state.step_idx+1}/{max_steps}")
met_col2.metric("Elapsed (s)", f"{st.session_state.elapsed:.4f}")

# Centered, larger graph
g1, g2, g3 = st.columns([1,3,1])
with g2:
    draw_graph(steps[st.session_state.step_idx])

# Color encoding explanation
st.markdown("**Color encoding:**")
st.markdown(
    "- **0**: default/background (`#CCCCCC`)"
    "- **1**: first color (`#E24A33`)"
    "- **2**: second color (`#348ABD`)"
    "- **3**: third color (`#988ED5`)"
    "- **4**: fourth color (`#777777`)"
    "- **5**: fifth color (`#FBC15E`)"
    "- **6**: sixth color (`#8EBA42`)"
    "- **7**: seventh color (`#FFB5B8`)"
    "- **8**: eighth color (`#B15E81`)"
    "- **9**: ninth color (`#7F7F7F`)"
)
