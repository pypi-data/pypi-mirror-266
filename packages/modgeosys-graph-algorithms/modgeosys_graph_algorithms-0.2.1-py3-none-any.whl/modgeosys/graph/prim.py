"""A module containing an implementation of Prim's algorithm for finding the minimum spanning tree of a graph."""

from modgeosys.graph.types import Edge, Graph, ValidEdgeCallable, NoNavigablePathError
from modgeosys.graph.edge_validation import edge_is_always_valid


def prim(graph: Graph, start_node_index: int, edge_is_valid: ValidEdgeCallable = edge_is_always_valid) -> set[Edge]:
    """Implement Prim's algorithm for finding the minimum spanning tree of a graph."""

    nodes = graph.nodes
    edges = graph.edges

    included_node_indices = {start_node_index}
    excluded_node_indices = set(range(len(nodes))) - included_node_indices

    included_edges = set()
    excluded_edges = set(edges)

    while excluded_node_indices:

        candidate_edges = sorted(edge for edge in excluded_edges if edge.node_indices & included_node_indices)
        best_edge = None

        for edge in candidate_edges:

            if edge_is_valid(edge):

                best_edge = edge
                indices = best_edge.node_indices - included_node_indices
                if len(indices) != 1:
                    # We've discovered a cycle.  Remove the edge from consideration, and move on.
                    excluded_edges.remove(best_edge)
                    continue
                new_node_index = next(iter(indices))

                included_node_indices.add(new_node_index)
                excluded_node_indices.remove(new_node_index)
                included_edges.add(best_edge)
                excluded_edges.remove(best_edge)

                break

        if not best_edge:
            raise NoNavigablePathError(start_node=nodes[start_node_index])

    return included_edges
