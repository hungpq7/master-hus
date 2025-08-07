import streamlit as st
import networkx as nx
import time


# Step generators
def bruteforce_steps(graph, k):
    n = graph.number_of_nodes()
    colors = [0] * n  # 0 represents unassigned or color 0

    def is_valid():
        for u, v in graph.edges():
            if colors[u] == colors[v] and colors[u] != 0:
                return False
        return True

    while True:
        if is_valid():
            break

        i = 0
        while i < n:
            colors[i] += 1
            if colors[i] <= k:
                break
            colors[i] = 0
            i += 1

        if i == n:
            break

        yield colors.copy()

    yield colors.copy()


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
    st.session_state.elapsed = 0.0

st.sidebar.title("GRAPH COLORING")
st.sidebar.selectbox(
    "Algorithm",
    ["Brute Force", "Backtracking", "Greedy", "Welsh-Powell", "DSATUR"],
    key="alg",
    on_change=reset_step,
)
st.sidebar.selectbox(
    "Graph",
    ["4-cycle", "Custom"],
    key="graph_option",
    on_change=reset_step,
)

alg = st.session_state.alg
graph_option = st.session_state.graph_option

# Build graph
if graph_option == "4-cycle":
    G = nx.cycle_graph(4)
else:
    adj = st.sidebar.text_area(
        "Edges (u v per line):", "1 2\n2 3\n3 4\n4 1", key="edges"
    )
    G = nx.Graph()
    for line in adj.splitlines():
        u, v = map(int, line.split())
        # convert 1-based input to 0-based internal
        G.add_edge(u-1, v-1)
    # ensure nodes present even if isolated
    nodes = {u for edge in G.edges() for u in edge}
    G.add_nodes_from(nodes)

# Color count
if alg in ["Brute Force", "Backtracking"]:
    k = st.sidebar.number_input(
        "Colors", min_value=1, max_value=10, value=3, key="k", on_change=reset_step
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

# Session state
if "step_idx" not in st.session_state:
    st.session_state.step_idx = 0
if "elapsed" not in st.session_state:
    st.session_state.elapsed = 0.0

# Draw graph

def draw_graph(G, colors):
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

# Sidebar title and controls
st.sidebar.title("GRAPH COLORING DEMO")
# Algorithm selection
algorithms = ["Brute Force", "Backtracking", "Greedy", "Welsh-Powell", "DSATUR"]
st.sidebar.selectbox("Algorithm", algorithms, key="alg", on_change=lambda: st.session_state.update({"step_idx":0, "elapsed":0}))

# Predefined graph demos
demo = st.sidebar.selectbox(
    "Demo Graph",
    ["4-cycle", "Complete Graph", "Path Graph", "Star Graph", "Binary Tree", "Random Graph", "Custom"],
    key="demo",
    on_change=lambda: st.session_state.update({"step_idx":0, "elapsed":0})
)

# Parameters for demos
if demo == "Complete Graph":
    n = st.sidebar.number_input("Nodes (n)", min_value=2, max_value=20, value=5, key="param_n")
    G = nx.complete_graph(n)
elif demo == "Path Graph":
    n = st.sidebar.number_input("Nodes (n)", min_value=2, max_value=20, value=5, key="param_n2")
    G = nx.path_graph(n)
elif demo == "Star Graph":
    n = st.sidebar.number_input("Leaves (n)", min_value=1, max_value=20, value=4, key="param_n3")
    G = nx.star_graph(n)
elif demo == "Binary Tree":
    h = st.sidebar.number_input("Height (h)", min_value=1, max_value=5, value=3, key="param_h")
    G = nx.balanced_tree(r=2, h=h)
elif demo == "Random Graph":
    n = st.sidebar.number_input("Nodes (n)", min_value=2, max_value=20, value=10, key="param_n4")
    p = st.sidebar.slider("Edge Prob (p)", min_value=0.0, max_value=1.0, value=0.3, step=0.05, key="param_p")
    G = nx.erdos_renyi_graph(n, p)
elif demo == "4-cycle":
    G = nx.cycle_graph(4)
else:
    adj = st.sidebar.text_area("Edges (u v per line):", "1 2\n2 3\n3 4\n4 1", key="edges")
    G = nx.Graph()
    nodes = set()
    for line in adj.splitlines():
        u, v = map(int, line.split())
        nodes.update([u-1, v-1])
        G.add_edge(u-1, v-1)
    G.add_nodes_from(nodes)

# Color count for exact algorithms
if st.session_state.alg in ["Brute Force", "Backtracking"]:
    k = st.sidebar.number_input("Colors", min_value=1, max_value=10, value=3, key="k", on_change=lambda: st.session_state.update({"step_idx":0, "elapsed":0}))

# Generate steps
generators = {
    "Brute Force": lambda: list(bruteforce_steps(G, k)),
    "Backtracking": lambda: list(backtracking_steps(G, k)),
    "Greedy": lambda: list(greedy_steps(G)),
    "Welsh-Powell": lambda: list(welsh_powell_steps(G)),
    "DSATUR": lambda: list(dsatur_steps(G)),
}
steps = generators[st.session_state.alg]()
max_steps = len(steps)

# Session state defaults
st.session_state.setdefault("step_idx", 0)
st.session_state.setdefault("elapsed", 0.0)

# Controls
col1, col2 = st.columns([2,1])
with col1:
    prev, next = st.columns([1,10])
    if prev.button("Previous", key="prev"):
        st.session_state.step_idx = max(st.session_state.step_idx - 1, 0)
    if next.button("Next", key="next"):
        st.session_state.step_idx = min(st.session_state.step_idx + 1, max_steps-1)
with col2:
    if st.button("Run All", key="runall", on_click=lambda: st.session_state.update({"elapsed": time.time() - start_time})):
        start_time = time.time()
        _ = generators[st.session_state.alg]()

# Metrics
m1, m2 = st.columns(2)
m1.metric("Step", f"{st.session_state.step_idx+1}/{max_steps}")

m2.metric("Elapsed (s)", f"{st.session_state.elapsed:.4f}")

# Graph display
_, gc, _ = st.columns([1,3,1])
with gc:
    draw_graph(G, steps[st.session_state.step_idx])

# Explanation
st.markdown(f"**Current assignment:** {steps[st.session_state.step_idx]}")
