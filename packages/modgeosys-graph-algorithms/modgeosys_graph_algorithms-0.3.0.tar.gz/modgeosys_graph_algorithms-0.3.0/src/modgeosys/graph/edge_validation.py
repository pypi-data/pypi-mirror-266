"""Standard edge validation functions."""

from modgeosys.graph.types import Edge


def edge_is_always_valid(edge: Edge) -> bool:
    """All edges are valid."""
    return True