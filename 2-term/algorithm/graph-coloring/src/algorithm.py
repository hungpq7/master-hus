def backtracking_steps(graph, k):
    n = graph.number_of_nodes()
    colors = [0] * n
    v = 0
    step_idx = 1

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

        msgs = list()
        msgs.append(f"Step {step_idx}: Trying to assign a color to node {v+1}.")
        
        if colors[v] <= k:
            msgs.append(f"- Assigned color {colors[v]} to node {v+1}.")
            msgs.append("- No conflict detected, move to the next node.")
            v += 1
            if v < n:
                colors[v] = 0
        else:
            msgs.append(f"- Backtracking: no valid color found for node {v+1}.")
            msgs.append("- Going back to the previous node to try a different color.")
            colors[v] = 0
            v -= 1
        
        if v < 0: msgs.append("\n:red-badge[:material/close: Failure]")
        elif v == n: msgs.append("\n:green-badge[:material/check: Success]")

        step_idx += 1
        yield colors.copy(), msgs


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
        msgs = list()
        msgs.append(f"Step {step_idx}: Greedy choice for node {v+1}.")
        msgs.append(f"- Neighbor colors in use: {used}.")
        msgs.append(f"- Assigned color {c} to node {v+1}.")
        if v == n: msgs.append("\n:green-badge[:material/check: Success]")
        step_idx += 1
        yield colors.copy(), msgs


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
        msgs = [f"Step {step_idx}: Welsh-Powell (degree-based) choice for node {v+1}."]
        msgs.append(f"- Neighbor colors in use: {used}.")
        msgs.append(f"- Assigned color {c}.")
        if v == n: msgs.append("\n:green-badge[:material/check: Success]")
        step_idx += 1
        yield colors.copy(), msgs


def dsatur_steps(graph):
    n = graph.number_of_nodes()
    colors = [0] * n
    degrees = dict(graph.degree())
    uncolored = set(graph.nodes())
    step_idx = 1

    while uncolored:
        sat_degrees = {
            v: len({colors[u] for u in graph.neighbors(v) if colors[u] != 0})
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
        msgs = [f"Step {step_idx}: DSATUR choice for node {v+1}."]
        msgs.append(f"- Saturation degrees: {sat_degrees}.")
        msgs.append(f"- Assigned color {c}.")
        if not uncolored: msgs.append("\n:green-badge[:material/check: Success]")
        step_idx += 1
        yield colors.copy(), msgs
