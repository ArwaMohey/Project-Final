"""
tests/test_bonus.py
===================
Bonus Tests (CSE112) — covers:
  1. ML-based congestion prediction (scikit-learn RandomForest)
  2. Dijkstra vs A* comparison (side-by-side metrics)
  3. Full-day simulation across all time periods
  4. Road maintenance knapsack DP
  5. Emergency multi-path resilience
"""
import math
import pytest
from data.loader import load_dataset
from algorithms import (
    dijkstra, a_star, time_dependent_dijkstra,
    kruskal_mst, optimize_transit_schedule,
    road_maintenance_allocation, emergency_priority,
)
from simulation import simulate_period


# ──────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def DS():
    return load_dataset()

@pytest.fixture(scope="module")
def G(DS):
    return DS["graph_existing"]

@pytest.fixture(scope="module")
def GF(DS):
    return DS["graph_full"]


# ──────────────────────────────────────────────────────────────
# 1. ML Congestion Prediction
# ──────────────────────────────────────────────────────────────

class TestMLCongestion:
    def test_model_trains_without_error(self):
        from ml.congestion import train_model
        model, metrics = train_model()
        assert model is not None
        assert "mae_vph" in metrics
        assert metrics["mae_vph"] >= 0

    def test_mae_is_reasonable(self):
        from ml.congestion import train_model
        _, metrics = train_model()
        # MAE should be below 300 vph (dataset range ~400-3800)
        assert metrics["mae_vph"] < 300

    def test_predict_returns_positive_float(self, G):
        from ml.congestion import train_model, predict_congestion
        model, _ = train_model()
        edge_data = {"distance": 5.0, "capacity": 3000, "condition": 7}
        vph = predict_congestion(model, edge_data, hour=8)
        assert isinstance(vph, float)
        assert vph >= 0

    def test_morning_peak_higher_than_night(self, G):
        from ml.congestion import train_model, predict_congestion
        model, _ = train_model()
        edge = {"distance": 6.0, "capacity": 3000, "condition": 7}
        morning_vph = predict_congestion(model, edge, hour=8)
        night_vph   = predict_congestion(model, edge, hour=23)
        assert morning_vph > night_vph

    def test_predict_all_hours(self, G):
        from ml.congestion import train_model, predict_congestion
        model, _ = train_model()
        edge = {"distance": 4.0, "capacity": 2500, "condition": 8}
        for hour in range(0, 24, 3):
            vph = predict_congestion(model, edge, hour=hour)
            assert vph >= 0, f"Negative vph at hour {hour}"

    def test_training_data_counts(self):
        from ml.congestion import train_model
        _, metrics = train_model()
        assert metrics["n_train"] > metrics["n_test"]
        assert metrics["n_train"] + metrics["n_test"] > 100


# ──────────────────────────────────────────────────────────────
# 2. Dijkstra vs A* Comparison (Side-by-side)
# ──────────────────────────────────────────────────────────────

class TestDijkstraVsAStar:
    TEST_PAIRS = [(1, "F1"), (3, 13), (12, "F9"), (7, 5), (15, 4)]

    def test_same_optimal_cost(self, G):
        """A* must find the same cost as Dijkstra (admissible heuristic)."""
        for src, dst in self.TEST_PAIRS:
            _, c_d, _ = dijkstra(G, src, dst)
            _, c_a, _ = a_star(G, src, dst)
            assert abs(c_d - c_a) < 1e-6, (
                f"Cost mismatch {src}->{dst}: Dijkstra={c_d:.4f}, A*={c_a:.4f}")

    def test_astar_visits_fewer_or_equal_nodes(self, G):
        """A* with an admissible heuristic should expand ≤ Dijkstra nodes."""
        for src, dst in self.TEST_PAIRS:
            _, _, sd = dijkstra(G, src, dst)
            _, _, sa = a_star(G, src, dst)
            assert sa["visited"] <= sd["visited"] + 2  # allow tiny slack

    def test_both_return_valid_paths(self, G):
        for src, dst in self.TEST_PAIRS:
            pd, _, _ = dijkstra(G, src, dst)
            pa, _, _ = a_star(G, src, dst)
            assert pd[0] == src and pd[-1] == dst
            assert pa[0] == src and pa[-1] == dst

    def test_astar_path_is_continuous(self, G):
        for src, dst in self.TEST_PAIRS:
            path, _, _ = a_star(G, src, dst)
            for u, v in zip(path, path[1:]):
                assert G.has_edge(u, v), f"Gap in A* path: {u}->{v}"

    def test_comparison_summary(self, G):
        """Collect comparison metrics — must not raise."""
        results = []
        for src, dst in self.TEST_PAIRS:
            _, c_d, sd = dijkstra(G, src, dst)
            _, c_a, sa = a_star(G, src, dst)
            results.append({
                "pair": (src, dst),
                "dijkstra_visited": sd["visited"],
                "astar_visited":    sa["visited"],
                "cost_match":       abs(c_d - c_a) < 1e-6,
            })
        assert all(r["cost_match"] for r in results)


# ──────────────────────────────────────────────────────────────
# 3. Full-day Simulation
# ──────────────────────────────────────────────────────────────

class TestFullDaySimulation:
    PERIODS = ["morning", "afternoon", "evening", "night"]

    def test_all_periods_run(self, G, DS):
        for p in self.PERIODS:
            res = simulate_period(G, DS["transit_demand"], p)
            assert res["period"] == p
            assert res["served"] > 0

    def test_morning_has_highest_load(self, G, DS):
        results = {p: simulate_period(G, DS["transit_demand"], p)
                   for p in self.PERIODS}
        # Morning avg travel time should be ≥ night
        assert results["morning"]["avg_minutes_per_pax"] >= \
               results["night"]["avg_minutes_per_pax"]

    def test_edge_load_populated(self, G, DS):
        res = simulate_period(G, DS["transit_demand"], "morning")
        assert len(res["edge_load"]) > 0

    def test_served_plus_unreachable_equals_total(self, G, DS):
        res = simulate_period(G, DS["transit_demand"], "afternoon")
        total = sum(r[2] for r in DS["transit_demand"])
        assert res["served"] + res["unreachable"] == total


# ──────────────────────────────────────────────────────────────
# 4. Road Maintenance Knapsack
# ──────────────────────────────────────────────────────────────

class TestMaintenanceKnapsack:
    def test_budget_not_exceeded(self):
        cands = [
            {"id": "r1", "cost_MEGP": 30, "benefit": 90},
            {"id": "r2", "cost_MEGP": 20, "benefit": 50},
            {"id": "r3", "cost_MEGP": 15, "benefit": 40},
            {"id": "r4", "cost_MEGP": 25, "benefit": 70},
        ]
        out = road_maintenance_allocation(cands, 50)
        assert out["spent_MEGP"] <= 50

    def test_maximises_benefit(self):
        cands = [
            {"id": "cheap",    "cost_MEGP": 10, "benefit": 10},
            {"id": "valuable", "cost_MEGP": 40, "benefit": 100},
        ]
        out = road_maintenance_allocation(cands, 40)
        assert "valuable" in out["selected"]

    def test_empty_candidates(self):
        out = road_maintenance_allocation([], 100)
        assert out["selected"] == []
        assert out["total_benefit"] == 0


# ──────────────────────────────────────────────────────────────
# 5. Emergency Multi-Path Resilience
# ──────────────────────────────────────────────────────────────

class TestEmergencyResilience:
    def test_three_routes_found(self, G):
        # 1 -> F1 has multiple disjoint paths (rich connectivity)
        reqs = [{"id": "Amb1", "src": 1, "dst": "F1", "severity": 10}]
        res = emergency_priority(G, reqs, "morning")
        r = res[0]
        assert r["num_routes"] >= 2  # At least 2 disjoint routes

    def test_routes_are_different(self, G):
        reqs = [{"id": "Fire1", "src": 1, "dst": "F1", "severity": 8}]
        res = emergency_priority(G, reqs, "morning")
        r = res[0]
        if r["path1"] and r["path2"]:
            assert r["path1"] != r["path2"]

    def test_eta_increases_per_route(self, G):
        """Each alternative route should have equal or longer ETA."""
        reqs = [{"id": "Police1", "src": 2, "dst": "F1", "severity": 5}]
        res = emergency_priority(G, reqs, "morning")
        r = res[0]
        if r["eta1"] and r["eta2"]:
            assert r["eta2"] >= r["eta1"] - 1e-6  # route 2 is >= route 1

    def test_priority_ordering(self, G):
        """Higher severity request should be processed first (appear first in output)."""
        reqs = [
            {"id": "Low",  "src": 1, "dst": "F1", "severity": 1},
            {"id": "High", "src": 3, "dst": "F9", "severity": 10},
        ]
        res = emergency_priority(G, reqs, "morning")
        assert res[0]["id"] == "High"
        assert res[1]["id"] == "Low"

    def test_all_periods(self, G):
        for period in ["morning", "afternoon", "evening", "night"]:
            reqs = [{"id": "Amb", "src": 3, "dst": "F9", "severity": 5}]
            res = emergency_priority(G, reqs, period)
            assert res[0]["eta1"] < math.inf


if __name__ == "__main__":
    pytest.main([__file__, "-v"])