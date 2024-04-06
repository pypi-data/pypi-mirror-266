import pytest

from modgeosys.graph.a_star import a_star, Hop
from modgeosys.graph.distance import manhattan_distance, euclidean_distance
from modgeosys.graph.types import Edge, Graph, NoNavigablePathError


def test_hop_creation():
    hop = Hop(Edge(weight=10.0, node_indices=frozenset((1, 2))), g=5.0, h=5.0)
    assert hop.edge == Edge(weight=10.0, node_indices=frozenset((1, 2)))
    assert hop.g == 5.0
    assert hop.h == 5.0


def test_hop_f_calculation():
    hop = Hop(Edge(weight=10.0, node_indices=frozenset((1, 2))), g=5.0, h=5.0)
    assert hop.f() == 10.0


def test_hop_equality():
    hop1 = Hop(Edge(weight=10.0, node_indices=frozenset((1, 2))), g=5.0, h=5.0)
    hop2 = Hop(Edge(weight=10.0, node_indices=frozenset((1, 2))), g=5.0, h=5.0)
    assert hop1 == hop2


def test_a_star_finds_shortest_path_manhattan_graph1(valid_graph1):
    result = a_star(graph=valid_graph1, start_node_index=0, goal_node_index=4, heuristic_distance=manhattan_distance)

    assert len(result) == 2
    assert result == [Hop(Edge(weight=2.0, node_indices=frozenset({0, 1})), g=2.0, h=3.0),
                      Hop(Edge(weight=3.0, node_indices=frozenset({1, 4})), g=5.0, h=0.0)]


def test_a_star_finds_shortest_path_manhattan_graph2(valid_graph2):
    result = a_star(graph=valid_graph2, start_node_index=0, goal_node_index=4, heuristic_distance=manhattan_distance)

    assert len(result) == 3
    assert result == [Hop(Edge(weight=1.0, node_indices=frozenset({0, 2})), g=1.0, h=4.0),
                      Hop(Edge(weight=1.0, node_indices=frozenset({2, 3})), g=2.0, h=2.0),
                      Hop(Edge(weight=1.0, node_indices=frozenset({3, 4})), g=3.0, h=0.0)]


def test_a_star_with_no_path_manhattan(valid_nodes):
    with pytest.raises(NoNavigablePathError):
        a_star(graph=Graph(valid_nodes, ()), start_node_index=0, goal_node_index=3, heuristic_distance=manhattan_distance)


def test_a_star_with_single_node_path_manhattan():
    assert len(a_star(graph=Graph([(0.0, 0.0)], ()), start_node_index=0, goal_node_index=0, heuristic_distance=manhattan_distance)) == 0.0


# TODO: Add tests for euclidean distance, and many more permutations of the above tests.
