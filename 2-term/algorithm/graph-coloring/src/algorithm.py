# def backtracking_steps(graph, k):
#     n = graph.number_of_nodes()
#     colors = [0] * n
#     v = 0
#     step_idx = 1

#     while 0 <= v < n:
#         colors[v] += 1
#         while (
#             colors[v] <= k
#             and any(
#                 colors[v] == colors[u]
#                 for u in graph.neighbors(v)
#                 if colors[u] != 0
#             )
#         ):
#             colors[v] += 1

#         explanation = f"Step {step_idx}: Trying to assign a color to node {v+1}.\n"
        
#         if colors[v] <= k:
#             explanation += f"- Assigned color {colors[v]} to node {v+1}.\n"
#             explanation += "- No conflict detected, move to the next node."
#             v += 1
#             if v < n:
#                 colors[v] = 0
#         else:
#             explanation += f"- Backtracking: no valid color found for node {v+1}.\n"
#             explanation += "- Going back to the previous node to try a different color."
#             colors[v] = 0
#             v -= 1

#         step_idx += 1
#         yield colors.copy(), explanation

def backtracking_steps(graph, k):
    n = graph.number_of_nodes()
    colors = [0] * n
    v = 0
    step_idx = 1

    while 0 <= v < n:
        # Try to assign a color to the current node
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

        explanation = f"Step {step_idx}: Trying to assign a color to node {v+1}.\n"
        
        if colors[v] <= k:
            explanation += f"- Assigned color {colors[v]} to node {v+1}.\n"
            explanation += "- No conflict detected, move to the next node."
            v += 1
            if v < n:
                colors[v] = 0  # Reset the next node color for the next iteration
        else:
            explanation += f"- Backtracking: no valid color found for node {v+1}.\n"
            explanation += "- Going back to the previous node to try a different color."
            colors[v] = 0
            v -= 1

        # Check if the solution is finished
        if v < 0:
            explanation += "\n- No solution found: backtracked to the first node, unable to assign valid colors."
            break
        elif v == n:  # All nodes successfully colored
            explanation += "\n- Solution found: all nodes successfully colored."
            break

        step_idx += 1
        yield colors.copy(), explanation  # yield both color and explanation


def greedy_steps(graph):
    n = graph.number_of_nodes()
    colors = [0] * n
    step_idx = 1

    for v in graph.nodes():
        used = {colors[u] for u in graph.neighbors(v) if colors[u] != 0}
        c = 1
        while c in used:
            c += 1
        colors[v] = c
        explanation = f"Step {step_idx}: Greedy choice for node {v+1}.\n"
        explanation += f"- Neighbor colors in use: {used}.\n"
        explanation += f"- Assigned color {c} to node {v+1}.\n"
        step_idx += 1
        yield colors.copy(), explanation


def welsh_powell_steps(graph):
    order = sorted(
        graph.nodes(), key=lambda v: graph.degree(v), reverse=True
    )
    colors = [0] * graph.number_of_nodes()
    step_idx = 1

    for v in order:
        used = {colors[u] for u in graph.neighbors(v) if colors[u] != 0}
        c = 1
        while c in used:
            c += 1
        colors[v] = c
        explanation = f"Step {step_idx}: Welsh-Powell (degree-based) choice for node {v+1}.\n"
        explanation += f"- Neighbor colors in use: {used}.\n"
        explanation += f"- Assigned color {c}.\n"
        step_idx += 1
        yield colors.copy(), explanation


def dsatur_steps(graph):
    n = graph.number_of_nodes()
    colors = [0] * n
    degrees = dict(graph.degree())
    uncolored = set(graph.nodes())
    step_idx = 1

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
        explanation = f"Step {step_idx}: DSATUR choice for node {v+1}.\n"
        explanation += f"- Saturation degrees: {sat_degrees}.\n"
        explanation += f"- Assigned color {c}.\n"
        step_idx += 1
        yield colors.copy(), explanation
