import streamlit as st
import networkx as nx
import plotly.graph_objects as go
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

# Sidebar controls
alg = st.sidebar.selectbox("Algorithm", ["Brute Force", "Backtracking", "Greedy", "Welsh-Powell"])

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

if alg in ["Brute Force", "Backtracking"]:
    k = st.sidebar.number_input("Colors", min_value=1, max_value=10, value=3)

# Run all button
graph_trace = None
if st.button("Run All"):
    start = time.time()
    if alg == "Brute Force":
        steps = list(bruteforce_steps(G, k))
    elif alg == "Backtracking":
        steps = list(backtracking_steps(G, k))
    elif alg == "Greedy":
        steps = list(greedy_steps(G))
    else:
        steps = list(welsh_powell_steps(G))
    total_time = time.time() - start
    st.write(f"Total time: {total_time:.4f} seconds")
    final_colors = steps[-1] if steps else []
    # Prepare Plotly graph
    pos = nx.spring_layout(G, seed=42)
    edge_x, edge_y = [], []
    for u, v in G.edges():
        x0, y0 = pos[u]; x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
    edge_trace = go.Scatter(x=edge_x, y=edge_y, mode='lines', line=dict(width=1), hoverinfo='none')
    node_x = [pos[i][0] for i in G.nodes()]
    node_y = [pos[i][1] for i in G.nodes()]
    node_trace = go.Scatter(
        x=node_x, y=node_y, mode='markers+text', text=[str(i) for i in G.nodes()], textposition='top center', hoverinfo='none',
        marker=dict(size=20, color='grey'))
    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        margin=dict(b=0,l=0,r=0,t=0)
    )
    st.plotly_chart(fig, use_container_width=True)
