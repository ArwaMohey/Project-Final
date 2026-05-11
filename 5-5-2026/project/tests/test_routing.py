"""
tests/test_routing.py
=====================
Tests for Member 3 — Routing & Traffic Module (Dijkstra)
Covers: Dijkstra, time-dependent weights, road closures,
        alternate paths, memoized router, congestion-aware routing.
"""
import math
import pytest
import networkx as nx

from data.loader import load_dataset
from algorithms.shortest_path import (
    dijkstra,
    time_dependent_dijkstra,
    time_dependent_weight,
    MemoizedRouter,
)
from simulation import scenario_road_closure


# ──────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def DS():
    return load_dataset()

@pytest.fixture(scope="module")
def G(DS):
    return DS["graph_existing"]


# ──────────────────────────────────────────────────────────────
# 1. Dijkstra — basic correctness
# ──────────────────────────────────────────────────────────────

class TestDijkstraBasic:
    def test_path_exists_between_known_nodes(self, G):
        path, cost, stats = dijkstra(G, 12, "F1")  # Helwan → Airport
        assert path, "Expected a path"
        assert path[0] == 12 and path[-1] == "F1"
        assert cost < math.inf

    def test_path_starts_and_ends_correctly(self, G):
        path, _, _ = dijkstra(G, 1, 4)   # Maadi → New Cairo
        assert path[0] == 1 and path[-1] == 4

    def test_path_is_continuous(self, G):
        path, _, _ = dijkstra(G, 3, 13)  # Downtown → NAC
        for i in range(len(path) - 1):
            assert G.has_edge(path[i], path[i + 1]), \
                f"Gap in path: {path[i]} → {path[i+1]}"

    def test_single_node_path(self, G):
        path, cost, _ = dijkstra(G, 3, 3)
        assert path == [3] and cost == 0.0

    def test_no_path_returns_empty(self, G):
        # Add an isolated node
        H = G.copy()
        H.add_node(9999, kind="district", name="Ghost", pop=0,
                   type="Test", x=31.0, y=30.0)
        path, cost, _ = dijkstra(H, 3, 9999)
        assert path == [] and cost == math.inf

    def test_cost_is_positive(self, G):
        _, cost, _ = dijkstra(G, 8, "F9")  # Giza → Hospital
        assert cost > 0

    def test_visited_nodes_count_positive(self, G):
        _, _, stats = dijkstra(G, 3, 5)
        assert stats["visited"] > 0

    def test_complexity_label(self, G):
        _, _, stats = dijkstra(G, 1, 2)
        assert "(V+E)" in stats["complexity"]

    def test_custom_weight_function(self, G):
        # Route using only distance (in km) as weight
        path, cost, _ = dijkstra(G, 1, 4,
                                  weight_fn=lambda u, v, d: d["distance"])
        assert path[0] == 1 and path[-1] == 4

    def test_all_node_pairs_reachable(self, G):
        nodes = list(G.nodes())[:8]  # Sample 8 nodes
        for src in nodes:
            for dst in nodes:
                if src == dst:
                    continue
                _, cost, _ = dijkstra(G, src, dst)
                assert cost < math.inf, f"No path {src} → {dst}"


# ──────────────────────────────────────────────────────────────
# 2. Time-dependent weights
# ──────────────────────────────────────────────────────────────

class TestTimeDependentWeights:
    PERIODS = ["morning", "afternoon", "evening", "night"]

    def test_morning_heavier_than_night(self, G):
        _, cm, _ = time_dependent_dijkstra(G, 1, 4, "morning")
        _, cn, _ = time_dependent_dijkstra(G, 1, 4, "night")
        assert cn <= cm, "Night should be ≤ morning cost"

    def test_all_periods_produce_valid_paths(self, G):
        for p in self.PERIODS:
            path, cost, _ = time_dependent_dijkstra(G, 3, "F1", p)
            assert path and cost < math.inf, f"Failed for period {p}"

    def test_weight_fn_uses_correct_traffic(self, G):
        wfn_m = time_dependent_weight("morning")
        wfn_n = time_dependent_weight("night")
        u, v = 3, 5  # Downtown → Heliopolis
        if G.has_edge(u, v):
            wm = wfn_m(u, v, G[u][v])
            wn = wfn_n(u, v, G[u][v])
            assert wn <= wm

    def test_emergency_weight_ignores_congestion(self, G):
        wfn_normal    = time_dependent_weight("morning", is_emergency=False)
        wfn_emergency = time_dependent_weight("morning", is_emergency=True)
        u, v = 3, 5
        if G.has_edge(u, v):
            w_norm = wfn_normal(u, v, G[u][v])
            w_emrg = wfn_emergency(u, v, G[u][v])
            assert w_emrg <= w_norm  # Emergency should be faster

    def test_evening_heavier_than_afternoon(self, G):
        # Evening peaks are higher than afternoon in the dataset
        _, ce, _ = time_dependent_dijkstra(G, 4, 3, "evening")
        _, ca, _ = time_dependent_dijkstra(G, 4, 3, "afternoon")
        assert ca <= ce  # afternoon less congested

    def test_period_cost_variation(self, G):
        costs = {}
        for p in self.PERIODS:
            _, c, _ = time_dependent_dijkstra(G, 12, "F1", p)
            costs[p] = c
        # Not all periods should have identical costs
        assert len(set(costs.values())) > 1, "All periods have same cost — suspicious"


# ──────────────────────────────────────────────────────────────
# 3. Road closures & alternate paths
# ──────────────────────────────────────────────────────────────

class TestRoadClosures:
    def test_path_reroutes_around_closure(self, G):
        # Normal route may use 3→5; close it and ensure another path exists
        H = scenario_road_closure(G, [(3, 5)])
        assert not H.has_edge(3, 5)
        path, cost, _ = dijkstra(H, 3, "F1")
        assert path and cost < math.inf

    def test_closed_edge_not_in_path(self, G):
        H = scenario_road_closure(G, [(3, 5)])
        path, _, _ = dijkstra(H, 3, "F1")
        if path:
            edges_used = set(zip(path, path[1:]))
            assert (3, 5) not in edges_used

    def test_multiple_closures(self, G):
        H = scenario_road_closure(G, [(3, 5), (2, 3), (1, 3)])
        path, cost, _ = dijkstra(H, 12, "F1")
        # Graph still connected enough for a route to exist
        assert path and cost < math.inf

    def test_unreachable_after_bridge_removal(self, G):
        # Isolate node 6 (Zamalek) by removing all its edges
        H = G.copy()
        for nbr in list(H.successors(6)):
            H.remove_edge(6, nbr)
        for nbr in list(H.predecessors(6)):
            H.remove_edge(nbr, 6)
        path, cost, _ = dijkstra(H, 3, 6)
        assert path == [] and cost == math.inf


# ──────────────────────────────────────────────────────────────
# 4. Memoized router
# ──────────────────────────────────────────────────────────────

class TestMemoizedRouter:
    def test_cache_hit_on_second_call(self, G):
        r = MemoizedRouter(G)
        r.query(1, 4, "morning")
        r.query(1, 4, "morning")
        assert r.hits == 1 and r.misses == 1

    def test_different_period_is_cache_miss(self, G):
        r = MemoizedRouter(G)
        r.query(1, 4, "morning")
        r.query(1, 4, "evening")
        assert r.misses == 2 and r.hits == 0

    def test_same_result_from_cache(self, G):
        r = MemoizedRouter(G)
        p1, c1 = r.query(3, "F1", "morning")
        p2, c2 = r.query(3, "F1", "morning")
        assert p1 == p2 and c1 == c2

    def test_cache_independent_per_pair(self, G):
        r = MemoizedRouter(G)
        r.query(1, 4, "afternoon")
        r.query(3, 5, "afternoon")
        assert r.misses == 2

    def test_cache_grows_with_queries(self, G):
        r = MemoizedRouter(G)
        r.query(1, 4, "morning")
        r.query(1, 3, "morning")
        r.query(2, 5, "morning")
        assert len(r._cache) == 3


# ──────────────────────────────────────────────────────────────
# 5. Route planner sanity checks
# ──────────────────────────────────────────────────────────────

class TestRoutePlannerSanity:
    def test_route_to_airport_exists(self, G):
        path, cost, _ = dijkstra(G, 1, "F1")
        assert path and cost < math.inf

    def test_route_to_hospital_exists(self, G):
        path, cost, _ = dijkstra(G, 7, "F9")
        assert path and cost < math.inf

    def test_route_to_nac_exists(self, G):
        path, cost, _ = dijkstra(G, 3, 13)
        assert path and cost < math.inf

    def test_longer_route_via_hub(self, G):
        # Shortest path from Sheikh Zayed to NAC must pass through
        # some intermediate hub — verify path length > 2
        path, _, _ = dijkstra(G, 15, 13)
        assert len(path) > 2

    def test_cost_respects_triangle_inequality(self, G):
        _, c_13, _ = dijkstra(G, 1, 3)
        _, c_35, _ = dijkstra(G, 3, 5)
        _, c_15, _ = dijkstra(G, 1, 5)
        assert c_15 <= c_13 + c_35 + 1e-6  # allowing floating-point slack


if __name__ == "__main__":
    pytest.main([__file__, "-v"])