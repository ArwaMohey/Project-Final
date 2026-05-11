import pytest
import math
from data.loader import load_dataset
from algorithms.shortest_path import dijkstra, time_dependent_dijkstra

def test_standard_dijkstra():
    ds = load_dataset()
    G = ds["graph_existing"]
    
    path, cost, stats = dijkstra(G, 1, "F1")
    
    assert path[0] == 1
    assert path[-1] == "F1"
    assert cost < math.inf
    assert stats["visited"] > 0

def test_time_dependent_routing():
    ds = load_dataset()
    G = ds["graph_existing"]
    
    # Compare morning vs night routing
    path_m, cost_m, _ = time_dependent_dijkstra(G, 1, 4, "morning")
    path_n, cost_n, _ = time_dependent_dijkstra(G, 1, 4, "night")
    
    # Night traffic should generally yield a faster or equal travel time
    assert cost_n <= cost_m