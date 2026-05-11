"""
tests/test_mst.py
=================
Tests for Member 2 — MST Infrastructure Module
Covers: Kruskal's algorithm, modified edge weights, connectivity
        guarantees, cost analysis, and graph-theoretic properties.
"""
import math
import pytest
import networkx as nx

from src.data.loader import load_dataset
from src.algorithms.mst import kruskal_mst, _priority_factor, _DSU


# ──────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def DS():
    return load_dataset()


@pytest.fixture(scope="module")
def GF(DS):
    return DS["graph_full"]


@pytest.fixture(scope="module")
def G(DS):
    return DS["graph_existing"]


@pytest.fixture(scope="module")
def mst_result(GF):
    return kruskal_mst(GF)


# ──────────────────────────────────────────────────────────────
# 1. Disjoint-Set Union (Union-Find)
# ──────────────────────────────────────────────────────────────

class TestDSU:
    def test_initial_find_is_self(self):
        dsu = _DSU([1, 2, 3, 4, 5])
        for x in [1, 2, 3, 4, 5]:
            assert dsu.find(x) == x

    def test_union_merges_components(self):
        dsu = _DSU([1, 2, 3])
        assert dsu.union(1, 2) is True
        assert dsu.find(1) == dsu.find(2)

    def test_duplicate_union_returns_false(self):
        dsu = _DSU([1, 2])
        dsu.union(1, 2)
        assert dsu.union(1, 2) is False  # already same component

    def test_path_compression_works(self):
        items = list(range(10))
        dsu = _DSU(items)
        for i in range(9):
            dsu.union(i, i + 1)
        # After all unions, all point to same root
        root = dsu.find(0)
        for i in range(10):
            assert dsu.find(i) == root

    def test_union_by_rank(self):
        dsu = _DSU(["a", "b", "c"])
        dsu.union("a", "b")
        dsu.union("b", "c")
        assert dsu.find("a") == dsu.find("c")

    def test_string_and_int_keys(self):
        dsu = _DSU([1, "F1", 2, "F2"])
        dsu.union(1, "F1")
        assert dsu.find(1) == dsu.find("F1")


# ──────────────────────────────────────────────────────────────
# 2. Priority factor
# ──────────────────────────────────────────────────────────────

class TestPriorityFactor:
    def test_critical_facility_discounted(self, GF):
        # F9 = Qasr El Aini Hospital (Medical) — should be discounted
        factor = _priority_factor(GF, "F9", 3)
        assert factor < 1.0

    def test_high_pop_discounted(self, GF):
        # Node 2 = Nasr City (500,000) — should get discount
        factor = _priority_factor(GF, 2, 3)
        assert factor < 1.0

    def test_low_pop_no_discount(self, GF):
        # Node 6 = Zamalek (50,000) — minimal discount
        factor_low  = _priority_factor(GF, 6, 6)
        factor_high = _priority_factor(GF, 2, 3)  # Nasr City × Downtown
        assert factor_low >= factor_high

    def test_factor_in_valid_range(self, GF):
        for u, v in list(GF.edges())[:20]:
            f = _priority_factor(GF, u, v)
            assert 0 < f <= 1.0


# ──────────────────────────────────────────────────────────────
# 3. MST correctness
# ──────────────────────────────────────────────────────────────

class TestMSTCorrectness:
    def test_returns_dict_with_required_keys(self, mst_result):
        required = {"edges", "n_edges", "construction_cost_MEGP",
                    "maintenance_index", "baseline_construction_MEGP",
                    "baseline_maintenance_index", "savings_construction_MEGP",
                    "components_in_mst", "complexity"}
        assert required.issubset(mst_result.keys())

    def test_edge_count_is_v_minus_1(self, GF, mst_result):
        # A spanning tree of N nodes has exactly N-1 edges
        expected = GF.number_of_nodes() - 1
        assert mst_result["n_edges"] == expected

    def test_mst_spans_all_nodes(self, GF, mst_result):
        mst_nodes = set()
        for u, v, _ in mst_result["edges"]:
            mst_nodes.add(u)
            mst_nodes.add(v)
        assert mst_nodes == set(GF.nodes())

    def test_mst_is_acyclic(self, mst_result):
        H = nx.Graph()
        for u, v, _ in mst_result["edges"]:
            H.add_edge(u, v)
        assert nx.is_forest(H)

    def test_mst_is_connected(self, mst_result):
        H = nx.Graph()
        for u, v, _ in mst_result["edges"]:
            H.add_edge(u, v)
        assert nx.is_connected(H)

    def test_no_duplicate_edges_in_mst(self, mst_result):
        seen = set()
        for u, v, _ in mst_result["edges"]:
            key = tuple(sorted([str(u), str(v)]))
            assert key not in seen, f"Duplicate MST edge {key}"
            seen.add(key)


# ──────────────────────────────────────────────────────────────
# 4. Cost analysis
# ──────────────────────────────────────────────────────────────

class TestCostAnalysis:
    def test_construction_cost_non_negative(self, mst_result):
        assert mst_result["construction_cost_MEGP"] >= 0

    def test_mst_construction_leq_baseline(self, mst_result):
        assert (mst_result["construction_cost_MEGP"] <=
                mst_result["baseline_construction_MEGP"])

    def test_savings_is_difference(self, mst_result):
        expected = (mst_result["baseline_construction_MEGP"] -
                    mst_result["construction_cost_MEGP"])
        assert abs(mst_result["savings_construction_MEGP"] - expected) < 0.1

    def test_savings_non_negative(self, mst_result):
        assert mst_result["savings_construction_MEGP"] >= 0

    def test_complexity_string(self, mst_result):
        assert "E log E" in mst_result["complexity"]


# ──────────────────────────────────────────────────────────────
# 5. Critical connectivity requirements
# ──────────────────────────────────────────────────────────────

class TestCriticalConnectivity:
    CRITICAL = {"F1", "F9", "F10", "F2", 13}   # airport, hospitals, station, NAC

    def test_critical_nodes_in_mst(self, mst_result):
        mst_nodes = set()
        for u, v, _ in mst_result["edges"]:
            mst_nodes.add(u)
            mst_nodes.add(v)
        for c in self.CRITICAL:
            assert c in mst_nodes, f"Critical node {c} missing from MST"

    def test_hospitals_connected_to_mst(self, mst_result):
        H = nx.Graph()
        for u, v, _ in mst_result["edges"]:
            H.add_edge(u, v)
        hospitals = {"F9", "F10"}
        for h in hospitals:
            if h in H:
                assert nx.has_path(H, h, 3), f"Hospital {h} not reachable"


# ──────────────────────────────────────────────────────────────
# 6. Kruskal on a tiny synthetic graph (white-box verification)
# ──────────────────────────────────────────────────────────────

class TestKruskalSynthetic:
    @pytest.fixture
    def tiny_graph(self):
        """
        4-node graph:
            A --1-- B
            A --3-- C
            B --2-- C
            C --4-- D
        MST = A-B(1), B-C(2), C-D(4)  total=7
        """
        G = nx.DiGraph()
        for n in ["A", "B", "C", "D"]:
            G.add_node(n, kind="district", name=n, pop=10000,
                       type="Mixed", x=31.0, y=30.0)
        def _add(u, v, dist):
            attrs = dict(distance=dist, capacity=3000, condition=9,
                         weight=float(dist), kind="existing", cost=0.0,
                         traffic={p: 1000 for p in
                                  ["morning","afternoon","evening","night"]})
            G.add_edge(u, v, **attrs)
            G.add_edge(v, u, **attrs)
        _add("A", "B", 1)
        _add("A", "C", 3)
        _add("B", "C", 2)
        _add("C", "D", 4)
        return G

    def test_tiny_mst_edge_count(self, tiny_graph):
        result = kruskal_mst(tiny_graph)
        assert result["n_edges"] == 3  # 4 nodes → 3 edges

    def test_tiny_mst_contains_cheapest_edge(self, tiny_graph):
        result = kruskal_mst(tiny_graph)
        mst_pairs = {(str(u), str(v)) for u, v, _ in result["edges"]}
        mst_pairs |= {(v, u) for u, v in mst_pairs}
        assert ("A", "B") in mst_pairs or ("B", "A") in mst_pairs

    def test_tiny_mst_excludes_heaviest_redundant_edge(self, tiny_graph):
        result = kruskal_mst(tiny_graph)
        mst_pairs = {(str(u), str(v)) for u, v, _ in result["edges"]}
        mst_pairs |= {(v, u) for u, v in mst_pairs}
        # A-C(3) should NOT be in MST (A-B(1) + B-C(2) is cheaper)
        assert ("A", "C") not in mst_pairs and ("C", "A") not in mst_pairs


if __name__ == "__main__":
    pytest.main([__file__, "-v"])