import streamlit as st
import networkx as nx
import time

def backtracking_steps(graph, k):
    n = graph.number_of_nodes()
    colors = [0] * n
    v = 0

    while 0 <= v < n:
        colors[v] += 1
        while (
            colors[v] <= k
            and any(
                colors[v] == colors[u]
                for u in graph.neighbors(v)
                if colors[u] != 0
            )
        ):
            colors[v] += 1

        if colors[v] <= k:
            v += 1
            if v < n:
                colors[v] = 0
        else:
            colors[v] = 0
            v -= 1

        yield colors.copy()


def greedy_steps(graph):
    n = graph.number_of_nodes()
    colors = [0] * n

    for v in graph.nodes():
        used = {colors[u] for u in graph.neighbors(v) if colors[u] != 0}
        c = 1
        while c in used:
            c += 1
        colors[v] = c
        yield colors.copy()


def welsh_powell_steps(graph):
    order = sorted(
        graph.nodes(), key=lambda v: graph.degree(v), reverse=True
    )
    colors = [0] * graph.number_of_nodes()

    for v in order:
        used = {colors[u] for u in graph.neighbors(v) if colors[u] != 0}
        c = 1
        while c in used:
            c += 1
        colors[v] = c
        yield colors.copy()


def dsatur_steps(graph):
    n = graph.number_of_nodes()
    colors = [0] * n
    degrees = dict(graph.degree())
    uncolored = set(graph.nodes())

    while uncolored:
        sat_degrees = {
            v: len({colors[u]
                     for u in graph.neighbors(v)
                     if colors[u] != 0})
            for v in uncolored
        }
        max_sat = max(sat_degrees.values())
        candidates = [v for v, sat in sat_degrees.items() if sat == max_sat]
        v = max(candidates, key=lambda x: degrees[x])

        used = {colors[u] for u in graph.neighbors(v) if colors[u] != 0}
        c = 1
        while c in used:
            c += 1

        colors[v] = c
        uncolored.remove(v)
        yield colors.copy()


# Sidebar title and controls
def reset_step():
    st.session_state.step_idx = 0

st.sidebar.title("GRAPH COLORING")
st.sidebar.selectbox(
    "Algorithm",
    ["Backtracking", "Greedy", "Welsh-Powell", "DSATUR"],
    key="alg",
    on_change=reset_step,
)
st.sidebar.selectbox(
    "Graph",
    [
        "4-cycle",
        "Complete Graph",
        "Path Graph",
        "Star Graph",
        "Custom",
    ],
    key="graph_option",
    on_change=reset_step,
)

alg = st.session_state.get("alg", "Backtracking")
graph_option = st.session_state.get("graph_option", "4-cycle")

# Build graph
if graph_option == "4-cycle":
    G = nx.cycle_graph(4)
elif graph_option == "Complete Graph":
    n = st.sidebar.number_input(
        "Number of nodes", min_value=1, max_value=20, value=5, key="complete_n", on_change=reset_step
    )
    G = nx.complete_graph(n)
elif graph_option == "Path Graph":
    n = st.sidebar.number_input(
        "Number of nodes", min_value=1, max_value=20, value=5, key="path_n", on_change=reset_step
    )
    G = nx.path_graph(n)
elif graph_option == "Star Graph":
    n = st.sidebar.number_input(
        "Number of leaves", min_value=1, max_value=20, value=4, key="star_n", on_change=reset_step
    )
    G = nx.star_graph(n)
else:
    adj = st.sidebar.text_area(
        "Edges (u v per line):", "1 2\n2 3\n3 4\n4 1", key="edges"
    )
    G = nx.Graph()
    for line in adj.splitlines():
        u, v = map(int, line.split())
        G.add_edge(u-1, v-1)
    nodes = {u for edge in G.edges() for u in edge}
    G.add_nodes_from(nodes)

# Color count
if alg in ["Backtracking"]:
    k = st.sidebar.number_input(
        "Colors", min_value=1, max_value=10, value=3, key="k", on_change=reset_step
    )
    st.sidebar.write(f"Number of colors: {k}")
else:
    k = None

# Generate steps
def get_steps():
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

col1, col2 = st.columns([1, 1])
with col1:
    sub1, sub2, _ = st.columns([1,1,1])
    with sub1:
        if st.button("Previous"):
            st.session_state.step_idx = max(st.session_state.step_idx - 1, 0)
    with sub2:
        if st.button("Next"):
            st.session_state.step_idx = min(st.session_state.step_idx + 1, max_steps - 1)
    st.metric("Step", f"{st.session_state.step_idx + 1}/{max_steps}")
with col2:
    if st.button("Run All", type='primary'):
        st.session_state.step_idx = max_steps - 1

def draw_graph(colors):
    dot = (
        "graph G {\n"
        "  graph [splines=true, overlap=false, sep=1.0, ranksep=1.0, nodesep=1.0, layout=neato];\n"
    )
    palette = [
        "#FFFFFF", "#E24A33", "#348ABD", "#988ED5", "#777777",
        "#FBC15E", "#8EBA42", "#FFB5B8", "#B15E81", "#7F7F7F",
    ]
    dot += (
        "  node [shape=circle, style=filled, color=\"#333333\", "
        "fontcolor=\"#000000\", fontsize=14, width=0.5, height=0.5];\n"
    )
    dot += "  edge [color=\"#444444\", penwidth=2];\n"
    for idx, c in enumerate(colors):
        node_id = idx + 1
        fill = palette[c] if c < len(palette) else palette[0]
        dot += f"  {node_id} [label=\"{node_id}\", fillcolor=\"{fill}\"];\n"
    for u, v in G.edges():
        dot += f"  {u+1} -- {v+1};\n"
    dot += "}"
    st.graphviz_chart(dot)

# Render graph and info
current_colors = steps[st.session_state.step_idx]

draw_graph(current_colors)
st.write(f"Node color assignments (1-based indices): {current_colors}")
