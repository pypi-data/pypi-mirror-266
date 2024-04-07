import numpy as np

from modgeosys.graph.types import Node, Edge


def test_node_creation():
    node = Node((0.0, 0.0))
    assert node.coordinates.all() == np.array([0.0, 0.0]).all()


def test_node_equality():
    node1 = Node((0.0, 0.0))
    node2 = Node((0.0, 0.0))
    assert node1 == node2


def test_node_inequality():
    node1 = Node((0.0, 0.0))
    node2 = Node((0.0, 1.0))
    assert node1 != node2


def test_edge_creation():
    edge = Edge(weight=10.0, node_indices=frozenset((1, 2)))
    assert edge.weight == 10.0
    assert edge.node_indices == frozenset((1, 2))


def test_edge_creation_with_int_weight():
    edge = Edge(weight=10, node_indices=frozenset((1, 2)))
    assert edge.weight == 10.0


def test_edge_creation_with_string_weight():
    edge = Edge(weight='10.0', node_indices=frozenset((1, 2)))
    assert edge.weight == 10.0


def test_edge_index_of_other_node():
    edge = Edge(weight=10.0, node_indices=frozenset((1, 2)))
    assert edge.index_of_other_node(1) == 2
    assert edge.index_of_other_node(2) == 1


def test_edge_equality():
    edge1 = Edge(weight=10.0, node_indices=frozenset((1, 2)))
    edge2 = Edge(weight=10.0, node_indices=frozenset((1, 2)))
    assert edge1 == edge2


def test_edge_inequality():
    edge1 = Edge(weight=10.0, node_indices=frozenset((1, 2)))
    edge2 = Edge(weight=10.0, node_indices=frozenset((1, 3)))
    assert edge1 != edge2


def test_graph_creation(valid_nodes, valid_edges1, valid_graph1):
    assert valid_graph1.nodes == valid_nodes
    assert valid_graph1.edges == valid_edges1


def test_graph_creation_from_edge_definitions(valid_graph_from_edge_definitions, valid_nodes, valid_edges1):
    assert valid_graph_from_edge_definitions.nodes == valid_nodes
    assert valid_graph_from_edge_definitions.edges == valid_edges1

def test_graph_adjacency_map(valid_graph1):
    adjacency_map = valid_graph1.adjacency_map()
    assert adjacency_map == {Node((0.0, 0.0)): [Edge(weight=1, node_indices=frozenset((0, 2))), Edge(weight=2, node_indices=frozenset((0, 1)))],
                             Node((0.0, 2.0)): [Edge(weight=2, node_indices=frozenset((0, 1))), Edge(weight=3, node_indices=frozenset((1, 4)))],
                             Node((1.0, 0.0)): [Edge(weight=1, node_indices=frozenset((0, 2))), Edge(weight=1, node_indices=frozenset((2, 3)))],
                             Node((2.0, 1.0)): [Edge(weight=1, node_indices=frozenset((2, 3))), Edge(weight=1, node_indices=frozenset((3, 4)))],
                             Node((2.0, 3.0)): [Edge(weight=1, node_indices=frozenset((3, 4))), Edge(weight=3, node_indices=frozenset((1, 4)))]}


def test_graph_adjacency_matrix(valid_graph1):
    graph = valid_graph1
    adjacency_matrix = graph.adjacency_matrix()
    assert adjacency_matrix.all() == np.array([[np.inf,    2.0,    1.0, np.inf, np.inf],
                                               [   2.0, np.inf, np.inf, np.inf,      3],
                                               [   1.0, np.inf, np.inf,    1.0, np.inf],
                                               [np.inf, np.inf,    1.0, np.inf,    1.0],
                                               [np.inf,    3.0, np.inf,    1.0, np.inf]]).all()
