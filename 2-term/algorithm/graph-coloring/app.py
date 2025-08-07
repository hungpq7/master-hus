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
    # DSATUR: choose next vertex by saturation degree, tie-break on degree
    n = graph.number_of_nodes()
    colors = [-1] * n
    degrees = dict(graph.degree())
    uncolored = set(graph.nodes())
    while uncolored:
        # saturation degree: number of distinct neighbor colors
        sat_degrees = {v: len({colors[u] for u in graph.neighbors(v) if colors[u] != -1}) for v in uncolored}
        max_sat = max(sat_degrees.values())
        # candidates with maximum saturation
        candidates = [v for v, sat in sat_degrees.items() if sat == max_sat]
        # tie-break by degree
        v = max(candidates, key=lambda x: degrees[x])
        # assign smallest available color
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
if alg == "Brute Force":
    steps = list(bruteforce_steps(G, k))
elif alg == "Backtracking":
    steps = list(backtracking_steps(G, k))
elif alg == "Greedy":
    steps = list(greedy_steps(G))
elif alg == "Welsh-Powell":
    steps = list(welsh_powell_steps(G))
elif alg == "DSATUR":
    steps = list(dsatur_steps(G))

# Run All button and elapsed time
graph_col, time_col = st.columns([1,1])
elapsed = None
if graph_col.button("Run All"):
    start = time.time()
    # generate steps for timing
    elapsed = time.time() - start
    time_col.write(f"Elapsed: {elapsed:.4f}s")

# Step slider only
step_idx = st.slider("Step", 1, max(len(steps),1), 1) - 1

# Draw graph using Graphviz with node colors per step
def draw_graph(colors):
    dot = "graph G {\n"
    # Graph attributes
    dot += "  graph [splines=true, overlap=false, sep=0.5, ranksep=0.5, layout=neato];\n"
    # Define a palette for up to 10 colors
    palette = ['#CCCCCC','#E24A33','#348ABD','#988ED5','#777777','#FBC15E','#8EBA42','#FFB5B8','#B15E81','#7F7F7F']
    # Node style template
    dot += "  node [shape=circle, style=filled, color=\"#333333\", fontcolor=\"#000000\", fontsize=12];\n"
    # Edge style
    dot += "  edge [color=\"#444444\", penwidth=1.5];\n"
    # Nodes with per-step fillcolor
    for i, c in enumerate(colors):
        fill = palette[c % len(palette)]
        dot += f"  {i} [fillcolor=\"{fill}\"];\n"
    # Edges
    for u, v in G.edges():
        dot += f"  {u} -- {v};\n"
    dot += "}"
    st.graphviz_chart(dot)

# Render
draw_graph(steps[step_idx])
