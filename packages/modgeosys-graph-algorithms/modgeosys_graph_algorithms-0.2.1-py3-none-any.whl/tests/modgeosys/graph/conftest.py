import pickle
import pytest

from src.modgeosys.graph.types import Node, Edge, Graph


@pytest.fixture
def valid_nodes():
    return [Node((0.0, 0.0)), Node((0.0, 2.0)), Node((1.0, 0.0)), Node((2.0, 1.0)), Node((2.0, 3.0))]


@pytest.fixture
def valid_edges1():
    return (Edge(weight=2, node_indices=frozenset((0, 1))),
            Edge(weight=1, node_indices=frozenset((0, 2))),
            Edge(weight=1, node_indices=frozenset((2, 3))),
            Edge(weight=3, node_indices=frozenset((1, 4))),
            Edge(weight=1, node_indices=frozenset((3, 4))))


@pytest.fixture
def valid_edges2():
    return (Edge(weight=3, node_indices=frozenset((0, 1))),
            Edge(weight=1, node_indices=frozenset((0, 2))),
            Edge(weight=1, node_indices=frozenset((2, 3))),
            Edge(weight=3, node_indices=frozenset((1, 4))),
            Edge(weight=1, node_indices=frozenset((3, 4))))


@pytest.fixture
def valid_graph1(valid_nodes, valid_edges1):
    return Graph(valid_nodes, valid_edges1)


@pytest.fixture
def valid_graph2(valid_nodes, valid_edges2):
    return Graph(valid_nodes, valid_edges2)


@pytest.fixture
def valid_graph_from_edge_definitions():
    return Graph.from_edge_definitions(((2, ((0.0, 0.0), (0.0, 2.0))),
                                        (1, ((0.0, 0.0), (1.0, 0.0))),
                                        (1, ((1.0, 0.0), (2.0, 1.0))),
                                        (3, ((0.0, 2.0), (2.0, 3.0))),
                                        (1, ((2.0, 1.0), (2.0, 3.0)))))


@pytest.fixture
def valid_graph_larger():
    with open('data/graph.pickle', 'rb') as pickled_sample_larger_graph_file:
        return pickle.load(pickled_sample_larger_graph_file)


@pytest.fixture
def valid_graph_larger_with_string_edge_weights():
    with open('data/graph_with_string_edge_weights.pickle', 'rb') as pickled_sample_larger_graph_file:
        return pickle.load(pickled_sample_larger_graph_file)