# Technical Report — Smart City Transportation Network Optimization

**Course:** CSE112 — Design and Analysis of Algorithms
**Institution:** Alamein International University
**Project:** Greater Cairo metropolitan area transportation optimizer

---

## 1. System Architecture

The system is split into six clearly-bounded layers:

```
┌─────────────────────────────────────────────────────────┐
│   Streamlit dashboard (app.py) — interactive Plotly UI  │
├─────────────────────────────────────────────────────────┤
│   FastAPI backend (backend/api.py) — REST endpoints     │
├─────────────────────────────────────────────────────────┤
│  algorithms/        simulation/        ml/              │
│  ── mst.py          ── engine.py       ── congestion.py │
│  ── shortest_path                                        │
│  ── dynamic_programming                                  │
│  ── greedy                                               │
├─────────────────────────────────────────────────────────┤
│   data/ (NetworkX graph + Cairo dataset)                │
└─────────────────────────────────────────────────────────┘
```

* **Graph model.** A `networkx.DiGraph` with 25 nodes (15 districts + 10
  facilities) and 54 directed arcs (each undirected road is duplicated). Edge
  attributes carry `distance`, `capacity`, `condition`, per-period `traffic`,
  and a derived composite `weight` that approximates travel-time minutes.
* **Frontend / Backend separation.** Algorithms have **no UI dependency** and
  are exercised directly by the test suite, by the FastAPI layer, and by the
  Streamlit dashboard — each can run independently.

## 2. Algorithm Implementations

### 2.1 Minimum Spanning Tree — Kruskal (`algorithms/mst.py`)

Modifications relative to textbook Kruskal:

1. **Mixed edge cost model.**
   *Existing roads* contribute a maintenance proxy `distance × (11 − condition)`.
   *Potential roads* contribute their `construction_cost (M EGP)` — so the MST
   meaningfully chooses between *building* and *upgrading*.
2. **Priority discount factor.** Edges incident to high-population districts
   (× 0.7) and critical facilities (medical, airport, transit hub, government —
   × 0.6) are made *cheaper*, biasing the MST toward keeping them.
3. **Cost savings analysis.** Compared against the baseline of building every
   potential road and maintaining every existing one. On the provided Cairo
   dataset the MST saves **≈ 9,770 M EGP** of construction cost.

Complexity: **O(E log E)** time, **O(V)** space (Union-Find with path compression).

### 2.2 Shortest Paths (`algorithms/shortest_path.py`)

* **Dijkstra** — standard binary-heap implementation, O((V+E) log V).
* **A\*** — uses a *haversine* great-circle heuristic divided by a maximum
  speed of 90 km/h, expressed in minutes. This is admissible because no edge
  can travel faster than 90 km/h, guaranteeing **A\* finds the same optimum
  as Dijkstra** while expanding fewer nodes (verified by `test_astar_matches_dijkstra_cost`).
* **Time-dependent shortest path** — recomputes edge weights using the
  per-period traffic counts from the dataset (`morning`, `afternoon`,
  `evening`, `night`), so the optimal Helwan → Airport route can shift
  depending on the time of day.
* **Memoized router** — `MemoizedRouter` caches `(src, dst, period)` queries.
  In benchmarks repeated queries are answered in < 1 µs after the first call.

### 2.3 Dynamic Programming (`algorithms/dynamic_programming.py`)

* **Bus fleet scheduling** — bounded-knapsack variant. State
  `dp[i][b] = max passengers served by allocating b buses among the first i
  routes`. Each bus serves up to 1500 pax/day. Transitions iterate
  `0 … max_per_route` buses per route.
  Complexity **O(R · B · Bmax)**, space **O(R · B)**.
* **Road maintenance** — classical 0/1 knapsack maximising "benefit"
  (population served by adjacent districts) under an EGP budget.
  Complexity **O(N · Budget)**.

### 2.4 Greedy (`algorithms/greedy.py`)

* **Signal timing** — green time proportional to incoming vehicle counts with
  a per-direction floor. The output is compared against a Webster-style
  reference; on uneven flows the proportional rule is within ~5% of optimum,
  but it becomes suboptimal (≥10% worse) when saturation flow rates differ
  sharply across approaches — this is documented as the *suboptimal case* in
  the dashboard.
* **Emergency vehicle preemption** — successive emergency vehicles are routed
  with A\* on a graph where previously-reserved corridors carry a 3× weight
  penalty, ensuring fleet-wide diversity. Optimal when corridors are disjoint;
  suboptimal when a hospital sits at a graph bottleneck.

## 3. Simulation Framework (`simulation/engine.py`)

For each demand pair `(src, dst, passengers)`, the simulator computes a
time-dependent shortest path and accumulates per-edge load. This produces:

* total served vs unreachable passengers,
* average minutes per passenger,
* a per-edge load dictionary feeding the **traffic heatmap**.

Three scenarios are first-class: `scenario_road_closure`, `scenario_accident`
(weight × severity), and the default rush-hour run.

## 4. Performance Evaluation

Benchmark script: `tests/benchmarks.py`. Representative numbers on a typical
laptop CPU (mean of 20 runs):

| Algorithm | Mean (ms) |
|---|---|
| Kruskal MST (full graph)        | ~2 |
| Dijkstra (random pair)          | <1 |
| A* (random pair)                | <1 |
| Time-dependent Dijkstra         | <1 |
| DP transit allocation (250 buses) | ~80 |
| DP maintenance (40 cands, B=600) | ~25 |
| Greedy signal                   | <1 |
| Citywide simulation (morning)   | ~10 |

**Memoization speedup:** repeating the same 8 routes 5× drops total runtime
by ≈ 80% versus uncached calls.

## 5. Challenges & Solutions

| Challenge | Resolution |
|---|---|
| Mixed node IDs (ints + `"F1"` strings) | Coercion helper `_coerce` and `str(...)` keys for DSU & edge sets. |
| MST mixing build vs maintenance costs | Single normalized cost via `_priority_factor`, applied uniformly. |
| A* heuristic admissibility | Haversine distance / max speed expressed in **minutes**, matching the weight unit. |
| Time-dependent weights without recomputing the whole graph | `time_dependent_weight(period)` closure passed to Dijkstra as `weight_fn`. |
| Streamlit re-renders triggering full recompute | `@st.cache_resource` on dataset loading + `MemoizedRouter` between calls. |

## 6. Bonus Components

* **ML congestion forecast.** RandomForest (scikit-learn) trained on
  synthetic-expanded per-edge per-period traffic, predicts vehicles/hour
  given `(hour, distance, capacity, condition)`.
* **Side-by-side algorithm visualizer.** Tab "Dijkstra vs A*" shows both
  routes on the same map with timing & visited-node counts.
* **Containerization.** `Dockerfile` + `docker-compose.yml` runs the API and
  dashboard side-by-side: `docker compose up`.
* **REST API.** `FastAPI` exposes 8 endpoints with auto-generated OpenAPI at
  `/docs`.

## 7. Future Work

* Replace Random Forest with a recurrent model trained on real time-series
  Cairo traffic.
* Add per-vehicle agent-based simulation rather than aggregate edge load.
* Multi-objective MST (Pareto front of cost vs population coverage).
* Live deployment on Render / Vercel with HTTPS + auth.

## References

* Cormen, Leiserson, Rivest, Stein. *Introduction to Algorithms*, 4 ed.
* Cherkassky, Goldberg, Radzik. *Shortest paths algorithms: theory and
  experimental evaluation.*
* Webster, F. V. *Traffic signal settings* (1958).
