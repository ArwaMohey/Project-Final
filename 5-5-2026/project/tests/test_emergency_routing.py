import pytest
import math
from src.data.loader import load_dataset
from src.algorithms.shortest_path import a_star
from src.algorithms.greedy import emergency_priority

def test_astar_heuristic():
    ds = load_dataset()
    G = ds["graph_existing"]
    
    path, cost, stats = a_star(G, 1, "F1")
    
    assert path[0] == 1
    assert path[-1] == "F1"
    assert cost < math.inf

def test_emergency_priority_preemption():
    ds = load_dataset()
    G = ds["graph_existing"]
    
    requests = [{"id": "Amb1", "src": 1, "dst": "F9", "severity": 10}]
    results = emergency_priority(G, requests, "morning")
    
    assert len(results) == 1
    res = results[0]
    
    # Should provide up to 3 disjoint routes
    assert res["path1"] is not None
    assert res["eta1"] < math.inf