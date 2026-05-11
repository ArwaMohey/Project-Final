"""
tests/test_data.py
==================
Tests for Member 1 — Data & Graph System
Covers: cairo_data.py, loader.py (Node / Edge / Graph construction,
        adjacency list, helper functions, validation).
"""
import math
import pytest
import networkx as nx

from data.loader import (
    build_graph,
    load_dataset,
    haversine_km,
    edge_weight,
)
import data.cairo_data as D


# ──────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def G():
    return build_graph(include_potential=False)


@pytest.fixture(scope="module")
def GF():
    return build_graph(include_potential=True)


@pytest.fixture(scope="module")
def DS():
    return load_dataset()


# ──────────────────────────────────────────────────────────────
# 1. Raw data integrity
# ──────────────────────────────────────────────────────────────

class TestRawData:
    def test_neighborhood_count(self):
        assert len(D.NEIGHBORHOODS) == 15

    def test_facility_count(self):
        assert len(D.FACILITIES) == 10

    def test_neighborhood_fields(self):
        for row in D.NEIGHBORHOODS:
            nid, name, pop, typ, x, y = row
            assert isinstance(name, str) and name
            assert pop > 0
            assert 30.8 < x < 32.0, f"lon out of range: {x}"
            assert 29.7 < y < 30.3, f"lat out of range: {y}"

    def test_facility_fields(self):
        for row in D.FACILITIES:
            fid, name, typ, x, y = row
            assert str(fid).startswith("F")
            assert isinstance(name, str) and name

    def test_existing_road_fields(self):
        for row in D.EXISTING_ROADS:
            u, v, dist, cap, cond = row
            assert dist > 0
            assert cap > 0
            assert 1 <= cond <= 10

    def test_potential_road_fields(self):
        for row in D.POTENTIAL_ROADS:
            u, v, dist, cap, cost = row
            assert dist > 0 and cap > 0 and cost > 0

    def test_traffic_flow_keys_are_tuples(self):
        for k in D.TRAFFIC_FLOW:
            assert isinstance(k, tuple) and len(k) == 2

    def test_traffic_flow_values_are_4_periods(self):
        for k, v in D.TRAFFIC_FLOW.items():
            assert len(v) == 4, f"Expected 4 periods for {k}"

    def test_time_periods_order(self):
        assert D.TIME_PERIODS == ["morning", "afternoon", "evening", "night"]

    def test_metro_lines_defined(self):
        assert len(D.METRO_LINES) == 3

    def test_bus_routes_defined(self):
        assert len(D.BUS_ROUTES) == 10

    def test_transit_demand_pairs(self):
        assert len(D.TRANSIT_DEMAND) > 0
        for row in D.TRANSIT_DEMAND:
            src, dst, pax = row
            assert pax > 0


# ──────────────────────────────────────────────────────────────
# 2. Haversine helper
# ──────────────────────────────────────────────────────────────

class TestHaversine:
    def test_same_point_is_zero(self):
        assert haversine_km(30.04, 31.24, 30.04, 31.24) == 0.0

    def test_known_distance_cairo_downtown_maadi(self):
        # Downtown Cairo (30.04, 31.24) → Maadi (29.96, 31.25)
        d = haversine_km(30.04, 31.24, 29.96, 31.25)
        assert 8 < d < 10, f"Expected ~9 km, got {d:.2f}"

    def test_symmetry(self):
        d1 = haversine_km(30.04, 31.24, 29.96, 31.25)
        d2 = haversine_km(29.96, 31.25, 30.04, 31.24)
        assert abs(d1 - d2) < 1e-9

    def test_returns_float(self):
        assert isinstance(haversine_km(30.0, 31.0, 30.1, 31.1), float)


# ──────────────────────────────────────────────────────────────
# 3. Edge-weight formula
# ──────────────────────────────────────────────────────────────

class TestEdgeWeight:
    def test_positive_weight(self):
        assert edge_weight(10.0, 3000, 7) > 0

    def test_poor_condition_slower(self):
        w_good = edge_weight(10.0, 3000, 9)
        w_bad  = edge_weight(10.0, 3000, 3)
        assert w_bad > w_good

    def test_congestion_increases_weight(self):
        w_free = edge_weight(10.0, 3000, 7, traffic=0)
        w_jam  = edge_weight(10.0, 3000, 7, traffic=3000)
        assert w_jam > w_free

    def test_zero_distance_is_minimal(self):
        assert edge_weight(0.0, 3000, 10) >= 0


# ──────────────────────────────────────────────────────────────
# 4. Graph structure (existing only)
# ──────────────────────────────────────────────────────────────

class TestGraphStructure:
    def test_node_count(self, G):
        assert G.number_of_nodes() == 25  # 15 districts + 10 facilities

    def test_directed_graph_type(self, G):
        assert isinstance(G, nx.DiGraph)

    def test_district_nodes_have_pop(self, G):
        for n, d in G.nodes(data=True):
            if d["kind"] == "district":
                assert d["pop"] > 0, f"Node {n} missing population"

    def test_facility_nodes_have_type(self, G):
        for n, d in G.nodes(data=True):
            if d["kind"] == "facility":
                assert d["type"], f"Node {n} missing type"

    def test_all_nodes_have_coordinates(self, G):
        for n, d in G.nodes(data=True):
            assert "x" in d and "y" in d
            assert 30.8 < d["x"] < 32.0
            assert 29.7 < d["y"] < 30.3

    def test_edges_have_required_attributes(self, G):
        for u, v, d in G.edges(data=True):
            for attr in ("distance", "capacity", "condition", "weight",
                         "kind", "traffic"):
                assert attr in d, f"Edge {u}→{v} missing '{attr}'"

    def test_edges_have_traffic_for_all_periods(self, G):
        periods = {"morning", "afternoon", "evening", "night"}
        for u, v, d in G.edges(data=True):
            assert set(d["traffic"].keys()) == periods

    def test_edge_kind_values(self, G):
        for _, _, d in G.edges(data=True):
            assert d["kind"] in ("existing", "potential")

    def test_bidirectional_edges(self, G):
        # Every existing road should have both directions
        for u, v, d in G.edges(data=True):
            if d["kind"] == "existing":
                assert G.has_edge(v, u), f"Missing reverse edge {v}→{u}"

    def test_weights_are_positive(self, G):
        for u, v, d in G.edges(data=True):
            assert d["weight"] > 0, f"Non-positive weight on {u}→{v}"

    def test_no_self_loops(self, G):
        for u, v in G.edges():
            assert u != v


# ──────────────────────────────────────────────────────────────
# 5. Connectivity
# ──────────────────────────────────────────────────────────────

class TestConnectivity:
    def test_weakly_connected(self, G):
        assert nx.is_weakly_connected(G)

    def test_no_isolated_nodes(self, G):
        assert list(nx.isolates(G)) == []

    def test_all_districts_reachable_from_downtown(self, G):
        reachable = nx.descendants(G, 3) | {3}
        districts = {n for n, d in G.nodes(data=True) if d["kind"] == "district"}
        assert districts.issubset(reachable)

    def test_all_hospitals_reachable(self, G):
        hospitals = [n for n, d in G.nodes(data=True) if d.get("type") == "Medical"]
        assert len(hospitals) >= 2
        for h in hospitals:
            assert nx.has_path(G, 3, h), f"Hospital {h} not reachable from Downtown"


# ──────────────────────────────────────────────────────────────
# 6. Full graph (existing + potential)
# ──────────────────────────────────────────────────────────────

class TestFullGraph:
    def test_full_has_more_edges(self, G, GF):
        assert GF.number_of_edges() > G.number_of_edges()

    def test_potential_edges_present(self, GF):
        potential = [(u, v) for u, v, d in GF.edges(data=True)
                     if d["kind"] == "potential"]
        assert len(potential) > 0

    def test_potential_edges_have_cost(self, GF):
        for u, v, d in GF.edges(data=True):
            if d["kind"] == "potential":
                assert d["cost"] > 0


# ──────────────────────────────────────────────────────────────
# 7. load_dataset helper
# ──────────────────────────────────────────────────────────────

class TestLoadDataset:
    def test_returns_all_keys(self, DS):
        expected = {"graph_existing", "graph_full", "neighborhoods",
                    "facilities", "existing_roads", "potential_roads",
                    "traffic_flow", "metro_lines", "metro_routes",
                    "bus_routes", "transit_demand", "time_periods"}
        assert expected.issubset(DS.keys())

    def test_graphs_are_digraphs(self, DS):
        assert isinstance(DS["graph_existing"], nx.DiGraph)
        assert isinstance(DS["graph_full"],     nx.DiGraph)

    def test_raw_lists_non_empty(self, DS):
        for key in ("neighborhoods", "facilities", "existing_roads",
                    "potential_roads", "bus_routes", "metro_lines"):
            assert len(DS[key]) > 0, f"{key} is empty"

    def test_transit_demand_non_empty(self, DS):
        assert len(DS["transit_demand"]) > 0


# ──────────────────────────────────────────────────────────────
# 8. Neighbor / adjacency helpers
# ──────────────────────────────────────────────────────────────

class TestAdjacency:
    def test_successors_downtown(self, G):
        succs = list(G.successors(3))
        assert len(succs) >= 4  # Downtown is a hub

    def test_edge_weight_access(self, G):
        # weight of Downtown → Heliopolis
        assert G.has_edge(3, 5)
        w = G[3][5]["weight"]
        assert w > 0

    def test_predecessors_airport(self, G):
        preds = list(G.predecessors("F1"))
        assert len(preds) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])