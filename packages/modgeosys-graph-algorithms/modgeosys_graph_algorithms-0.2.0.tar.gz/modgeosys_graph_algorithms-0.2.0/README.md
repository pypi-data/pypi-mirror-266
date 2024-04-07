# modgeosys-graph-algorithms: Graph Algorithms

A repository for [hopefully] clean, readable, and easily-called implementations of some navigation,
path planning, and obstacle avoidance algorithms I will be using in the near future, written in modern
Python and/or Rust with Python bindings. I'll be adding more algorithm implementations over time.

## Algorithms: Currently implemented + planned
* [A*](https://en.wikipedia.org/wiki/A*_search_algorithm) - Graph path search algorithm.
  * Code-complete in both Python and Rust.
  * Needs a more thorough test suite.
  * Needs Python bindings for Rust implementation.
* [Prim's algorithm](https://en.wikipedia.org/wiki/Prim's_algorithm) - Prim's Minimum Spanning Tree algorithm.
  * Code-complete in Python.
  * Tested on toy dataset in test suite.
  * Tested on larger sample (pickled) dataset, not yet incorporated into test suite.
  * Needs a Rust implementation and corresponding Python bindings.

## Usage

### A\*

```python
import pickle
from pprint import pprint

from modgeosys.graph.types import Node, Edge, Graph
from modgeosys.graph.distance import manhattan_distance, euclidean_distance
from modgeosys.graph.a_star import a_star

# Define a toy graph.
nodes = [Node(coordinates=(0.0, 0.0)),
         Node(coordinates=(0.0, 2.0)),
         Node(coordinates=(1.0, 0.0)),
         Node(coordinates=(2.0, 1.0)),
         Node(coordinates=(2.0, 3.0))]
edges = (Edge(weight=2.0, node_indices=frozenset((0, 1))),
         Edge(weight=1.0, node_indices=frozenset((0, 2))),
         Edge(weight=1.0, node_indices=frozenset((2, 3))),
         Edge(weight=3.0, node_indices=frozenset((1, 4))),
         Edge(weight=1.0, node_indices=frozenset((3, 4))))
toy_graph = Graph(nodes=nodes, edges=edges)

# Load a bigger graph from a pickle file.
with open('python/data/graph.pickle', 'rb') as pickled_sample_larger_graph_file:
    larger_graph = pickle.load(pickled_sample_larger_graph_file)

# Call the A* function.
toy_a_star_path = a_star(graph=toy_graph, start_node_index=0, goal_node_index=4, heuristic_distance=manhattan_distance)
print(f'Toy A* Path:')
pprint(toy_a_star_path)
print()
larger_a_star_path = a_star(graph=larger_graph, start_node_index=0, goal_node_index=4, heuristic_distance=manhattan_distance)
print(f'Large A* Path:')
pprint(larger_a_star_path)
```

### Prim's algorithm

```python
import pickle

from modgeosys.graph.types import Node, Edge, Graph
from modgeosys.graph.prim import prim

# Define a toy graph.
nodes = [Node(coordinates=(0.0, 0.0)),
         Node(coordinates=(0.0, 2.0)),
         Node(coordinates=(1.0, 0.0)),
         Node(coordinates=(2.0, 1.0)),
         Node(coordinates=(2.0, 3.0))]
edges = (Edge(weight=2.0, node_indices=frozenset((0, 1))),
         Edge(weight=1.0, node_indices=frozenset((0, 2))),
         Edge(weight=1.0, node_indices=frozenset((2, 3))),
         Edge(weight=3.0, node_indices=frozenset((1, 4))),
         Edge(weight=1.0, node_indices=frozenset((3, 4))))
toy_graph = Graph(nodes=nodes, edges=edges)

# Load a bigger graph from a pickle file.
with open('python/data/graph.pickle', 'rb') as pickled_sample_larger_graph_file:
    larger_graph = pickle.load(pickled_sample_larger_graph_file)

# Call the Prim function.
toy_minimum_spanning_tree = prim(graph=toy_graph, start_node_index=0)
print('Toy Prim Minimum Spanning Tree:')
print(toy_minimum_spanning_tree)
print()
larger_minimum_spanning_tree = prim(graph=larger_graph, start_node_index=0)
print('Prim Minimum Spanning Tree:')
print(larger_minimum_spanning_tree)
```