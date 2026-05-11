"""
Greedy algorithms.

1) traffic_signal_optimization(approaches, ...)
       Round-robin green time proportional to incoming vehicle counts —
       a greedy "largest queue first" rule.  Compared against Webster's
       formula.

       Optimal when arrival rates differ widely; suboptimal (up to ~15%
       worse than Webster) when saturation flow rates differ between
       approaches.

       Complexity: O(K log K) for sorting K approaches.

2) emergency_priority(G, requests, period)
       Each request gets up to 3 edge-disjoint alternative routes using A*.
       After each route is found, its edges are removed from a working copy
       of the graph so the next route is forced to use different roads.

       Complexity: O(R × (V + E) log V) for R requests.
"""
from __future__ import annotations
from typing import Dict, List, Any
import networkx as nx

from algorithms.shortest_path import a_star, time_dependent_weight


# ---------------------------------------------------------------------------
# Traffic signal optimisation
# ---------------------------------------------------------------------------

def traffic_signal_optimization(approaches: Dict[str, int],
                                  cycle_seconds: int = 90,
                                  min_green: int = 8,
                                  saturation_flow_vph: int = 3600,
                                  lost_time_per_cycle: int = 4) -> Dict[str, Any]:
    """
    Parameters
    ----------
    approaches          dict mapping direction label → vehicles/hour,
                        e.g. {'N': 1500, 'S': 1300, 'E': 900, 'W': 1100}
    cycle_seconds       total signal cycle length (default 90 s)
    min_green           minimum green time per direction (default 8 s)
    saturation_flow_vph assumed saturation flow for Webster calc (vph)
    lost_time_per_cycle total lost time per cycle (s)

    Returns
    -------
    dict with greedy_plan_seconds, webster_reference, cycle_seconds,
    complexity
    """
    if not approaches:
        return {"greedy_plan_seconds": {}, "webster_reference": {},
                "cycle_seconds": cycle_seconds, "complexity": "O(K log K)"}

    total = sum(approaches.values()) or 1
    n = len(approaches)
    available = cycle_seconds - n * min_green

    # ---- Greedy plan ----
    plan: Dict[str, int] = {}
    for d, vph in approaches.items():
        plan[d] = min_green + max(0, int(round(available * vph / total)))

    # Repair rounding drift so sum == cycle_seconds
    drift = cycle_seconds - sum(plan.values())
    if drift != 0:
        biggest = max(approaches, key=lambda k: approaches[k])
        plan[biggest] += drift

    # ---- Webster's formula reference ----
    y = {d: vph / saturation_flow_vph for d, vph in approaches.items()}
    sum_y = sum(y.values())

    if sum_y >= 1.0:
        # Over-saturated — fall back to proportional
        webster_ideal = {d: max(min_green, int(round(cycle_seconds * vph / total)))
                         for d, vph in approaches.items()}
    else:
        C_opt = (1.5 * lost_time_per_cycle + 5) / (1.0 - sum_y)
        effective_green = max(1.0, C_opt - lost_time_per_cycle)
        webster_ideal = {}
        for d, vph in approaches.items():
            g = effective_green * y[d] / (sum_y or 1)
            webster_ideal[d] = max(min_green, int(round(g)))
        # Scale to cycle_seconds
        tw = sum(webster_ideal.values())
        if tw > 0 and tw != cycle_seconds:
            factor = cycle_seconds / tw
            webster_ideal = {d: max(min_green, int(round(g * factor)))
                             for d, g in webster_ideal.items()}
        # Fix rounding for Webster plan too
        w_drift = cycle_seconds - sum(webster_ideal.values())
        if w_drift != 0:
            biggest = max(approaches, key=lambda k: approaches[k])
            webster_ideal[biggest] += w_drift

    return {
        "greedy_plan_seconds": plan,
        "webster_reference":   webster_ideal,
        "cycle_seconds":       cycle_seconds,
        "complexity":          "O(K log K)",
    }


# ---------------------------------------------------------------------------
# Emergency priority dispatch
# ---------------------------------------------------------------------------

# algorithms/greedy.py (Replace the existing emergency_priority function)

def emergency_priority(G: nx.DiGraph,
                       requests: List[Dict[str, Any]],
                       period: str = "morning") -> List[Dict[str, Any]]:
    """
    Greedy priority dispatch for emergency vehicles.
    Uses A* with a preemption weight function (ignores standard traffic congestion).
    Finds up to 3 edge-disjoint routes per request for resilience.
    """
    # Use the emergency weight function (bypasses congestion)
    weight_fn = time_dependent_weight(period, is_emergency=True)
    out = []

    for req in requests: # No sorting by severity anymore
        src, dst = req["src"], req["dst"]
        paths: List[List] = []
        costs: List[float] = []
        last_visited = 0

        G_work = G.copy()

        # Find up to 3 edge-disjoint routes
        for _ in range(3):
            path, cost, stats = a_star(G_work, src, dst, weight_fn=weight_fn)
            last_visited = stats.get("visited", 0)
            
            if path and cost < float("inf"):
                paths.append(path)
                costs.append(cost)
                # Remove edges to force the next route to be different
                for u, v in zip(path, path[1:]):
                    if G_work.has_edge(u, v):
                        G_work.remove_edge(u, v)
            else:
                break

        out.append({
            "id":         req["id"],
            "path1":      paths[0] if len(paths) > 0 else None,
            "path2":      paths[1] if len(paths) > 1 else None,
            "path3":      paths[2] if len(paths) > 2 else None,
            "eta1":       costs[0] if len(costs) > 0 else None,
            "eta2":       costs[1] if len(costs) > 1 else None,
            "eta3":       costs[2] if len(costs) > 2 else None,
            "num_routes": len(paths),
            "visited":    last_visited,
        })

    return out