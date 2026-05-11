"""Build a NetworkX graph from the Cairo dataset."""
from __future__ import annotations
import math
from typing import Dict, Any
import networkx as nx

from . import cairo_data as D


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in kilometres between two lat/lon points."""
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(min(1.0, a)))


def edge_weight(distance_km: float, capacity: int, condition: int,
                traffic: float = 0.0) -> float:
    """
    Composite travel-time proxy (minutes).
    Lower is better.  Penalises bad condition and congestion.
    """
    cond = max(1, min(10, condition))
    cap = max(1, capacity)
    # Effective speed degrades with poor condition
    speed_kmh = max(20.0, 60.0 - 4 * (10 - cond))
    base_time_min = (distance_km / speed_kmh) * 60.0
    congestion_ratio = min(traffic / cap, 1.0)
    return base_time_min * (1.0 + 0.6 * congestion_ratio) + (10 - cond) * 0.4


def build_graph(include_potential: bool = False) -> nx.DiGraph:
    """
    Returns a directed graph (each undirected road becomes two arcs).

    Node attributes : kind ('district'|'facility'), name, pop, type, x, y
    Edge attributes : distance, capacity, condition, weight, kind
                      ('existing'|'potential'), cost (for potential),
                      traffic (dict period -> vph)
    """
    G = nx.DiGraph()

    for nid, name, pop, typ, x, y in D.NEIGHBORHOODS:
        G.add_node(nid, kind="district", name=name, pop=pop, type=typ, x=x, y=y)

    for fid, name, typ, x, y in D.FACILITIES:
        G.add_node(fid, kind="facility", name=name, pop=0, type=typ, x=x, y=y)

    def _add_edge(u, v, dist, cap, cond, kind, cost=0.0):
        flow = D.TRAFFIC_FLOW.get((u, v)) or D.TRAFFIC_FLOW.get((v, u))
        if flow:
            traffic_dict = dict(zip(D.TIME_PERIODS, flow))
        else:
            traffic_dict = {p: cap * 0.4 for p in D.TIME_PERIODS}
        avg_traffic = sum(traffic_dict.values()) / len(traffic_dict)
        w = edge_weight(dist, cap, cond, avg_traffic)
        G.add_edge(u, v, distance=dist, capacity=cap, condition=cond,
                   weight=w, kind=kind, cost=cost, traffic=traffic_dict)

    for u, v, dist, cap, cond in D.EXISTING_ROADS:
        _add_edge(u, v, dist, cap, cond, "existing")
        _add_edge(v, u, dist, cap, cond, "existing")

    if include_potential:
        for u, v, dist, cap, cost in D.POTENTIAL_ROADS:
            _add_edge(u, v, dist, cap, 10, "potential", cost=cost)
            _add_edge(v, u, dist, cap, 10, "potential", cost=cost)

    return G


def load_dataset() -> Dict[str, Any]:
    """Return a dict with both graphs and all raw tables."""
    return {
        "graph_existing":  build_graph(False),
        "graph_full":      build_graph(True),
        "neighborhoods":   D.NEIGHBORHOODS,
        "facilities":      D.FACILITIES,
        "existing_roads":  D.EXISTING_ROADS,
        "potential_roads": D.POTENTIAL_ROADS,
        "traffic_flow":    D.TRAFFIC_FLOW,
        "metro_lines":     D.METRO_LINES,
        "metro_routes":    D.METRO_ROUTES,
        "bus_routes":      D.BUS_ROUTES,
        "transit_demand":  D.TRANSIT_DEMAND,
        "time_periods":    D.TIME_PERIODS,
    }