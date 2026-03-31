import tkinter as tk
from tkinter import messagebox
import networkx as nx
import matplotlib.pyplot as plt

# Initialize the graph
G = nx.Graph()

# GUI setup
root = tk.Tk()
root.title("Graph Algorithms Visualizer")

# Canvas for drawing
canvas = tk.Canvas(root, width=800, height=600, bg='white')
canvas.pack()

# Variables to store node positions
nodes = {}
edges = []

# Function to add a node
def add_node(event):
    node_id = canvas.create_oval(event.x-10, event.y-10, event.x+10, event.y+10, fill='blue')
    nodes[node_id] = (event.x, event.y)
    G.add_node(node_id)

# Function to add an edge
def add_edge(event):
    if len(nodes) < 2:
        messagebox.showwarning("Warning", "At least two nodes are required to draw an edge.")
        return
    start_node = None
    end_node = None
    for node_id, (x, y) in nodes.items():
        if abs(event.x - x) <= 10 and abs(event.y - y) <= 10:
            if start_node is None:
                start_node = node_id
            else:
                end_node = node_id
                break
    if start_node and end_node:
        edge_id = canvas.create_line(nodes[start_node][0], nodes[start_node][1], nodes[end_node][0], nodes[end_node][1], fill='red')
        edges.append(edge_id)
        G.add_edge(start_node, end_node)

# Bind events to canvas
canvas.bind("<Button-1>", add_node)
canvas.bind("<Button-3>", add_edge)

# Function to run Dijkstra's algorithm
def run_dijkstra():
    if len(nodes) < 2:
        messagebox.showwarning("Warning", "At least two nodes are required to run Dijkstra's algorithm.")
        return
    start_node = list(nodes.keys())[0]
    try:
        path = nx.dijkstra_path(G, start_node, list(nodes.keys())[1])
        for node in path:
            canvas.itemconfig(node, fill='green')
    except nx.NetworkXNoPath:
        messagebox.showwarning("Warning", "No path found.")

# Function to run Kruskal's algorithm
def run_kruskal():
    if len(nodes) < 2:
        messagebox.showwarning("Warning", "At least two nodes are required to run Kruskal's algorithm.")
        return
    try:
        mst = nx.minimum_spanning_tree(G)
        for edge in mst.edges():
            for e in edges:
                start_node, end_node = edge
                if (nodes[start_node], nodes[end_node]) in mst.edges() or (nodes[end_node], nodes[start_node]) in mst.edges():
                    canvas.itemconfig(e, fill='green')
    except nx.NetworkXError:
        messagebox.showwarning("Warning", "Error running Kruskal's algorithm.")

# Function to run BFS
def run_bfs():
    if len(nodes) < 2:
        messagebox.showwarning("Warning", "At least two nodes are required to run BFS.")
        return
    start_node = list(nodes.keys())[0]
    try:
        path = list(nx.bfs_edges(G, start_node))
        for edge in path:
            start_node, end_node = edge
            for e in edges:
                if (nodes[start_node], nodes[end_node]) in path or (nodes[end_node], nodes[start_node]) in path:
                    canvas.itemconfig(e, fill='green')
    except nx.NetworkXError:
        messagebox.showwarning("Warning", "Error running BFS.")

# Function to run DFS
def run_dfs():
    if len(nodes) < 2:
        messagebox.showwarning("Warning", "At least two nodes are required to run DFS.")
        return
    start_node = list(nodes.keys())[0]
    try:
        path = list(nx.dfs_edges(G, start_node))
        for edge in path:
            start_node, end_node = edge
            for e in edges:
                if (nodes[start_node], nodes[end_node]) in path or (nodes[end_node], nodes[start_node]) in path:
                    canvas.itemconfig(e, fill='green')
    except nx.NetworkXError:
        messagebox.showwarning("Warning", "Error running DFS.")

# Buttons to run algorithms
dijkstra_button = tk.Button(root, text="Run Dijkstra", command=run_dijkstra)
dijkstra_button.pack()

kruskal_button = tk.Button(root, text="Run Kruskal", command=run_kruskal)
kruskal_button.pack()

bfs_button = tk.Button(root, text="Run BFS", command=run_bfs)
bfs_button.pack()

dfs_button = tk.Button(root, text="Run DFS", command=run_dfs)
dfs_button.pack()

root.mainloop()