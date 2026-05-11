import pytest
from src.data.loader import load_dataset
from src.simulation.engine import simulate_period, scenario_road_closure

def test_traffic_simulation():
    ds = load_dataset()
    G = ds["graph_existing"]
    demand = ds["transit_demand"]
    
    result = simulate_period(G, demand, "morning")
    
    assert result["period"] == "morning"
    assert result["served"] > 0
    assert "avg_minutes_per_pax" in result
    assert len(result["edge_load"]) > 0

def test_road_closure_scenario():
    ds = load_dataset()
    G = ds["graph_existing"]
    
    closed_G = scenario_road_closure(G, [(1, 3)])
    
    assert G.has_edge(1, 3) is True
    assert closed_G.has_edge(1, 3) is False
    assert closed_G.has_edge(3, 1) is False