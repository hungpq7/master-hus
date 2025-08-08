import streamlit as st
import networkx as nx
import time

from src.algorithm import backtracking_steps, greedy_steps
from src.algorithm import welsh_powell_steps, dsatur_steps

st.set_page_config(layout="wide")

def reset_step():
    st.session_state.step_idx = 0

st.sidebar.title("GRAPH COLORING")
st.sidebar.selectbox(
    "ALGORITHM",
    ["Backtracking", "Greedy", "Welsh-Powell", "DSATUR"],
    key="alg",
    on_change=reset_step,
)
st.sidebar.selectbox(
    "GRAPH",
    [
        "Cycle", "Complete", "Path",
        "Erdos-Renyi", "Barabasi-Albert", "Watts-Strogatz",
        "Custom",
    ],
    key="graph_option",
    on_change=reset_step,
)

alg = st.session_state.get("alg", "Backtracking")
graph_option = st.session_state.get("graph_option", "Cycle")

if graph_option == "Cycle":
    n = st.sidebar.number_input(
        "NODES", min_value=1, max_value=20, value=5, key="complete_n", on_change=reset_step
    )
    G = nx.cycle_graph(n)
elif graph_option == "Complete":
    n = st.sidebar.number_input(
        "NODES", min_value=1, max_value=20, value=5, key="complete_n", on_change=reset_step
    )
    G = nx.complete_graph(n)
elif graph_option == "Path":
    n = st.sidebar.number_input(
        "NODES", min_value=1, max_value=20, value=5, key="path_n", on_change=reset_step
    )
    G = nx.path_graph(n)

elif graph_option in ["Erdos-Renyi", "Barabasi-Albert", "Watts-Strogatz"]:
    if graph_option == "Erdos-Renyi":
        n = st.sidebar.number_input("n (nodes)", 1, 100, 10, key="er_n", on_change=reset_step)
        p = st.sidebar.slider("p (prob)", 0.0, 1.0, 0.3, key="er_p", on_change=reset_step)
        params = {"n": n, "p": p}
    elif graph_option == "Barabasi-Albert":
        n = st.sidebar.number_input("n (nodes)", 1, 100, 10, key="ba_n", on_change=reset_step)
        m = st.sidebar.number_input("m (links)", 1, n-1, 2, key="ba_m", on_change=reset_step)
        params = {"n": n, "m": m}
    elif graph_option == "Watts-Strogatz":
        n = st.sidebar.number_input("n (nodes)", 1, 100, 10, key="ws_n", on_change=reset_step)
        k = st.sidebar.number_input("k (neigh)", 0, n-1, 4, key="ws_k", on_change=reset_step)
        p = st.sidebar.slider("p (rewire)", 0.0, 1.0, 0.1, key="ws_p", on_change=reset_step)
        params = {"n": n, "k": k, "p": p}

    if (
        "rand_graph" not in st.session_state
        or st.session_state.rand_graph_option != graph_option
        or st.session_state.rand_params != params
    ):
        if graph_option == "Erdos-Renyi":
            G = nx.erdos_renyi_graph(n, p)
        elif graph_option == "Barabasi-Albert":
            G = nx.barabasi_albert_graph(n, m)
        else:
            G = nx.watts_strogatz_graph(n, k, p)

        st.session_state.rand_graph = G
        st.session_state.rand_graph_option = graph_option
        st.session_state.rand_params = params
    else:
        G = st.session_state.rand_graph

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
        "COLORS", min_value=1, max_value=10, value=3, key="k", on_change=reset_step
    )
else:
    k = None

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
if "elapsed" not in st.session_state:
    st.session_state.elapsed = 0.0


col1, col2 = st.columns([1, 1])
with col1:
    col11, col12 = st.columns([1,1])
    with col11:
        if st.button("PREVIOUS"):
            st.session_state.step_idx = max(st.session_state.step_idx - 1, 0)
        st.metric("Step (current/total)", f"{st.session_state.step_idx + 1}/{max_steps}")
    with col12:
        if st.button("NEXT"):
            st.session_state.step_idx = min(st.session_state.step_idx + 1, max_steps - 1)
    st.write('---')

with col2:
    if st.button("RUN ALL", type='primary'):
        start = time.time()
        st.session_state.step_idx = max_steps - 1
        st.session_state.elapsed = time.time() - start
    st.metric("Elapsed (seconds)", f"{st.session_state.elapsed:.6f}s")
    st.write('---')

current_colors, current_explanation = steps[st.session_state.step_idx]
with col12:
    set_colors = set([c for c in current_colors if c > 0])
    st.metric("Colors used", len(set_colors))


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

with col1:
    draw_graph(current_colors)

with col2:
    st.write("### Interpretation")
    st.markdown(current_explanation)
