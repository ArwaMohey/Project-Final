"""Time-step traffic simulation engine."""
from __future__ import annotations
from typing import Dict, List, Any
import networkx as nx

from src.algorithms.shortest_path import time_dependent_dijkstra

PERIODS = ["morning", "afternoon", "evening", "night"]


def simulate_period(G: nx.DiGraph,
                    demand: List[tuple],
                    period: str) -> Dict[str, Any]:
    """
    For each (src, dst, passengers) in the demand list, route via
    time-dependent Dijkstra and accumulate edge load.

    Returns served, unreachable, avg_minutes_per_pax, edge_load.
    """
    edge_load: Dict[tuple, float] = {}
    served      = 0
    unreachable = 0
    total_min   = 0.0

    for src, dst, pax in demand:
        if src not in G or dst not in G:
            unreachable += pax
            continue
        path, cost, _ = time_dependent_dijkstra(G, src, dst, period)
        if not path or cost == float("inf"):
            unreachable += pax
            continue
        served    += pax
        total_min += cost * pax
        for u, v in zip(path, path[1:]):
            edge_load[(u, v)] = edge_load.get((u, v), 0) + pax

    return {
        "period":               period,
        "served":               served,
        "unreachable":          unreachable,
        "avg_minutes_per_pax":  total_min / served if served else 0.0,
        "edge_load":            edge_load,
    }


def scenario_road_closure(G: nx.DiGraph,
                           closed_edges: List[tuple]) -> nx.DiGraph:
    """Return a copy of G with the given edges removed (both directions)."""
    H = G.copy()
    for u, v in closed_edges:
        if H.has_edge(u, v): H.remove_edge(u, v)
        if H.has_edge(v, u): H.remove_edge(v, u)
    return H


def scenario_accident(G: nx.DiGraph,
                       accident_edge: tuple,
                       severity: int = 5) -> nx.DiGraph:
    """
    Simulate an accident by multiplying the edge weight by `severity`.
    Affects both directions if present.
    """
    H = G.copy()
    u, v = accident_edge
    for a, b in [(u, v), (v, u)]:
        if H.has_edge(a, b):
            H[a][b]["weight"] *= severity
    return H


def run_full_day(G: nx.DiGraph, demand) -> Dict[str, Any]:
    """Run simulate_period for all four time periods."""
    return {p: simulate_period(G, demand, p) for p in PERIODS}