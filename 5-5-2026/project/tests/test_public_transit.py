import pytest
from data.loader import load_dataset
from algorithms.dynamic_programming import optimize_transit_schedule

def test_transit_dp_allocation():
    ds = load_dataset()
    routes = [{"id": r[0], "demand": r[3], "current_buses": r[2]} for r in ds["bus_routes"]]
    
    total_fleet = 200
    result = optimize_transit_schedule(routes, total_fleet)
    
    assert "allocation" in result
    assert result["total_buses_used"] <= total_fleet
    assert result["passengers_served"] > 0
    
    # Ensure every route got processed
    assert len(result["allocation"]) == len(routes)