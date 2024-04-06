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
