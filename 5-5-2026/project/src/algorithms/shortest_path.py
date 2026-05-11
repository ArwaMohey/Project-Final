"""
Shortest-path algorithms.

Includes:
    * dijkstra              — classic, generic weight key
    * a_star                — A* with great-circle (haversine) heuristic in MIN
                              (admissible because weight is roughly travel time)
    * time_dependent_dijkstra — weights recomputed per time period
    * memoized_route        — DP-style memoization for repeated queries
"""
from __future__ import annotations
from typing import Callable, Dict, List, Tuple, Any, Optional
import heapq
import math
import networkx as nx

from src.data.loader import haversine_km, edge_weight


# ---------------------------------------------------------------------------
# Dijkstra  —  O((V + E) log V)
# ---------------------------------------------------------------------------

def dijkstra(G: nx.DiGraph, src, dst,
             weight_fn: Optional[Callable[[Any, Any, dict], float]] = None
             ) -> Tuple[List, float, dict]:
    """
    Returns (path, total_cost, stats).
    Complexity: O((V + E) log V) with a binary heap.
    """
    if weight_fn is None:
        weight_fn = lambda u, v, d: d["weight"]

    dist: Dict[Any, float] = {src: 0.0}
    prev: Dict[Any, Any] = {}
    pq = [(0.0, src)]
    visited = 0

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist.get(u, math.inf):
            continue
        visited += 1
        if u == dst:
            break
        for v in G.successors(u):
            w = weight_fn(u, v, G[u][v])
            nd = d + w
            if nd < dist.get(v, math.inf):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))

    if dst not in dist:
        return [], math.inf, {"visited": visited, "complexity": "O((V+E) log V)"}

    path = [dst]
    while path[-1] != src:
        path.append(prev[path[-1]])
    path.reverse()
    return path, dist[dst], {"visited": visited, "complexity": "O((V+E) log V)"}


# ---------------------------------------------------------------------------
# A*  —  O((V + E) log V), heuristic-guided
# ---------------------------------------------------------------------------

def a_star(G: nx.DiGraph, src, dst,
           weight_fn: Optional[Callable[[Any, Any, dict], float]] = None
           ) -> Tuple[List, float, dict]:
    """
    Heuristic: haversine distance / MAX_SPEED → minutes (admissible).
    Guarantees the same optimal cost as Dijkstra while expanding fewer nodes.
    """
    if weight_fn is None:
        weight_fn = lambda u, v, d: d["weight"]

    MAX_SPEED_KMH = 90.0

    def h(n) -> float:
        a = G.nodes[n]
        b = G.nodes[dst]
        km = haversine_km(a["y"], a["x"], b["y"], b["x"])
        return km / MAX_SPEED_KMH * 60.0  # minutes

    g: Dict[Any, float] = {src: 0.0}
    prev: Dict[Any, Any] = {}
    # heap entries: (f, g_cost, node)
    pq = [(h(src), 0.0, src)]
    visited = 0

    while pq:
        f, gu, u = heapq.heappop(pq)
        if gu > g.get(u, math.inf):
            continue
        visited += 1
        if u == dst:
            path = [dst]
            while path[-1] != src:
                path.append(prev[path[-1]])
            path.reverse()
            return path, gu, {
                "visited": visited,
                "complexity": "O((V+E) log V), heuristic-guided",
            }
        for v in G.successors(u):
            w = weight_fn(u, v, G[u][v])
            ng = gu + w
            if ng < g.get(v, math.inf):
                g[v] = ng
                prev[v] = u
                heapq.heappush(pq, (ng + h(v), ng, v))

    return [], math.inf, {"visited": visited,
                          "complexity": "O((V+E) log V), heuristic-guided"}


# ---------------------------------------------------------------------------
# Time-dependent shortest path
# ---------------------------------------------------------------------------

# algorithms/shortest_path.py (Update the existing function)

def time_dependent_weight(period: str, is_emergency: bool = False):
    """Return a weight function that uses the given traffic period.
    If is_emergency is True, simulates signal preemption by bypassing congestion.
    """
    def _w(u, v, d):
        traffic = d["traffic"][period]
        if is_emergency:
            # Preemption clears the road: evaluate travel time without congestion delays
            return edge_weight(d["distance"], d["capacity"], d["condition"], 0.0)
        return edge_weight(d["distance"], d["capacity"], d["condition"], traffic)
    return _w

def time_dependent_dijkstra(G: nx.DiGraph, src, dst, period: str):
    """Dijkstra with time-dependent edge weights for the given period."""
    return dijkstra(G, src, dst, weight_fn=time_dependent_weight(period, is_emergency=False))

# ---------------------------------------------------------------------------
# Memoized route planner  —  DP cache for repeated queries
# ---------------------------------------------------------------------------

class MemoizedRouter:
    """Caches shortest paths between (src, dst, period) triples."""

    def __init__(self, G: nx.DiGraph):
        self.G = G
        self._cache: Dict[Tuple, Tuple[List, float]] = {}
        self.hits = 0
        self.misses = 0

    def query(self, src, dst, period: str = "afternoon") -> Tuple[List, float]:
        key = (src, dst, period)
        if key in self._cache:
            self.hits += 1
            return self._cache[key]
        self.misses += 1
        path, cost, _ = time_dependent_dijkstra(self.G, src, dst, period)
        self._cache[key] = (path, cost)
        return path, cost