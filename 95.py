# Prompt 95

import networkx as nx
import matplotlib.pyplot as plt

# Create a directed graph
G = nx.DiGraph()

# Add nodes (intersections)
intersections = ['A', 'B', 'C', 'D', 'E', 'F']
G.add_nodes_from(intersections)

# Add edges (roads) with travel times
edges = [
    ('A', 'B', 10),
    ('A', 'C', 15),
    ('B', 'D', 12),
    ('C', 'D', 10),
    ('D', 'E', 8),
    ('E', 'F', 5),
    ('C', 'F', 20),
    ('B', 'F', 18)
]
G.add_weighted_edges_from(edges)

# Function to find the shortest path
def find_shortest_path(graph, start, end):
    try:
        shortest_path = nx.shortest_path(graph, source=start, target=end, weight='weight')
        shortest_path_length = nx.shortest_path_length(graph, source=start, target=end, weight='weight')
        return shortest_path, shortest_path_length
    except nx.NetworkXNoPath:
        return None, None

# Simulate traffic flow and find optimal routes
start_node = 'A'
end_node = 'F'
optimal_route, optimal_time = find_shortest_path(G, start_node, end_node)

# Output the optimal route and time
print(f"Optimal route from {start_node} to {end_node}: {optimal_route} with total travel time of {optimal_time} minutes.")

# Visualize the graph
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_size=700, node_color='skyblue', font_size=10, font_weight='bold', arrows=True)
edge_labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
plt.title("Urban Traffic Flow Simulation")
plt.show()