# Smart City Transportation Network Optimization — Greater Cairo

CSE112 (AIU) — Design & Analysis of Algorithms project.

A complete, demo-ready Python system that models, optimizes, simulates and
visualizes the **Greater Cairo** transportation network using graph algorithms,
dynamic programming, greedy methods and an ML traffic-prediction bonus —
delivered with a polished interactive **Streamlit + Plotly map dashboard**, a
**FastAPI REST backend**, and a one-command **Docker Compose** setup.

![dashboard preview](https://img.shields.io/badge/Streamlit-dashboard-ff4b4b?logo=streamlit)
![api preview](https://img.shields.io/badge/FastAPI-backend-009485?logo=fastapi)
![docker](https://img.shields.io/badge/Docker-compose-2496ED?logo=docker)
![python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)

## ✨ Highlights

| Module | Algorithms |
|---|---|
| `algorithms/mst.py` | **Kruskal** MST with population & critical-facility priority modifiers + cost-savings analysis |
| `algorithms/shortest_path.py` | **Dijkstra**, **A\*** (haversine heuristic), **time-dependent Dijkstra**, **memoized router** |
| `algorithms/dynamic_programming.py` | **DP transit scheduling** (knapsack), **DP road-maintenance** (0/1 knapsack) |
| `algorithms/greedy.py` | **Greedy signal timing** w/ Webster reference, **emergency vehicle preemption** |
| `simulation/engine.py` | Time-stepped simulation, **rush hour / accident / road-closure** scenarios |
| `visualization/` | Matplotlib + **Plotly OpenStreetMap** interactive maps |
| `ml/congestion.py` | **RandomForest** congestion forecasting (scikit-learn) |
| `backend/api.py` | **FastAPI** REST endpoints with OpenAPI docs at `/docs` |
| `app.py` | **Streamlit** dashboard with 10 tabs, interactive maps, comparison charts |

## 📁 Project structure

```
project/
├── algorithms/           # MST, shortest-path, DP, greedy
├── backend/api.py        # FastAPI backend
├── data/                 # Cairo dataset + graph builder
├── ml/                   # ML congestion model
├── simulation/           # Traffic simulation engine
├── visualization/        # Matplotlib + Plotly helpers
├── tests/
│   ├── test_algorithms.py
│   └── benchmarks.py
├── app.py                # Streamlit dashboard
├── docs/REPORT.md        # Full technical report
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## 🚀 Quick start (local Python)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Dashboard:
PYTHONPATH=. streamlit run app.py
# → open http://localhost:8501

# REST API:
PYTHONPATH=. uvicorn src.backend.api:app --reload
# → open http://localhost:8000/docs

# Tests + benchmarks:
PYTHONPATH=. python tests/test_algorithms.py
PYTHONPATH=. python tests/benchmarks.py
```

## 🐳 Docker (one command)

Run **API + dashboard** together:

```bash
docker compose up --build
```

* Dashboard → http://localhost:8501
* REST API  → http://localhost:8000/docs

Or just the dashboard:

```bash
docker build -t cairo-transport .
docker run -p 8501:8501 cairo-transport
```

## 🧪 REST endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/shortest-path?src=1&dst=4&period=morning` | Time-dependent Dijkstra |
| GET | `/emergency-route?src=12&dst=F1` | A* + Dijkstra side-by-side |
| GET | `/mst-network` | Kruskal MST + cost analysis |
| POST | `/simulate-traffic` | Period simulation w/ accident & closure scenarios |
| GET | `/optimize-transit?total_buses=250` | DP bus fleet allocation |
| GET | `/maintenance?budget_MEGP=800` | DP knapsack road repair |
| GET | `/signal?north=1500&...` | Greedy signal plan |
| GET | `/predict-congestion?u=3&v=5&hour=8` | ML traffic forecast |

## 📊 Algorithm complexities

| Algorithm | Time | Space |
|---|---|---|
| Kruskal MST | O(E log E) | O(V) |
| Dijkstra | O((V+E) log V) | O(V) |
| A* | O((V+E) log V), heuristic-pruned | O(V) |
| DP transit allocation | O(R · B · Bmax) | O(R · B) |
| DP maintenance | O(N · Budget) | O(N · Budget) |
| Greedy signal | O(K log K) | O(K) |
| Simulation | O(D · (V+E) log V) | O(E) |

See **[REPORT.md](./docs/REPORT.md)** for the full technical report.

## 🎓 Authored for

CSE112 — Design and Analysis of Algorithms — Alamein International University.
