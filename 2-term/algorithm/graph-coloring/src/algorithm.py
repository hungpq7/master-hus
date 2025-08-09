def backtracking_steps(graph, k):
    n = graph.number_of_nodes()  # Total number of nodes in the graph
    colors = [0] * n  # List to hold the color for each node (0 means uncolored)
    v = 0  # Start at the first node
    step_idx = 1  # Initialize step counter

    while 0 <= v < n:
        colors[v] += 1  # Try to assign the next color to the current node
        while (
            colors[v] <= k  # Check if the color is within the limit
            and any(
                colors[v] == colors[u]  # Ensure no color conflict with neighbors
                for u in graph.neighbors(v)
                if colors[u] != 0  # Only check neighbors that are already colored
            )
        ):
            colors[v] += 1  # Increment the color if there’s a conflict

        msgs = list()  # List to hold the messages for each step
        msgs.append(f"Step {step_idx}: Trying to assign a color to node {v+1}.")
        
        if colors[v] <= k:
            msgs.append(f"- Assigned color {colors[v]} to node {v+1}.")
            msgs.append("- No conflict detected, move to the next node.")
            v += 1  # Move to the next node
            if v < n:
                colors[v] = 0  # Reset color for the next node
        else:
            msgs.append(f"- Backtracking: no valid color found for node {v+1}.")
            msgs.append("- Going back to the previous node to try a different color.")
            colors[v] = 0  # Reset the color of the current node
            v -= 1  # Backtrack to the previous node
        
        if v < 0: msgs.append("\n:red-badge[:material/close: Failure]")  # If backtracking to before the first node, it’s a failure
        elif v == n: msgs.append("\n:green-badge[:material/check: Success]")  # Success if all nodes are colored

        step_idx += 1  # Increment step counter
        yield colors.copy(), msgs  # Yield the current coloring and messages


def greedy_steps(graph):
    n = graph.number_of_nodes()  # Total number of nodes in the graph
    colors = [0] * n  # List to hold the color for each node (0 means uncolored)
    step_idx = 1  # Initialize step counter

    nodes_list = list(graph.nodes())  # List of all nodes in the graph
    for idx, v in enumerate(nodes_list):  # Loop over all nodes
        used = {colors[u] for u in graph.neighbors(v) if colors[u] != 0}  # Collect colors of neighbors
        c = 1  # Start with color 1
        while c in used:  # Find the smallest available color that is not used by neighbors
            c += 1
        colors[v] = c  # Assign the chosen color to the current node

        msgs = list()  # List to hold the messages for each step
        msgs.append(f"Step {step_idx}: Greedy choice for node {v+1}.")
        msgs.append(f"- Neighbor colors in use: {used}.")
        msgs.append(f"- Assigned color {c} to node {v+1}.")
        
        if idx == n - 1:  # If it’s the last node in the list
            msgs.append("\n:green-badge[:material/check: Success]")  # Success when all nodes are colored
        
        step_idx += 1  # Increment step counter
        yield colors.copy(), msgs  # Yield the current coloring and messages


def welsh_powell_steps(graph):
    n = graph.number_of_nodes()  # Total number of nodes in the graph
    order = sorted(graph.nodes(), key=lambda v: graph.degree(v), reverse=True)  # Sort nodes by degree in descending order
    colors = [0] * graph.number_of_nodes()  # List to hold the color for each node (0 means uncolored)
    step_idx = 1  # Initialize step counter

    for idx, v in enumerate(order):  # Loop over all nodes in the sorted order
        used = {colors[u] for u in graph.neighbors(v) if colors[u] != 0}  # Collect colors of neighbors
        c = 1  # Start with color 1
        while c in used:  # Find the smallest available color that is not used by neighbors
            c += 1
        colors[v] = c  # Assign the chosen color to the current node

        msgs = [f"Step {step_idx}: Welsh-Powell (degree-based) choice for node {v+1}."]  # Step message
        msgs.append(f"- Neighbor colors in use: {used}.")
        msgs.append(f"- Assigned color {c}.")
        
        if idx == n - 1:  # If it’s the last node in the sorted order
            msgs.append("\n:green-badge[:material/check: Success]")  # Success when all nodes are colored
        
        step_idx += 1  # Increment step counter
        yield colors.copy(), msgs  # Yield the current coloring and messages


def dsatur_steps(graph):
    n = graph.number_of_nodes()  # Total number of nodes in the graph
    colors = [0] * n  # List to hold the color for each node (0 means uncolored)
    degrees = dict(graph.degree())  # Dictionary with node degrees
    uncolored = set(graph.nodes())  # Set of uncolored nodes
    step_idx = 1  # Initialize step counter

    while uncolored:  # Continue until all nodes are colored
        sat_degrees = {
            v: len({colors[u] for u in graph.neighbors(v) if colors[u] != 0})  # Calculate saturation degree for each node
            for v in uncolored
        }
        max_sat = max(sat_degrees.values())  # Find the maximum saturation degree
        candidates = [v for v, sat in sat_degrees.items() if sat == max_sat]  # Nodes with the maximum saturation degree
        v = max(candidates, key=lambda x: degrees[x])  # Choose the node with the highest degree from the candidates

        used = {colors[u] for u in graph.neighbors(v) if colors[u] != 0}  # Collect colors of neighbors
        c = 1  # Start with color 1
        while c in used:  # Find the smallest available color that is not used by neighbors
            c += 1

        colors[v] = c  # Assign the chosen color to the current node
        uncolored.remove(v)  # Remove the node from the set of uncolored nodes

        msgs = [f"Step {step_idx}: DSATUR choice for node {v+1}."]  # Step message
        msgs.append(f"- Saturation degrees: {sat_degrees}.")
        msgs.append(f"- Assigned color {c}.")
        
        if not uncolored:  # If all nodes are colored
            msgs.append("\n:green-badge[:material/check: Success]")  # Success when all nodes are colored
        
        step_idx += 1  # Increment step counter
        yield colors.copy(), msgs  # Yield the current coloring and messages
