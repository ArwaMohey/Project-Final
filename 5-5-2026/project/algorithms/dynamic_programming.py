"""
Dynamic Programming components.

1) optimize_transit_schedule(routes, total_buses)
       Allocates a fixed fleet across routes to MAXIMISE total daily
       passengers served — a classical bounded resource-allocation problem
       solved with DP.

       dp[i][b] = max passengers when the first i routes get b vehicles total.

       Complexity: O(R × B × Bmax_per_route)   space O(R × B)

2) road_maintenance_allocation(roads, budget)
       0/1 knapsack: each candidate road repair has a cost (M EGP) and a
       benefit (population-served score). Maximises benefit under budget.

       Complexity: O(N × Budget_scaled)
"""
from __future__ import annotations
from typing import List, Dict, Any


# ---------------------------------------------------------------------------
# Bounded resource-allocation DP  (transit scheduling)
# ---------------------------------------------------------------------------

def optimize_transit_schedule(routes: List[dict],
                               total_vehicles: int,
                               max_per_route: int = 60) -> Dict[str, Any]:
    """
    Parameters
    ----------
    routes          list of dicts with keys:
                        id, demand (passengers/day),
                        current_buses (int),
                        capacity_per_vehicle (int, default 1500)
    total_vehicles  total fleet size to allocate
    max_per_route   cap on vehicles per single route

    Returns
    -------
    dict with allocation, passengers_served, total_buses_used, complexity
    """
    R = len(routes)
    B = total_vehicles

    # dp[i][b] = best total passengers when routes 0..i-1 share b vehicles
    # Store as flat list for memory efficiency: dp[i*(B+1) + b]
    INF_NEG = -1.0
    dp      = [INF_NEG] * ((R + 1) * (B + 1))
    choice  = [0]       * ((R + 1) * (B + 1))   # how many given to route i-1

    # base case: 0 routes → 0 passengers regardless of budget
    for b in range(B + 1):
        dp[b] = 0.0

    def idx(i, b):
        return i * (B + 1) + b

    for i in range(1, R + 1):
        r   = routes[i - 1]
        cap = r.get("capacity_per_vehicle", 1500)
        dem = r["demand"]
        limit = min(max_per_route, B)

        for b in range(B + 1):
            best_val = INF_NEG
            best_k   = 0
            for k in range(0, min(limit, b) + 1):
                prev = dp[idx(i - 1, b - k)]
                if prev < 0:
                    continue
                served = min(dem, k * cap)
                val = prev + served
                if val > best_val:
                    best_val = val
                    best_k   = k
            dp[idx(i, b)]     = best_val if best_val >= 0 else 0.0
            choice[idx(i, b)] = best_k

    # Backtrack to find allocation
    allocation = {r["id"]: 0 for r in routes}
    b = B
    for i in range(R, 0, -1):
        k = choice[idx(i, b)]
        allocation[routes[i - 1]["id"]] = k
        b -= k

    passengers = dp[idx(R, B)]
    return {
        "allocation":        allocation,
        "passengers_served": int(max(passengers, 0)),
        "total_buses_used":  sum(allocation.values()),
        "complexity":        "O(R × B × Bmax)",
    }


# ---------------------------------------------------------------------------
# 0/1 Knapsack DP  (road maintenance allocation)
# ---------------------------------------------------------------------------

def road_maintenance_allocation(candidates: List[dict],
                                 budget_MEGP: float) -> Dict[str, Any]:
    """
    Parameters
    ----------
    candidates  list of dicts: {id, cost_MEGP (float), benefit (float)}
    budget_MEGP total budget in million EGP

    Returns
    -------
    dict with selected, total_benefit, spent_MEGP, complexity
    """
    SCALE = 10                               # 0.1 M EGP precision
    B = int(budget_MEGP * SCALE)
    items = [(max(1, int(round(c["cost_MEGP"] * SCALE))),
              float(c["benefit"]),
              c["id"])
             for c in candidates]
    n = len(items)

    # 1-D rolling DP (memory-efficient)
    dp    = [0.0] * (B + 1)
    keep  = [[False] * (B + 1) for _ in range(n)]   # keep[i][b]

    for i, (cost, benefit, _) in enumerate(items):
        # iterate backwards to avoid using item twice
        for b in range(B, cost - 1, -1):
            if dp[b - cost] + benefit > dp[b]:
                dp[b] = dp[b - cost] + benefit
                keep[i][b] = True

    # Backtrack
    chosen = []
    b = B
    for i in range(n - 1, -1, -1):
        if keep[i][b]:
            chosen.append(items[i][2])
            b -= items[i][0]

    spent = (B - b) / SCALE
    return {
        "selected":      chosen,
        "total_benefit": round(dp[B], 4),
        "spent_MEGP":    round(spent, 2),
        "complexity":    "O(N × Budget)",
    }