"""
A* (A-Star) Algorithm for Amravati Delivery Route Optimization
─────────────────────────────────────────────────────────────
A* uses heuristic (straight-line distance to goal) + actual cost
to find the shortest path efficiently.

f(n) = g(n) + h(n)
  g(n) = cost from start to n
  h(n) = heuristic estimate from n to goal
"""

import heapq
import math
import networkx as nx
from typing import Optional, Dict, List, Tuple


def haversine_heuristic(G: nx.MultiDiGraph, u: int, v: int) -> float:
    """
    Haversine distance heuristic between two graph nodes.
    Returns distance in kilometers — admissible (never overestimates).
    """
    u_data = G.nodes[u]
    v_data = G.nodes[v]

    lat1 = math.radians(u_data.get("y", 0))
    lon1 = math.radians(u_data.get("x", 0))
    lat2 = math.radians(v_data.get("y", 0))
    lon2 = math.radians(v_data.get("x", 0))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return 6371 * c  # Earth radius in km


def astar_algorithm(
    G: nx.MultiDiGraph,
    source: int,
    target: int,
    weight: str = "length"
) -> Dict:
    """
    A* Search Algorithm Implementation.

    Args:
        G: NetworkX MultiDiGraph (Amravati road network)
        source: Source node ID
        target: Target node ID
        weight: Edge attribute to use as cost ('length' = meters)

    Returns:
        dict with keys: success, path, distance, nodes_explored
    """

    # Priority queue: (f_score, tie_breaker, node)
    open_heap = []
    counter = 0  # tie-breaker for equal f-scores

    # g_score[node] = best known cost from source to node
    g_score: Dict[int, float] = {source: 0.0}

    # f_score[node] = g_score + heuristic
    h0 = haversine_heuristic(G, source, target) * 1000  # convert to meters
    f_score: Dict[int, float] = {source: h0}

    # came_from: for path reconstruction
    came_from: Dict[int, Optional[int]] = {source: None}

    # Push source to heap
    heapq.heappush(open_heap, (f_score[source], counter, source))
    counter += 1

    # Closed set: already fully explored nodes
    closed_set = set()
    nodes_explored = 0

    while open_heap:
        # Pop node with lowest f_score
        _, _, current = heapq.heappop(open_heap)

        if current in closed_set:
            continue

        closed_set.add(current)
        nodes_explored += 1

        # ── GOAL TEST ──
        if current == target:
            path = _reconstruct_path(came_from, current)
            total_dist = g_score[target] / 1000.0  # meters → km
            return {
                "success": True,
                "path": path,
                "distance": total_dist,
                "nodes_explored": nodes_explored
            }

        # ── EXPAND NEIGHBORS ──
        for neighbor in G.neighbors(current):
            if neighbor in closed_set:
                continue

            # Get minimum edge weight (multiple edges possible in MultiDiGraph)
            edge_data = G.get_edge_data(current, neighbor)
            if edge_data is None:
                continue

            min_weight = min(
                d.get(weight, 1.0) for d in edge_data.values()
            )

            tentative_g = g_score[current] + min_weight

            if tentative_g < g_score.get(neighbor, float("inf")):
                # Better path found
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g

                h = haversine_heuristic(G, neighbor, target) * 1000
                f = tentative_g + h
                f_score[neighbor] = f

                heapq.heappush(open_heap, (f, counter, neighbor))
                counter += 1

    # No path found
    return {
        "success": False,
        "path": [],
        "distance": 0,
        "nodes_explored": nodes_explored
    }


def _reconstruct_path(came_from: Dict, current: int) -> List[int]:
    """Reconstruct path by tracing came_from map backwards."""
    path = []
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path
