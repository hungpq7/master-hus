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
        while (
            colors[v] < k
            and any(
                colors[v] == colors[u]
                for u in graph.neighbors(v)
                if colors[u] != -1
            )
        ):
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
    order = sorted(
        graph.nodes(), key=lambda v: graph.degree(v), reverse=True
    )
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
        sat_degrees = {
            v: len({colors[u]
                     for u in graph.neighbors(v)
                     if colors[u] != -1})
            for v in uncolored
        }
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
alg = st.sidebar.selectbox(
    "Algorithm",
    ["Brute Force", "Backtracking", "Greedy", "Welsh-Powell", "DSATUR"],
)


# Graph selection
graph_option = st.sidebar.selectbox("Graph", ["4-cycle", "Custom"])
if graph_option == "4-cycle":
    G = nx.cycle_graph(4)
else:
    adj = st.sidebar.text_area(
        "Edges (u v per line):", "0 1\n1 2\n2 3\n3 0"
    )
    G = nx.Graph()
    nodes = set()
    for line in adj.splitlines():
        u, v = map(int, line.split())
        nodes.update([u, v])
        G.add_edge(u, v)
    G.add_nodes_from(nodes)


# Color count for exact algorithms
if alg in ["Brute Force", "Backtracking"]:
    k = st.sidebar.number_input(
        "Colors", min_value=1, max_value=10, value=3
    )


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
if "step_idx" not in st.session_state:
    st.session_state.step_idx = 0
if "elapsed" not in st.session_state:
    st.session_state.elapsed = 0.0


# Draw graph function
def draw_graph(colors):
    dot = ("graph G {\n"
           "  graph [splines=true, overlap=false, sep=0.5, "
           "ranksep=0.5, layout=neato];\n")
    palette = [
        "#CCCCCC", "#E24A33", "#348ABD", "#988ED5", "#777777",
        "#FBC15E", "#8EBA42", "#FFB5B8", "#B15E81", "#7F7F7F",
    ]
    dot += (
        "  node [shape=circle, style=filled, color=\"#333333\", "
        "fontcolor=\"#000000\", fontsize=12];\n"
    )
    dot += "  edge [color=\"#444444\", penwidth=1.5];\n"

    for i, c in enumerate(colors):
        fill = palette[c % len(palette)]
        dot += f"  {i} [fillcolor=\"{fill}\"];\n"

    for u, v in G.edges():
        dot += f"  {u} -- {v};\n"

    dot += "}"
    st.graphviz_chart(dot)


# Custom button styles
st.markdown(
    """
<style>
.white-btn .stButton>button { background-color: white; color: black; }
.red-btn .stButton>button { background-color: red; color: white; }
</style>
    """,
    unsafe_allow_html=True,
)


# Line 1: Navigation & Run All
def run_all():
    start = time.time()
    _ = get_steps()
    st.session_state.elapsed = time.time() - start

ctrl_col1, ctrl_col2 = st.columns([1, 1])
with ctrl_col1:
    if st.button("Previous", key="prev"):  # noqa: E731
        st.session_state.step_idx = max(st.session_state.step_idx - 1, 0)
    if st.button("Next", key="next"):  # noqa: E731
        st.session_state.step_idx = min(st.session_state.step_idx + 1, max_steps - 1)

with ctrl_col2:
    if st.button("Run All", on_click=run_all, key="runall"):  # noqa: E731
        pass


# Line 2: Metrics
met_col1, met_col2 = st.columns([1, 1])
met_col1.metric("Step", f"{st.session_state.step_idx + 1}/{max_steps}")
met_col2.metric("Elapsed (s)", f"{st.session_state.elapsed:.4f}")


# Centered, larger graph layout
_, graph_col, _ = st.columns([1, 3, 1])
with graph_col:
    draw_graph(steps[st.session_state.step_idx])
