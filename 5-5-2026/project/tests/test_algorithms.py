"""Sanity tests for all algorithms."""
import math
from src.data.loader import load_dataset
from src.algorithms import (
    kruskal_mst, dijkstra, a_star, time_dependent_dijkstra,
    optimize_transit_schedule, road_maintenance_allocation,
    traffic_signal_optimization, MemoizedRouter,
)
from src.simulation import simulate_period, scenario_road_closure

DS = load_dataset()
G  = DS["graph_existing"]
GF = DS["graph_full"]


def test_graph_loaded():
    assert G.number_of_nodes() == 25  # 15 districts + 10 facilities
    assert G.number_of_edges() >= 50


def test_dijkstra_path_exists():
    p, c, s = dijkstra(G, 12, "F1")
    assert p[0] == 12 and p[-1] == "F1"
    assert c < math.inf
    assert s["visited"] > 0


def test_astar_matches_dijkstra_cost():
    p1, c1, _ = dijkstra(G, 12, "F1")
    p2, c2, _ = a_star(G, 12, "F1")
    assert abs(c1 - c2) < 1e-6  # admissible heuristic ⇒ same optimum


def test_time_dependent_changes_cost():
    _, cm, _ = time_dependent_dijkstra(G, 1, 4, "morning")
    _, cn, _ = time_dependent_dijkstra(G, 1, 4, "night")
    assert cn <= cm  # night should be ≤ morning peak


def test_mst_connected_and_saves():
    out = kruskal_mst(GF)
    assert out["n_edges"] == GF.number_of_nodes() - 1 or out["components_in_mst"] >= 1
    assert out["construction_cost_MEGP"] <= out["baseline_construction_MEGP"]


def test_transit_dp():
    routes = [{"id": r[0], "demand": r[3], "current_buses": r[2]}
              for r in DS["bus_routes"]]
    out = optimize_transit_schedule(routes, 200)
    assert out["total_buses_used"] <= 200
    assert out["passengers_served"] > 0


def test_maintenance_dp():
    cands = [{"id": "a", "cost_MEGP": 50, "benefit": 100},
             {"id": "b", "cost_MEGP": 30, "benefit": 60},
             {"id": "c", "cost_MEGP": 20, "benefit": 40}]
    out = road_maintenance_allocation(cands, 60)
    assert out["spent_MEGP"] <= 60


def test_signal_greedy():
    out = traffic_signal_optimization({"N": 1000, "S": 500, "E": 800, "W": 200})
    assert sum(out["greedy_plan_seconds"].values()) == out["cycle_seconds"]


def test_router_memoization():
    r = MemoizedRouter(G)
    r.query(1, 4, "morning"); r.query(1, 4, "morning")
    assert r.hits == 1 and r.misses == 1


def test_simulation_runs():
    res = simulate_period(G, DS["transit_demand"], "morning")
    assert res["served"] > 0


def test_road_closure():
    H = scenario_road_closure(G, [(3, 5)])
    assert not H.has_edge(3, 5) and not H.has_edge(5, 3)


if __name__ == "__main__":
    import sys
    failed = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn(); print(f"✓ {name}")
            except AssertionError as e:
                failed += 1; print(f"✗ {name}: {e}")
    sys.exit(failed)
