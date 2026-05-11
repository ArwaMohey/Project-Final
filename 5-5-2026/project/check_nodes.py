from data.loader import load_dataset
DS = load_dataset()
G = DS['graph_existing']
print('Available nodes:')
for n, d in G.nodes(data=True):
    kind = d.get('kind', '?')
    name = d.get('name', 'Unknown')
    print(f'  {str(n):5s} - {name:20s} (kind: {kind})')
print(f'\nTotal: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges')

# Find facilities that are reachable
print('\nReachable facilities:')
facilities = [n for n, d in G.nodes(data=True) if d.get('kind') == 'facility']
districts = [n for n, d in G.nodes(data=True) if d.get('kind') != 'facility']
print(f'Facilities: {facilities}')
print(f'Districts: {districts}')
