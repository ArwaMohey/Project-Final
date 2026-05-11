"""
Minimum Spanning Tree (Kruskal) for Greater Cairo road network.

Modifications vs textbook Kruskal:
  * Edge weights are penalised when they connect to high-population districts
    or critical facilities (hospitals, airport) — those edges become 'cheaper'
    so the MST prefers keeping / building them.
  * Considers BOTH existing and potential roads.
    - Existing roads: cost = distance * (11 - condition)  [maintenance proxy]
    - Potential roads: cost = construction_cost_M_EGP     [build cost]
  * Returns the MST + a cost-savings analysis vs naïve "connect everything".

Complexity: O(E log E) time, O(V) space.
"""
from __future__ import annotations
from typing import Dict, List, Tuple, Any
import networkx as nx

CRITICAL_FACILITY_TYPES = {"Medical", "Airport", "Transit Hub", "Government"}


# ---------------------------------------------------------------------------
# Disjoint-Set Union (Union-Find) with path compression + union-by-rank
# ---------------------------------------------------------------------------

class _DSU:
    def __init__(self, items):
        self.p = {x: x for x in items}
        self.r = {x: 0   for x in items}

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]   # path-halving
            x = self.p[x]
        return x

    def union(self, a, b) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.r[ra] < self.r[rb]:
            ra, rb = rb, ra
        self.p[rb] = ra
        if self.r[ra] == self.r[rb]:
            self.r[ra] += 1
        return True


# ---------------------------------------------------------------------------
# Priority factor — lower ⇒ edge is more important to keep
# ---------------------------------------------------------------------------

def _priority_factor(G: nx.DiGraph, u, v) -> float:
    """
    Multiplier in (0, 1].
    Discounts edges that touch high-population nodes or critical facilities
    so Kruskal is more likely to include them in the MST.
    """
    factor = 1.0
    for n in (u, v):
        d = G.nodes[n]
        if d.get("kind") == "facility" and d.get("type") in CRITICAL_FACILITY_TYPES:
            factor *= 0.6
        pop = d.get("pop", 0)
        if pop >= 400_000:
            factor *= 0.7
        elif pop >= 200_000:
            factor *= 0.85
    return factor


# ---------------------------------------------------------------------------
# Kruskal MST
# ---------------------------------------------------------------------------

def kruskal_mst(G: nx.DiGraph) -> Dict[str, Any]:
    """
    Build MST on the underlying undirected graph.

    Cost model:
        existing edge  → distance × (11 − condition)   [maintenance index]
        potential edge → construction_cost  (M EGP)
    Both multiplied by _priority_factor to favour critical/high-pop edges.
    """
    seen: set = set()
    edges: List[Tuple[float, Any, Any, dict]] = []

    for u, v, data in G.edges(data=True):
        key = tuple(sorted([str(u), str(v)]))
        if key in seen:
            continue
        seen.add(key)
        if data["kind"] == "existing":
            base = data["distance"] * (11 - data["condition"])
        else:
            base = data["cost"]
        cost = base * _priority_factor(G, u, v)
        edges.append((cost, u, v, data))

    edges.sort(key=lambda e: e[0])

    dsu = _DSU(list(G.nodes()))
    mst_edges: List[Tuple] = []
    total_construction = 0.0
    total_maintenance  = 0.0

    for cost, u, v, data in edges:
        if dsu.union(u, v):
            mst_edges.append((u, v, data))
            if data["kind"] == "potential":
                total_construction += data["cost"]
            else:
                total_maintenance  += data["distance"] * (11 - data["condition"])

    # ---- Naive baseline: build every potential + maintain every existing ----
    seen2: set = set()
    naive_construction = 0.0
    naive_maintenance  = 0.0
    for _, _, d in G.edges(data=True):
        key = tuple(sorted([str(_), str(_)]))   # placeholder; use seen2 below

    seen2 = set()
    for u, v, d in G.edges(data=True):
        key = tuple(sorted([str(u), str(v)]))
        if key in seen2:
            continue
        seen2.add(key)
        if d["kind"] == "potential":
            naive_construction += d["cost"]
        else:
            naive_maintenance  += d["distance"] * (11 - d["condition"])

    # How many connected components remain in the MST
    mst_undirected = nx.Graph()
    mst_undirected.add_nodes_from(G.nodes())
    mst_undirected.add_edges_from((u, v) for u, v, _ in mst_edges)
    components = nx.number_connected_components(mst_undirected)

    return {
        "edges":                         mst_edges,
        "n_edges":                       len(mst_edges),
        "construction_cost_MEGP":        round(total_construction, 2),
        "maintenance_index":             round(total_maintenance, 2),
        "baseline_construction_MEGP":    round(naive_construction, 2),
        "baseline_maintenance_index":    round(naive_maintenance, 2),
        "savings_construction_MEGP":     round(naive_construction - total_construction, 2),
        "components_in_mst":             components,
        "complexity":                    "O(E log E) time, O(V) space",
    }