"""
Performance benchmarks — runs every algorithm on the full Cairo dataset
and prints a summary table. Also dumps comparative charts to /tmp.
"""
from __future__ import annotations
import time, statistics, random
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from data.loader import load_dataset
from algorithms import (
    kruskal_mst, dijkstra, a_star, time_dependent_dijkstra,
    optimize_transit_schedule, road_maintenance_allocation,
    traffic_signal_optimization, MemoizedRouter,
)
from simulation import simulate_period

DS = load_dataset(); G = DS["graph_existing"]; GF = DS["graph_full"]
NODES = list(G.nodes())


def bench(label, fn, runs=20):
    times = []
    for _ in range(runs):
        t0 = time.perf_counter(); fn(); times.append(time.perf_counter() - t0)
    return label, statistics.mean(times)*1000, statistics.stdev(times)*1000


def main():
    random.seed(0)
    pairs = [(random.choice(NODES), random.choice(NODES)) for _ in range(20)]
    pairs = [(a, b) for a, b in pairs if a != b]

    results = []
    results.append(bench("Kruskal MST", lambda: kruskal_mst(GF), runs=10))
    results.append(bench("Dijkstra (random pair)",
                         lambda: dijkstra(G, *random.choice(pairs))))
    results.append(bench("A* (random pair)",
                         lambda: a_star(G, *random.choice(pairs))))
    results.append(bench("Time-dep. Dijkstra (morning)",
                         lambda: time_dependent_dijkstra(
                             G, *random.choice(pairs), "morning")))

    routes = [{"id": r[0], "demand": r[3], "current_buses": r[2]}
              for r in DS["bus_routes"]]
    results.append(bench("Transit DP (250 buses)",
                         lambda: optimize_transit_schedule(routes, 250),
                         runs=5))
    cands = [{"id": f"r{i}", "cost_MEGP": 10 + i*3, "benefit": 50 + i*7}
             for i in range(40)]
    results.append(bench("Maintenance DP (B=600)",
                         lambda: road_maintenance_allocation(cands, 600),
                         runs=5))
    results.append(bench("Greedy signal",
                         lambda: traffic_signal_optimization(
                             {"N": 1500, "S": 1300, "E": 900, "W": 1100})))
    results.append(bench("Simulation (morning)",
                         lambda: simulate_period(
                             G, DS["transit_demand"], "morning"),
                         runs=5))

    # Memoization gain
    R = MemoizedRouter(G)
    t0 = time.perf_counter()
    for _ in range(5):
        for a, b in pairs[:8]: R.query(a, b, "morning")
    memo_t = (time.perf_counter() - t0) * 1000
    print(f"\nMemoized router: 40 queries in {memo_t:.1f} ms "
          f"(hits={R.hits}, misses={R.misses})\n")

    print(f"{'Algorithm':35} {'Mean (ms)':>10} {'± Std (ms)':>12}")
    print("-" * 60)
    for label, mean, std in results:
        print(f"{label:35} {mean:>10.2f} {std:>12.2f}")

    # Bar chart
    labels = [r[0] for r in results]; means = [r[1] for r in results]
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.barh(labels, means, color="#0ea5e9")
    for i, v in enumerate(means):
        ax.text(v, i, f"  {v:.2f} ms", va="center", fontsize=9)
    ax.set_xlabel("Mean runtime (ms)")
    ax.set_title("Cairo Smart Transport — algorithm benchmarks")
    fig.tight_layout(); fig.savefig("/tmp/benchmarks.png", dpi=130)
    print("\nChart saved → /tmp/benchmarks.png")


if __name__ == "__main__":
    main()
