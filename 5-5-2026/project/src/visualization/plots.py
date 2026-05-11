"""
Matplotlib-based visualization helpers.
All functions return a matplotlib Figure (so Streamlit / FastAPI can serve
them without opening a window).
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx


def _positions(G: nx.DiGraph):
    return {n: (d["x"], d["y"]) for n, d in G.nodes(data=True)}


def plot_network(G: nx.DiGraph, title="Greater Cairo Network",
                 highlight_edges: Optional[List] = None,
                 highlight_color="crimson"):
    fig, ax = plt.subplots(figsize=(11, 9))
    pos = _positions(G)
    # node colors by kind/type
    colors, sizes, labels = [], [], {}
    for n, d in G.nodes(data=True):
        if d["kind"] == "facility":
            colors.append("orange"); sizes.append(220)
        else:
            pop = d.get("pop", 0)
            colors.append("#3b82f6"); sizes.append(80 + pop / 4000)
        labels[n] = d["name"][:14]
    # edges
    existing = [(u, v) for u, v, d in G.edges(data=True) if d["kind"] == "existing"]
    potential = [(u, v) for u, v, d in G.edges(data=True) if d["kind"] == "potential"]
    nx.draw_networkx_edges(G, pos, edgelist=existing, ax=ax,
                           edge_color="#94a3b8", width=1.2, arrows=False, alpha=0.7)
    nx.draw_networkx_edges(G, pos, edgelist=potential, ax=ax,
                           edge_color="#a3a3a3", style="dashed",
                           width=1.0, arrows=False, alpha=0.4)
    if highlight_edges:
        nx.draw_networkx_edges(G, pos, edgelist=highlight_edges, ax=ax,
                               edge_color=highlight_color, width=3.5,
                               arrows=False)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=colors, node_size=sizes,
                           edgecolors="white", linewidths=1.2)
    nx.draw_networkx_labels(G, pos, labels=labels, ax=ax, font_size=7)
    ax.set_title(title); ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")
    ax.grid(True, alpha=0.2)
    return fig


def plot_path(G, path, title="Shortest path", color="crimson"):
    edges = list(zip(path, path[1:]))
    return plot_network(G, title=title, highlight_edges=edges,
                        highlight_color=color)


def plot_traffic_heatmap(G, edge_load: Dict[tuple, float],
                         title="Traffic load heatmap"):
    fig, ax = plt.subplots(figsize=(11, 9))
    pos = _positions(G)
    if edge_load:
        max_load = max(edge_load.values())
    else:
        max_load = 1
    edges = list(G.edges())
    widths, colors = [], []
    for u, v in edges:
        load = edge_load.get((u, v), 0) + edge_load.get((v, u), 0)
        ratio = load / max_load if max_load else 0
        widths.append(0.8 + 4 * ratio)
        # red intensity
        colors.append((0.85, 0.15 + 0.7*(1-ratio), 0.15 + 0.7*(1-ratio)))
    nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=colors,
                           width=widths, ax=ax, arrows=False)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=60, node_color="#1e293b")
    nx.draw_networkx_labels(G, pos, ax=ax,
                            labels={n: G.nodes[n]["name"][:10] for n in G},
                            font_size=6, font_color="white")
    ax.set_title(title); ax.grid(True, alpha=0.2)
    return fig


def plot_compare_paths(G, path_a, path_b,
                       label_a="Dijkstra", label_b="A*"):
    fig, axes = plt.subplots(1, 2, figsize=(20, 9))
    pos = _positions(G)
    for ax, path, lab, col in [(axes[0], path_a, label_a, "crimson"),
                               (axes[1], path_b, label_b, "#16a34a")]:
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#cbd5e1",
                               width=1, arrows=False)
        edges = list(zip(path, path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=edges, ax=ax,
                               edge_color=col, width=3.5, arrows=False)
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=60,
                               node_color="#1e293b")
        nx.draw_networkx_labels(G, pos, ax=ax,
            labels={n: G.nodes[n]["name"][:10] for n in G}, font_size=6,
            font_color="white")
        ax.set_title(f"{lab}: {len(path)} stops")
        ax.grid(True, alpha=0.2)
    return fig
