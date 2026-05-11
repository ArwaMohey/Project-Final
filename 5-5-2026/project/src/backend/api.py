"""
FastAPI backend exposing every algorithm as an HTTP endpoint.
Run:
    uvicorn src.backend.api:app --reload --port 8000
"""
from __future__ import annotations
from typing import List, Optional, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.data.loader import load_dataset
from src.algorithms import (
    kruskal_mst, dijkstra, a_star, time_dependent_dijkstra,
    optimize_transit_schedule, road_maintenance_allocation,
    traffic_signal_optimization, emergency_priority, MemoizedRouter,
)
from src.simulation import simulate_period, scenario_road_closure, scenario_accident

DS = load_dataset()
G_EX  = DS["graph_existing"]
G_FUL = DS["graph_full"]
ROUTER = MemoizedRouter(G_EX)

# Cache ML model
try:
    from src.ml.congestion import train_model
    ML_MODEL, ML_METRICS = train_model()
except Exception:
    ML_MODEL, ML_METRICS = None, None


def _coerce(node: str):
    """Allow '3' or 'F1' in URLs."""
    if node.isdigit(): return int(node)
    return node


def _serialize_path(path):
    return [{"id": str(n), "name": G_EX.nodes[n]["name"]} for n in path]


app = FastAPI(title="Smart City — Cairo Transportation API",
              version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])


@app.get("/")
def root():
    return {"ok": True,
            "endpoints": ["/shortest-path", "/emergency-route",
                          "/mst-network", "/simulate-traffic",
                          "/optimize-transit", "/maintenance",
                          "/signal", "/predict-congestion"]}


@app.get("/shortest-path")
def shortest_path(src: str, dst: str, period: str = "afternoon"):
    s, d = _coerce(src), _coerce(dst)
    if s not in G_EX or d not in G_EX:
        raise HTTPException(404, "Unknown node")
    path, cost = ROUTER.query(s, d, period)
    if not path:
        raise HTTPException(404, "No path")
    return {"period": period, "minutes": round(cost, 2),
            "stops": _serialize_path(path),
            "cache": {"hits": ROUTER.hits, "misses": ROUTER.misses}}


@app.get("/emergency-route")
def emergency_route(src: str, dst: str):
    s, d = _coerce(src), _coerce(dst)
    path, cost, stats = a_star(G_EX, s, d)
    dij_path, dij_cost, dij_stats = dijkstra(G_EX, s, d)
    if not path:
        raise HTTPException(404, "No path")
    return {
        "astar":    {"minutes": round(cost, 2),
                     "visited": stats["visited"],
                     "stops": _serialize_path(path)},
        "dijkstra": {"minutes": round(dij_cost, 2),
                     "visited": dij_stats["visited"],
                     "stops": _serialize_path(dij_path)},
    }


@app.get("/mst-network")
def mst_network():
    out = kruskal_mst(G_FUL)
    return {
        "n_edges": out["n_edges"],
        "construction_cost_MEGP":      out["construction_cost_MEGP"],
        "baseline_construction_MEGP":  out["baseline_construction_MEGP"],
        "savings_construction_MEGP":   out["savings_construction_MEGP"],
        "complexity": out["complexity"],
        "edges": [{"from": str(u), "to": str(v),
                   "kind": d["kind"], "distance": d["distance"]}
                  for u, v, d in out["edges"]],
    }


class SimRequest(BaseModel):
    period: str = "morning"
    closed_edges: List[List[str]] = []   # e.g. [["3","5"]]
    accident:     Optional[List[str]] = None  # ["7","8"]


@app.post("/simulate-traffic")
def simulate_traffic(req: SimRequest):
    G = G_EX
    if req.closed_edges:
        G = scenario_road_closure(
            G, [(_coerce(a), _coerce(b)) for a, b in req.closed_edges])
    if req.accident:
        a, b = req.accident
        G = scenario_accident(G, (_coerce(a), _coerce(b)))
    res = simulate_period(G, DS["transit_demand"], req.period)
    return {"period": res["period"],
            "served": res["served"],
            "unreachable": res["unreachable"],
            "avg_minutes_per_pax": round(res["avg_minutes_per_pax"], 2),
            "edges_loaded": len(res["edge_load"])}


@app.get("/optimize-transit")
def optimize_transit(total_buses: int = 250):
    routes = []
    for rid, stops, buses, pax in DS["bus_routes"]:
        routes.append({"id": rid, "demand": pax, "current_buses": buses})
    return optimize_transit_schedule(routes, total_buses)


@app.get("/maintenance")
def maintenance(budget_MEGP: float = 800):
    candidates = []
    seen = set()
    # Build candidates from existing roads with cond <= 7
    for u, v, d in G_EX.edges(data=True):
        key = tuple(sorted([str(u), str(v)]))
        if key in seen or d["kind"] != "existing": continue
        seen.add(key)
        if d["condition"] > 7: continue
        cost = d["distance"] * (11 - d["condition"]) * 4   # M EGP
        benefit = (G_EX.nodes[u].get("pop", 50000) +
                   G_EX.nodes[v].get("pop", 50000)) / 1000.0
        candidates.append({"id": f"{u}-{v}", "cost_MEGP": round(cost, 1),
                           "benefit": round(benefit, 1)})
    return road_maintenance_allocation(candidates, budget_MEGP)


@app.get("/signal")
def signal(north: int = 1500, south: int = 1400,
           east: int = 900, west: int = 1100):
    return traffic_signal_optimization(
        {"N": north, "S": south, "E": east, "W": west})


@app.get("/predict-congestion")
def predict_congestion(u: str, v: str, hour: int = 8):
    if ML_MODEL is None:
        raise HTTPException(500, "ML model unavailable")
    try:
        from src.ml.congestion import predict_congestion as _pred
    except Exception as e:
        raise HTTPException(500, f"ML unavailable: {e}")
    a, b = _coerce(u), _coerce(v)
    if not G_EX.has_edge(a, b):
        raise HTTPException(404, "Edge not found")
    return {
        "edge": [str(a), str(b)],
        "hour": hour,
        "predicted_vph": round(_pred(ML_MODEL, G_EX[a][b], hour), 1),
        "model_mae_vph": round(ML_METRICS["mae_vph"], 1),
    }
