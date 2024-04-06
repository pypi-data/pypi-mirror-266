import pytest

from modgeosys.graph.prim import prim
from modgeosys.graph.types import Edge


def test_prim_finds_minimum_spanning_tree(valid_graph1):
    result = prim(graph=valid_graph1, start_node_index=0)

    assert len(result) == 4
    assert result == {Edge(weight=2.0, node_indices=frozenset({0, 1})),
                      Edge(weight=1.0, node_indices=frozenset({0, 2})),
                      Edge(weight=1.0, node_indices=frozenset({2, 3})),
                      Edge(weight=1.0, node_indices=frozenset({3, 4}))}
    assert sum(edge.weight for edge in result) == 5.0
