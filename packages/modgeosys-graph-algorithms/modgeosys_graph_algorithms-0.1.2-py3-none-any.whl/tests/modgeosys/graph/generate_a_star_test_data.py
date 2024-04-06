import numpy as np
import networkx as nx

def generate_dataset(num_samples):
    dataset = []
    for _ in range(num_samples):
        # Create a random graph
        G = nx.grid_2d_graph(np.random.randint(3, 6), np.random.randint(3, 6))
        for u, v, d in G.edges(data=True):
            d['weight'] = np.random.randint(1, 10)  # Assign random weights
        for n in G.nodes:
            G.nodes[n]['pos'] = n  # Assign positions as node labels for Manhattan distance

        # Choose random start and end nodes
        nodes = list(G.nodes())
        np.random.shuffle(nodes)
        start, end = nodes[:2]
        path_edges = a_star_algorithm(G, start, end)

        dataset.append({
            'graph': nx.node_link_data(G),
            'start': start,
            'end': end,
            'path_edges': path_edges
        })

    return dataset


# Generate a dataset of 5 samples
dataset = generate_dataset(5)
dataset[0]  # Display the first sample from the dataset
