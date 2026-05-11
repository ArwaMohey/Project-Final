# 🚦 Greater Cairo — Smart Transportation Optimizer

> **CSE112 · Design and Analysis of Algorithms**
> Alamein International University · Faculty of Engineering & Computer Science

A full-stack transportation intelligence system for the Greater Cairo metropolitan area, combining classical graph algorithms, dynamic programming, greedy heuristics, and machine learning to optimize routing, infrastructure planning, emergency dispatch, and transit scheduling — all rendered on an interactive Plotly/Mapbox dashboard.

---

## ✨ Features at a Glance

| Module | Algorithm | What it Solves |
|--------|-----------|----------------|
| 🌳 MST Builder | Kruskal + Union-Find | Minimum-cost road network expansion |
| 🗺️ Routing | Dijkstra (time-dependent) | Fastest path across traffic periods |
| ⚡ Racing | Dijkstra vs. A* | Live efficiency comparison |
| 🚑 Emergency | A* with preemption | 3 edge-disjoint routes to hospitals |
| 🚌 Transit DP | Bounded Resource DP | Optimal bus/metro fleet allocation |
| 🔧 Maintenance | 0/1 Knapsack DP | Budget-constrained road repair |
| 🚦 Signals | Greedy (Webster ref.) | Traffic signal green-time planning |
| 🔥 Simulation | Time-dep. Dijkstra | Citywide demand & congestion heatmap |
| 🤖 ML Forecast | Random Forest | 24-hour per-edge congestion prediction |

---

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Network Dataset](#network-dataset)
- [Dashboard Features](#dashboard-streamlit-app)
- [Algorithm Modules](#algorithm-modules)
- [REST API](#rest-api)
- [Running Tests](#running-tests)
- [Technologies](#technologies)
- [Performance Characteristics](#performance-characteristics)
- [Authors](#authors)

---

## 🚀 Quick Start

### Prerequisites

- Python **3.10+**
- pip

### 1 — Clone & Install

```bash
git clone <repo-url>
cd project
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2 — Launch the Dashboard

```bash
PYTHONPATH=. streamlit run app.py
```

Open **http://localhost:8501** in your browser.

### 3 — (Optional) Launch the REST API

```bash
PYTHONPATH=. uvicorn src.backend.api:app --reload --port 8000
```

Interactive docs at **http://localhost:8000/docs**

### 4 — (Optional) Run with Docker & Docker Compose

**Single container:**
```bash
docker build -t cairo-transport .
docker run -p 8501:8501 cairo-transport
```

**Both API + Dashboard:**
```bash
docker-compose up
```

- Dashboard: **http://localhost:8501**
- API: **http://localhost:8000/docs**

---

## 📁 Project Structure

```
project/
├── app.py                        # Streamlit 10-tab dashboard (main entry point)
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Container image definition
├── docker-compose.yml            # Orchestrate API + Dashboard
├── README.md                     # This file
│
├── src/                          # Core project modules
│   ├── data/
│   │   ├── cairo_data.py         # Static dataset: nodes, roads, traffic, metro, buses
│   │   └── loader.py             # Graph builder, haversine, edge_weight()
│   │
│   ├── algorithms/
│   │   ├── __init__.py           # Public API re-exports
│   │   ├── shortest_path.py      # Dijkstra, A*, Time-Dependent Dijkstra, MemoizedRouter
│   │   ├── mst.py                # Kruskal MST + Union-Find (path-halving + union-by-rank)
│   │   ├── greedy.py             # Signal optimizer + Emergency priority dispatch
│   │   └── dynamic_programming.py # Transit fleet DP + 0/1 Knapsack
│   │
│   ├── simulation/
│   │   └── engine.py             # simulate_period(), scenario_road_closure(), scenario_accident()
│   │
│   ├── ml/
│   │   └── congestion.py         # Random Forest pipeline: train_model(), predict_congestion()
│   │
│   ├── visualization/
│   │   ├── interactive.py        # map_network(), map_heatmap(), bar_compare(), _edge_segments()
│   │   └── plots.py              # Supplementary chart helpers
│   │
│   └── backend/
│       └── api.py                # FastAPI REST endpoints for all algorithm modules
│
├── tests/                        # Test suite
│   ├── test_algorithms.py
│   ├── test_routing.py
│   ├── test_routing_traffic.py
│   ├── test_mst.py
│   ├── test_emergency_routing.py
│   ├── test_emergency.py
│   ├── test_public_transit.py
│   ├── test_integration_sim.py
│   ├── test_data.py
│   ├── test_bonus.py
│   └── benchmarks.py
│
└── scripts/                      # Utility scripts
    ├── check_connectivity.py
    ├── check_nodes.py
    └── report.js
```

---

## 🗂️ Network Dataset

The Cairo graph models **25 nodes** and **70+ directed edges**.

### Districts (15)

| ID | Name | Population | Type |
|----|------|-----------|------|
| 1 | Maadi | 250,000 | Residential |
| 2 | Nasr City | 500,000 | Mixed |
| 3 | Downtown Cairo | 100,000 | Business |
| 4 | New Cairo | 300,000 | Residential |
| 7 | 6th October City | 400,000 | Mixed |
| 8 | Giza | 550,000 | Mixed |
| 11 | Shubra | 450,000 | Residential |
| 12 | Helwan | 350,000 | Industrial |
| 13 | New Administrative Capital | 50,000 | Government |
| … | *(15 total)* | | |

### Key Facilities (10)

| ID | Name | Type |
|----|------|------|
| F1 | Cairo International Airport | Airport |
| F2 | Ramses Railway Station | Transit Hub |
| F9 | Qasr El Aini Hospital | **Medical** |
| F10 | Maadi Military Hospital | **Medical** |
| F7 | Smart Village | Business |
| … | *(10 total)* | |

### Traffic Periods

| Period | Hours | Characteristic |
|--------|-------|---------------|
| `morning` | 06:00–11:00 | Peak inbound commute |
| `afternoon` | 11:00–16:00 | Inter-district movement |
| `evening` | 16:00–21:00 | Peak outbound commute |
| `night` | 21:00–06:00 | Minimal traffic |

### Edge Weight Formula

```
W(e) = (distance / speed_factor) × 60 × congestion_multiplier × condition_multiplier
```

- **congestion_multiplier** = `1 + 0.8 × (traffic_vph / capacity)²`  *(BPR-inspired)*
- **condition_multiplier** = `1.0 + (10 - condition) × 0.05`

---

## 🧮 Algorithm Modules

### Kruskal MST · `src/algorithms/mst.py`

```python
from src.algorithms import kruskal_mst
result = kruskal_mst(graph_full)
# result["edges"], result["construction_cost_MEGP"], result["savings_construction_MEGP"]
```

- Existing roads: cost = `distance × (11 − condition)`
- Potential roads: cost = construction cost (M EGP)
- Critical facilities (Medical, Airport) get a **0.6× discount**; high-pop districts get **0.7×**
- **Complexity:** O(E log E) time · O(V) space

---

### Dijkstra · `src/algorithms/shortest_path.py`

```python
from src.algorithms import dijkstra
path, cost, stats = dijkstra(G, src="Helwan", dst="F1")
# stats["visited"] — nodes expanded
```

- Lazy-deletion min-heap (Python `heapq`)
- Accepts a pluggable `weight_fn(u, v, data) → float`
- **Complexity:** O((V+E) log V)

---

### A* Search · `src/algorithms/shortest_path.py`

```python
from src.algorithms import a_star
path, cost, stats = a_star(G, src=12, dst="F1")
```

- Heuristic: `haversine(n, dst) / 90 km/h → minutes` (admissible)
- Guaranteed optimal; expands **30–65% fewer nodes** than Dijkstra on Cairo graph
- **Complexity:** O((V+E) log V) worst-case; significantly better in practice

---

### Time-Dependent Dijkstra · `src/algorithms/shortest_path.py`

```python
from src.algorithms import time_dependent_dijkstra
path, cost, _ = time_dependent_dijkstra(G, src=3, dst="F1", period="morning")
```

---

### Emergency Dispatch · `src/algorithms/greedy.py`

```python
from src.algorithms import emergency_priority
routes = emergency_priority(G, [{"id": "Ambulance", "src": 12, "dst": "F9"}], period="morning")
# routes[0]["path1"], ["path2"], ["path3"], ["eta1"], ["eta2"], ["eta3"]
```

- Uses A* with **signal preemption** (congestion = 0)
- Generates up to **3 edge-disjoint** alternative routes for resilience
- Destination **must be a Medical facility node**
- **Complexity:** O(3 × (V+E) log V)

---

### Transit Fleet DP · `src/algorithms/dynamic_programming.py`

```python
from src.algorithms import optimize_transit_schedule
result = optimize_transit_schedule(routes, total_vehicles=100)
# result["allocation"], result["passengers_served"]
```

- DP state: `dp[i][b]` = max passengers when first `i` routes share `b` vehicles
- **Complexity:** O(R × B × B_max)

---

### Road Maintenance Knapsack · `src/algorithms/dynamic_programming.py`

```python
from src.algorithms import road_maintenance_allocation
result = road_maintenance_allocation(candidates, budget_MEGP=800)
# result["selected"], result["total_benefit"], result["spent_MEGP"]
```

- 1-D rolling knapsack (memory-efficient)
- Benefit = `(pop_u + pop_v) / 1000`; Cost = `distance × (11 − condition) × 4 M EGP`
- **Complexity:** O(N × Budget_scaled)

---

### Traffic Signal Optimizer · `src/algorithms/greedy.py`

```python
from src.algorithms import traffic_signal_optimization
sig = traffic_signal_optimization({"N": 1500, "S": 1300, "E": 900, "W": 1100})
# sig["greedy_plan_seconds"], sig["webster_reference"], sig["cycle_seconds"]
```

- Green time proportional to incoming vehicle counts
- Benchmarked against **Webster's formula** `C = (1.5L+5)/(1−Σy)`
- **Complexity:** O(K log K)

---

### Traffic Simulation · `src/simulation/engine.py`

```python
from src.simulation import simulate_period, scenario_accident, scenario_road_closure
result = simulate_period(G, transit_demand, period="morning")
# result["served"], result["unreachable"], result["avg_minutes_per_pax"], result["edge_load"]

H = scenario_accident(G, accident_edge=(8, 12), severity=5)
H = scenario_road_closure(G, closed_edges=[(3, 5)])
```

---

### ML Congestion Forecast · `src/ml/congestion.py`

```python
from src.ml.congestion import train_model, predict_congestion
model, metrics = train_model()           # ~1.5s training
vph = predict_congestion(model, G[3]["F1"], hour=8)
```

- **Features:** hour, period (one-hot), distance, capacity, condition
- **Target:** vehicles/hour
- Synthetic data expansion: 6 noisy samples per (edge × period) pair → 672 training rows
- **Model:** `RandomForestRegressor(n_estimators=120)`
- Typical MAE: **65–90 vph** (~2–4% relative error)

---

### MemoizedRouter · `src/algorithms/shortest_path.py`

```python
from src.algorithms import MemoizedRouter
router = MemoizedRouter(G)
path, cost = router.query(src=12, dst="F1", period="morning")
# O(1) on repeated queries; tracks router.hits / router.misses
```

---

## � Dashboard (Streamlit App)

Interactive 10-tab Streamlit dashboard for visualizing and experimenting with all algorithms.

| Tab | Module | Features |
|-----|--------|----------|
| **Network Overview** | Data | Interactive Mapbox with 25 nodes, 70+ edges; toggle planned roads |
| **MST** | Kruskal | Visualize Minimum Spanning Tree; cost savings analysis |
| **Routing** | Dijkstra | Query fastest path; view visited nodes; time-dependent periods |
| **Dijkstra vs A*** | Comparison | Side-by-side pathfinding; efficiency benchmark (nodes expanded) |
| **Emergency Priority** | A* Greedy | Route 3 edge-disjoint paths to hospitals; ETA calculation |
| **Simulation** | Time-Step Engine | Aggregate traffic demand; compute edge loads & congestion |
| **Transit DP** | Fleet Allocation | Optimize bus/metro fleet across routes; passengers served |
| **Maintenance DP** | Knapsack | Budget-constrained road repair selection |
| **Signal Greedy** | Traffic Signals | Compute signal timing plans; compare vs Webster formula |
| **ML Forecast** | Random Forest | 24-hour per-edge congestion prediction; model accuracy metrics |

All visualizations are **interactive Plotly** with Mapbox, zooming, and real-time parameter tweaking.

---



Start the API server:

```bash
PYTHONPATH=. uvicorn src.backend.api:app --reload --port 8000
```

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/network/stats` | Node/edge counts |
| `GET` | `/mst` | Kruskal MST result |
| `GET` | `/route/{src}/{dst}?period=morning` | Time-dependent shortest path |
| `GET` | `/compare/{src}/{dst}` | Dijkstra vs. A* comparison |
| `POST` | `/emergency` | Emergency dispatch (JSON body) |
| `GET` | `/simulate/{period}` | Simulate traffic period |
| `POST` | `/transit/schedule` | Optimize fleet allocation |
| `POST` | `/maintenance` | Knapsack road allocation |
| `POST` | `/signals` | Signal timing plan |
| `GET` | `/ml/forecast/{u}/{v}` | 24-hour congestion forecast |

Interactive docs: **http://localhost:8000/docs**

---

## 🧪 Running Tests

All tests use pytest and the project structure with `PYTHONPATH`.

```bash
# All tests
PYTHONPATH=. pytest tests/ -v

# Specific test files
PYTHONPATH=. pytest tests/test_routing.py -v
PYTHONPATH=. pytest tests/test_emergency_routing.py -v
PYTHONPATH=. pytest tests/test_mst.py -v
PYTHONPATH=. pytest tests/test_algorithms.py -v
PYTHONPATH=. pytest tests/test_public_transit.py -v
PYTHONPATH=. pytest tests/test_integration_sim.py -v

# Performance benchmarks
PYTHONPATH=. python tests/benchmarks.py
```

### Test Coverage

- **test_algorithms.py** — Core algorithm validation
- **test_routing.py** — Shortest path routing
- **test_routing_traffic.py** — Time-dependent routing & traffic
- **test_mst.py** — Minimum spanning tree construction
- **test_emergency_routing.py** — 3-disjoint-path emergency dispatch
- **test_emergency.py** — Emergency scenario handling
- **test_public_transit.py** — Transit fleet optimization
- **test_integration_sim.py** — Full-system simulation integration
- **test_data.py** — Dataset loading & validation
- **test_bonus.py** — Bonus features
- **benchmarks.py** — Algorithm performance profiling

---

## 🛠️ Technologies

| Tool | Version | Role |
|------|---------|------|
| Python | 3.10+ | Core language |
| Streamlit | ≥1.32 | Interactive dashboard |
| NetworkX | ≥3.2 | Graph data structure & utilities |
| Plotly | ≥5.18 | Interactive Mapbox visualizations |
| scikit-learn | ≥1.4 | Random Forest ML pipeline |
| pandas / numpy | latest | Data manipulation |
| FastAPI + Uvicorn | ≥0.110 | REST API backend |

---

## ⚡ Performance Characteristics

| Algorithm | Time Complexity | Space | Notes |
|-----------|-----------------|-------|-------|
| Kruskal MST | O(E log E) | O(V) | Path-halving + union-by-rank |
| Dijkstra | O((V+E) log V) | O(V) | Lazy-deletion min-heap |
| A* | O((V+E) log V) | O(V) | Typically 30–65% fewer node expansions than Dijkstra |
| Time-Dependent Dijkstra | O((V+E) log V × T) | O(V×T) | T = number of time periods (4) |
| Emergency Dispatch (3-disjoint) | O(3 × (V+E) log V) | O(V) | 3 separate A* searches |
| Transit Fleet DP | O(R × B²) | O(B) | R = routes, B = vehicles; 1-D rolling array |
| Road Maintenance Knapsack | O(N × Budget) | O(Budget) | 1-D rolling knapsack; memory-efficient |
| Traffic Signals (Greedy) | O(K log K) | O(K) | K = number of approaches |
| Traffic Simulation | O(D × (V+E) log V) | O(E) | D = demand instances; time-dependent routing |
| ML Forecast (Random Forest) | O(672 × trees × depth) | O(features) | 672 training rows; ~1.5s per model |

### Typical Performance on Cairo Graph (25 nodes, 70+ edges)

- **Routing query:** ~2–5ms per path (Dijkstra)
- **A* query:** ~1–3ms per path (faster heuristic)
- **Emergency (3-disjoint):** ~5–10ms (3 parallel A* searches)
- **Full simulation (morning period):** ~50–200ms
- **ML prediction:** ~10–50ms (inference on new edge)
- **Kruskal MST construction:** ~1–2ms

---

## � Troubleshooting

### "ModuleNotFoundError: No module named 'src'"
Set the `PYTHONPATH` environment variable:
```bash
PYTHONPATH=. streamlit run app.py
# Or set globally
export PYTHONPATH=.
streamlit run app.py
```

### "No module named 'streamlit'" or dependency errors
Ensure you've installed requirements:
```bash
pip install -r requirements.txt
```

### Port 8501 already in use
The Streamlit port is in use by another process. Specify a different port:
```bash
streamlit run app.py --server.port 8502
```

### API won't start (Port 8000 in use)
Change the API port:
```bash
uvicorn src.backend.api:app --port 8001
```

### Mapbox visualization not displaying
Ensure Plotly is installed and internet connection is available for Mapbox tiles:
```bash
pip install --upgrade plotly
```

### Tests fail with import errors
Ensure PYTHONPATH is set:
```bash
PYTHONPATH=. pytest tests/ -v
```

---

## �👥 Authors

**Alamein International University**
Faculty of Engineering & Computer Science
CSE112 — Design and Analysis of Algorithms · 2024–2025

---

## 📄 License

Academic project — submitted for CSE112 course evaluation.
Not licensed for commercial use.
