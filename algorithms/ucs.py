"""
Uniform Cost Search (UCS) Algorithm for Amravati Route Optimization
────────────────────────────────────────────────────────────────────
UCS expands nodes in order of their path cost from the source.
It finds the OPTIMAL path (minimum total cost) without heuristics.

Unlike A*, UCS explores in all directions equally — guaranteeing
optimal cost but potentially exploring more nodes than A*.
"""

import heapq
import networkx as nx
from typing import Optional, Dict, List


def ucs_algorithm(
    G: nx.MultiDiGraph,
    source: int,
    target: int,
    weight: str = "length"
) -> Dict:
    """
    Uniform Cost Search (Dijkstra-style) Implementation.

    UCS is essentially Dijkstra's algorithm — it always expands
    the lowest-cost frontier node, guaranteeing optimality.

    Args:
        G: NetworkX MultiDiGraph (Amravati road network)
        source: Source node ID
        target: Target node ID
        weight: Edge attribute to use ('length' = meters)

    Returns:
        dict with keys: success, path, distance, nodes_explored
    """

    # Priority queue: (cost, tie_breaker, node)
    frontier = []
    counter = 0

    # Initial state
    heapq.heappush(frontier, (0.0, counter, source))
    counter += 1

    # Best cost to reach each node
    cost_so_far: Dict[int, float] = {source: 0.0}

    # Parent tracking for path reconstruction
    came_from: Dict[int, Optional[int]] = {source: None}

    # Explored set
    explored = set()
    nodes_explored = 0

    while frontier:
        # Pop lowest-cost node
        current_cost, _, current = heapq.heappop(frontier)

        # Skip if already explored (stale entry in heap)
        if current in explored:
            continue

        explored.add(current)
        nodes_explored += 1

        # ── GOAL TEST ──
        if current == target:
            path = _reconstruct_path(came_from, current)
            total_dist = cost_so_far[target] / 1000.0  # meters → km
            return {
                "success": True,
                "path": path,
                "distance": total_dist,
                "nodes_explored": nodes_explored
            }

        # ── EXPAND ──
        for neighbor in G.neighbors(current):
            if neighbor in explored:
                continue

            # Get minimum edge weight for multi-edges
            edge_data = G.get_edge_data(current, neighbor)
            if edge_data is None:
                continue

            min_weight = min(
                d.get(weight, 1.0) for d in edge_data.values()
            )

            new_cost = current_cost + min_weight

            # Only add if we found a cheaper path
            if new_cost < cost_so_far.get(neighbor, float("inf")):
                cost_so_far[neighbor] = new_cost
                came_from[neighbor] = current
                heapq.heappush(frontier, (new_cost, counter, neighbor))
                counter += 1

    # No path found
    return {
        "success": False,
        "path": [],
        "distance": 0,
        "nodes_explored": nodes_explored
    }


def _reconstruct_path(came_from: Dict, current: int) -> List[int]:
    """Trace back the path from target to source."""
    path = []
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path
