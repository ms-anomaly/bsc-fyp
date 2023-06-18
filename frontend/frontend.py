import random

import networkx as nx
import matplotlib.pyplot as plt

def drawServiceGraph(adj_matrix, labels, node_clr, path):
    plt.figure(figsize=(10, 10))  # Adjust the figure size if needed

    # Create an empty graph
    graph = nx.DiGraph()

    # Add nodes to the graph
    num_nodes = len(adj_matrix)
    graph.add_nodes_from(labels)

    # Add edges to the graph based on the adjacency matrix
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            if adj_matrix[i][j] == 1:
                graph.add_edge(labels[i], labels[j])

    # Draw the graph
    random.seed(42) # To produce the same node position for every run
    # pos = nx.spring_layout(graph, k=10)  # Determine the position of nodes
    pos = nx.circular_layout(graph, scale=4)  # Determine the position of nodes
    # pos = nx.nx_pydot.graphviz_layout(graph, prog='neato')  # Determine the position of nodes
    nx.draw_networkx_nodes(graph, pos, node_size=4000, node_color=[node_clr[node] for node in graph.nodes()])
    nx.draw_networkx_edges(graph, pos)
    nx.draw_networkx_labels(graph, pos)

    plt.title("Service Graph")
    plt.axis("off")
    plt.savefig(path)
    plt.close()
