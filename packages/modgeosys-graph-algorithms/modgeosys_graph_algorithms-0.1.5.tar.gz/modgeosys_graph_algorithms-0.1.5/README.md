# modgeosys-graph-algorithms: Graph Algorithms

A repository for [hopefully] clean, readable, and easily-called implementations of some navigation,
path planning, and obstacle avoidance algorithms I will be using in the near future, written in modern
Python and/or Rust with Python bindings. I'll be adding more algorithm implementations over time.

## Algorithms: Currently implemented + planned
* [A*](https://en.wikipedia.org/wiki/A*_search_algorithm) - Graph path search algorithm.
  * Code-complete in both Python and Rust.
  * Needs a more thorough test suite.
* [Prim's algorithm](https://en.wikipedia.org/wiki/Prim's_algorithm) - Prim's Minimum Spanning Tree algorithm.
  * Code-complete in Python.
  * Tested on toy dataset in test suite.
  * Tested on larger sample (pickled) dataset, not yet incorporated into test suite.

## Usage

### A\*

#### Python

```python
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

# Call the A* function.
path = a_star(graph=toy_graph, start_node_index=0, goal_node_index=4, heuristic_distance=manhattan_distance)
print(f'A* Path:')
pprint(path)
print()
```

#### Rust
```rust
use std::collections::HashSet;

use modgeosys_graph::a_star::a_star;
use modgeosys_graph::types::{Node, Edge, Graph};
use modgeosys_graph::distance::manhattan_distance;

fn main()
{
  // Define a graph.
  let nodes = vec![Node::new(vec![0.0, 0.0]),
                   Node::new(vec![0.0, 2.0]),
                   Node::new(vec![1.0, 0.0]),
                   Node::new(vec![2.0, 1.0]),
                   Node::new(vec![2.0, 3.0])];
  let edges = vec![Edge::new(2.0, HashSet::from([0, 1])),
                   Edge::new(1.0, HashSet::from([0, 2])),
                   Edge::new(1.0, HashSet::from([2, 3])),
                   Edge::new(3.0, HashSet::from([1, 4])),
                   Edge::new(1.0, HashSet::from([3, 4]))];
  let graph = Graph::new(nodes, edges);

  // Call the A* function.
  let path = a_star(&graph, 0, 4, manhattan_distance).unwrap();

  // Report the resulting path.
  println!("{:?}", path);
}
```

### Prim's algorithm

#### Python

```python
import pickle
from pprint import pprint

from modgeosys.graph.types import Node, Edge, Graph
from modgeosys.graph.distance import manhattan_distance, euclidean_distance

from modgeosys.graph.prim import prim

# Load a bigger graph from a pickle file.
with open('python/data/graph.pickle', 'rb') as f:
    larger_graph = pickle.load(f)

# Call the Prim function.
minimum_spanning_tree = prim(graph=larger_graph, start_node_index=0)
print('Prim Minimum Spanning Tree:')
print(minimum_spanning_tree)
```