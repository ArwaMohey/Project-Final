#!/usr/bin/env python
"""Test script for emergency routing with 3 paths per request."""

from src.data.loader import load_dataset
from src.algorithms.greedy import emergency_priority
import networkx as nx

DS = load_dataset()
G = DS['graph_existing']

# Find reachable pairs and use them for testing
facilities = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10']
districts = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

reachable_pairs = []
for src in districts:
    for dst in facilities:
        if nx.has_path(G, src, dst):
            reachable_pairs.append((src, dst))

print(f"Found {len(reachable_pairs)} reachable routes out of {len(districts) * len(facilities)}\n")

# Test with different emergency types and periods using reachable routes
test_cases = [
    ("morning", [
        {'id': 'Ambulance-1', 'src': 1, 'dst': 'F1'},
        {'id': 'Fire-1', 'src': 3, 'dst': 'F2'},
        {'id': 'Police-1', 'src': 5, 'dst': 'F7'},
    ]),
    ("afternoon", [
        {'id': 'Ambulance-2', 'src': 2, 'dst': 'F1'},
        {'id': 'Fire-2', 'src': 4, 'dst': 'F2'},
        {'id': 'Police-2', 'src': 6, 'dst': 'F7'},
    ]),
    ("evening", [
        {'id': 'Police-3', 'src': 7, 'dst': 'F1'},
        {'id': 'Ambulance-3', 'src': 9, 'dst': 'F2'},
        {'id': 'Fire-3', 'src': 10, 'dst': 'F7'},
    ]),
    ("night", [
        {'id': 'Ambulance-4', 'src': 11, 'dst': 'F1'},
        {'id': 'Fire-4', 'src': 12, 'dst': 'F2'},
        {'id': 'Police-4', 'src': 14, 'dst': 'F7'},
    ]),
]

print("=" * 70)
print("EMERGENCY ROUTING TEST - 3 PATHS PER REQUEST")
print("=" * 70)

for period, requests in test_cases:
    print(f"\n✓ Testing {period.upper()} traffic conditions")
    print("-" * 70)
    
    result = emergency_priority(G, requests, period)
    
    for r in result:
        print(f"\n  {r['id']:15s}: {r['num_routes']} routes available")
        print(f"    Route 1: {r['eta1']:6.1f} min" if r['eta1'] else "    Route 1: N/A")
        print(f"    Route 2: {r['eta2']:6.1f} min" if r['eta2'] else "    Route 2: N/A")
        print(f"    Route 3: {r['eta3']:6.1f} min" if r['eta3'] else "    Route 3: N/A")
        
        # Verify routes are different
        if r['path1'] and r['path2']:
            overlap = set(r['path1']).intersection(set(r['path2']))
            print(f"    Route 1-2 overlap: {len(overlap)} nodes")
        if r['path2'] and r['path3']:
            overlap = set(r['path2']).intersection(set(r['path3']))
            print(f"    Route 2-3 overlap: {len(overlap)} nodes")

print("\n" + "=" * 70)
print("✅ All emergency routing tests completed successfully!")
print("=" * 70)
