import pytest

from modgeosys.graph.a_star import a_star, Hop
from modgeosys.graph.distance import manhattan_distance, euclidean_distance
from modgeosys.graph.types import Edge, Graph, NoNavigablePathError


def test_hop_creation():
    hop = Hop(Edge(weight=10.0, node_indices=frozenset((1, 2))), g=5.0, h=5.0)
    assert hop.edge == Edge(weight=10.0, node_indices=frozenset((1, 2)))
    assert hop.cached_f is None
    assert hop.g == 5.0
    assert hop.h == 5.0


def test_hop_f_calculation():
    hop = Hop(Edge(weight=10.0, node_indices=frozenset((1, 2))), g=5.0, h=5.0)
    assert hop.f() == 10.0
    assert hop.cached_f == 10.0


def test_hop_equality():
    hop1 = Hop(Edge(weight=10.0, node_indices=frozenset((1, 2))), g=5.0, h=5.0)
    hop2 = Hop(Edge(weight=10.0, node_indices=frozenset((1, 2))), g=5.0, h=5.0)
    assert hop1 == hop2


def test_a_star_finds_shortest_path_manhattan_graph1(valid_graph1):
    result = a_star(graph=valid_graph1, start_node_index=0, goal_node_index=4, heuristic_distance=manhattan_distance)

    assert len(result) == 2
    assert result == [Hop(Edge(weight=2.0, node_indices=frozenset({0, 1})), cached_f=5.0, g=2.0, h=3.0),
                      Hop(Edge(weight=3.0, node_indices=frozenset({1, 4})), cached_f=5.0, g=5.0, h=0.0)]


def test_a_star_find_shortest_path_manhattan_graph_from_edge_definitions(valid_graph_from_edge_definitions):
    result = a_star(graph=valid_graph_from_edge_definitions, start_node_index=0, goal_node_index=4, heuristic_distance=manhattan_distance)

    assert len(result) == 2
    assert result == [Hop(Edge(weight=2.0, node_indices=frozenset({0, 1})), cached_f=5.0, g=2.0, h=3.0),
                      Hop(Edge(weight=3.0, node_indices=frozenset({1, 4})), cached_f=5.0, g=5.0, h=0.0)]


def test_a_star_finds_shortest_path_manhattan_graph2(valid_graph2):
    result = a_star(graph=valid_graph2, start_node_index=0, goal_node_index=4, heuristic_distance=manhattan_distance)

    assert len(result) == 3
    assert result == [Hop(Edge(weight=1.0, node_indices=frozenset({0, 2})), cached_f=5.0, g=1.0, h=4.0),
                      Hop(Edge(weight=1.0, node_indices=frozenset({2, 3})), cached_f=4.0, g=2.0, h=2.0),
                      Hop(Edge(weight=1.0, node_indices=frozenset({3, 4})), cached_f=3.0, g=3.0, h=0.0)]


def test_a_star_with_no_path_manhattan(valid_nodes):
    with pytest.raises(NoNavigablePathError):
        a_star(graph=Graph(valid_nodes, ()), start_node_index=0, goal_node_index=3, heuristic_distance=manhattan_distance)


def test_a_star_with_single_node_path_manhattan():
    assert len(a_star(graph=Graph([(0.0, 0.0)], ()), start_node_index=0, goal_node_index=0, heuristic_distance=manhattan_distance)) == 0.0


def test_a_star_finds_shortest_path_manhattan_larger_graph(valid_graph_larger):
    result = a_star(graph=valid_graph_larger, start_node_index=0, goal_node_index=4, heuristic_distance=manhattan_distance)

    assert len(result) == 12
    assert result == [Hop(edge=Edge(weight=122.70985671734266, node_indices=frozenset({0, 15})), cached_f=1177.683043473936, g=122.70985671734266, h=1054.9731867565933),
                      Hop(edge=Edge(weight=122.70985671734266, node_indices=frozenset({0, 15})), cached_f=1181.2230308807814, g=245.41971343468532, h=935.8033174460961),
                      Hop(edge=Edge(weight=327.68612780977446, node_indices=frozenset({0, 3})), cached_f=1836.5952865003298, g=573.1058412444597, h=1263.4894452558701),
                      Hop(edge=Edge(weight=450.3598302610208, node_indices=frozenset({3, 15})), cached_f=2078.438858262074, g=1023.4656715054805, h=1054.9731867565933),
                      Hop(edge=Edge(weight=327.68612780977446, node_indices=frozenset({12, 15})), cached_f=2733.811113881623, g=1351.151799315255, h=1382.6593145663683),
                      Hop(edge=Edge(weight=450.3598302610208, node_indices=frozenset({0, 12})), cached_f=2737.3149470223716, g=1801.5116295762757, h=935.8033174460961),
                      Hop(edge=Edge(weight=327.68612780977446, node_indices=frozenset({0, 3})), cached_f=3392.6872026419205, g=2129.1977573860504, h=1263.4894452558701),
                      Hop(edge=Edge(weight=450.3598302610208, node_indices=frozenset({3, 15})), cached_f=3634.5307744036645, g=2579.557587647071, h=1054.9731867565933),
                      Hop(edge=Edge(weight=327.68612780977446, node_indices=frozenset({12, 15})), cached_f=4289.903030023213, g=2907.2437154568456, h=1382.6593145663683),
                      Hop(edge=Edge(weight=450.3598302610208, node_indices=frozenset({0, 12})), cached_f=4293.406863163962, g=3357.6035457178664, h=935.8033174460961),
                      Hop(edge=Edge(weight=830.5744457304638, node_indices=frozenset({0, 1})), cached_f=4293.406863163963, g=4188.17799144833, h=105.22887171563275),
                      Hop(edge=Edge(weight=101.79769950915306, node_indices=frozenset({1, 4})), cached_f=4289.9756909574835, g=4289.9756909574835, h=0.0)]

def test_a_star_finds_shortest_path_with_string_edge_weights(valid_graph_larger_with_string_edge_weights):
    assert type(valid_graph_larger_with_string_edge_weights.edges[0].weight) == str

    # This is the only way to test edge construction with string weights in edges pickled before the automatic weight conversion was implemented.
    for edge in valid_graph_larger_with_string_edge_weights.edges:
        edge.__post_init__()

    result = a_star(graph=valid_graph_larger_with_string_edge_weights, start_node_index=0, goal_node_index=4, heuristic_distance=manhattan_distance)

    assert len(result) == 12
    assert result == [Hop(edge=Edge(weight=122.70985671734266, node_indices=frozenset({0, 15})), cached_f=1177.683043473936, g=122.70985671734266, h=1054.9731867565933),
                      Hop(edge=Edge(weight=122.70985671734266, node_indices=frozenset({0, 15})), cached_f=1181.2230308807814, g=245.41971343468532, h=935.8033174460961),
                      Hop(edge=Edge(weight=327.68612780977446, node_indices=frozenset({0, 3})), cached_f=1836.5952865003298, g=573.1058412444597, h=1263.4894452558701),
                      Hop(edge=Edge(weight=450.3598302610208, node_indices=frozenset({3, 15})), cached_f=2078.438858262074, g=1023.4656715054805, h=1054.9731867565933),
                      Hop(edge=Edge(weight=327.68612780977446, node_indices=frozenset({12, 15})), cached_f=2733.811113881623, g=1351.151799315255, h=1382.6593145663683),
                      Hop(edge=Edge(weight=450.3598302610208, node_indices=frozenset({0, 12})), cached_f=2737.3149470223716, g=1801.5116295762757, h=935.8033174460961),
                      Hop(edge=Edge(weight=327.68612780977446, node_indices=frozenset({0, 3})), cached_f=3392.6872026419205, g=2129.1977573860504, h=1263.4894452558701),
                      Hop(edge=Edge(weight=450.3598302610208, node_indices=frozenset({3, 15})), cached_f=3634.5307744036645, g=2579.557587647071, h=1054.9731867565933),
                      Hop(edge=Edge(weight=327.68612780977446, node_indices=frozenset({12, 15})), cached_f=4289.903030023213, g=2907.2437154568456, h=1382.6593145663683),
                      Hop(edge=Edge(weight=450.3598302610208, node_indices=frozenset({0, 12})), cached_f=4293.406863163962, g=3357.6035457178664, h=935.8033174460961),
                      Hop(edge=Edge(weight=830.5744457304638, node_indices=frozenset({0, 1})), cached_f=4293.406863163963, g=4188.17799144833, h=105.22887171563275),
                      Hop(edge=Edge(weight=101.79769950915306, node_indices=frozenset({1, 4})), cached_f=4289.9756909574835, g=4289.9756909574835, h=0.0)]

# TODO: Add tests for euclidean distance, and many more permutations of the above tests.
