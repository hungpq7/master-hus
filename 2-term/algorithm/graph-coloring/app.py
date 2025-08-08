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
        "Erdos-Renyi",
        "Barabasi-Albert",
        "Watts-Strogatz",
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
        "Colors", min_value=1, max_value=10, value=3, key="k", on_change=reset_step
    )
    st.sidebar.write(f"Number of colors: {k}")
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

# In your step display logic, ensure you also show the explanation:
current_colors, current_explanation = steps[st.session_state.step_idx]

def draw_graph(colors):
    # graph visualization code here (unchanged)

with col1:
    draw_graph(current_colors)

with col2:
    st.write("### Interpretation")
    st.write(current_explanation)
