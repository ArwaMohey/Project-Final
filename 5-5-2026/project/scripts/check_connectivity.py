from src.data.loader import load_dataset
import networkx as nx
DS = load_dataset()
G = DS['graph_existing']

print("Graph Analysis:")
print(f"  Nodes: {G.number_of_nodes()}")
print(f"  Edges: {G.number_of_edges()}")
print(f"  Is connected: {nx.is_strongly_connected(G)}")
print(f"  Is weakly connected: {nx.is_weakly_connected(G)}")

# Find all pairs with paths
print("\nConnectivity between districts and facilities:")
facilities = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10']
districts = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

reachable_pairs = []
for src in districts:
    for dst in facilities:
        if nx.has_path(G, src, dst):
            reachable_pairs.append((src, dst))

print(f"Reachable pairs: {len(reachable_pairs)} out of {len(districts) * len(facilities)}")
print("\nSample reachable routes:")
for src, dst in reachable_pairs[:15]:
    print(f"  {src} -> {dst}")
