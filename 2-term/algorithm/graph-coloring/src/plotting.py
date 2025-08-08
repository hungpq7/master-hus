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