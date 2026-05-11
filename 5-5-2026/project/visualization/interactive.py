from __future__ import annotations
from typing import Dict, List, Optional, Tuple
import plotly.graph_objects as go
import networkx as nx

CAIRO_CENTER = dict(lat=30.04, lon=31.24)


def _node_traces(G: nx.DiGraph):
    dist_lat, dist_lon, dist_text, dist_size, dist_names = [], [], [], [], []
    fac_lat, fac_lon, fac_text, fac_names = [], [], [], []
    for n, d in G.nodes(data=True):
        if d["kind"] == "facility":
            fac_lat.append(d["y"]); fac_lon.append(d["x"])
            fac_text.append(f"<b>{d['name']}</b><br>{d['type']}")
            fac_names.append(d['name'])
        else:
            dist_lat.append(d["y"]); dist_lon.append(d["x"])
            dist_text.append(
                f"<b>{d['name']}</b><br>Pop: {d['pop']:,}<br>{d['type']}")
            dist_size.append(8 + d["pop"] / 50000)
            dist_names.append(d['name'])
    return [
        go.Scattermapbox(
            lat=dist_lat, lon=dist_lon, mode="markers+text",
            marker=dict(size=dist_size, color="#3b82f6", opacity=0.85),
            text=dist_names, textposition="top center", textfont=dict(size=10, color="black"),
            hoverinfo="text", hovertext=dist_text, name="Districts",
        ),
        go.Scattermapbox(
            lat=fac_lat, lon=fac_lon, mode="markers+text",
            marker=dict(size=14, color="#f59e0b", symbol="circle"),
            text=fac_names, textposition="top center", textfont=dict(size=10, color="black"),
            hoverinfo="text", hovertext=fac_text, name="Facilities",
        ),
    ]


def _edge_segments(G, edges, color, width, name, dash=False):
    lats, lons, texts = [], [], []
    for u, v in edges:
        if not G.has_edge(u, v):
            continue
        a, b = G.nodes[u], G.nodes[v]
        lats += [a["y"], b["y"], None]
        lons += [a["x"], b["x"], None]
        d = G[u][v]
        texts += [f"{a['name']} ↔ {b['name']}<br>"
                  f"{d['distance']} km · cap {d['capacity']}", "", ""]
    return go.Scattermapbox(
        lat=lats, lon=lons, mode="lines",
        line=dict(width=width, color=color),
        hoverinfo="text", text=texts, name=name,
        opacity=0.85,
    )


def map_network(G: nx.DiGraph,
                highlight_path: Optional[List] = None,
                second_path:    Optional[List] = None,
                third_path:     Optional[List] = None,
                title: str = "Greater Cairo Network") -> go.Figure:
    seen = set(); existing, potential = [], []
    for u, v, d in G.edges(data=True):
        k = tuple(sorted([str(u), str(v)]))
        if k in seen: continue
        seen.add(k)
        (potential if d["kind"] == "potential" else existing).append((u, v))

    traces = [
        _edge_segments(G, existing,  "#94a3b8", 2, "Existing roads"),
        _edge_segments(G, potential, "#cbd5e1", 1.5, "Potential roads"),
    ]
    if highlight_path and len(highlight_path) > 1:
        traces.append(_edge_segments(
            G, list(zip(highlight_path, highlight_path[1:])),
            "#dc2626", 6, "Route 1 (Primary)"))
    if second_path and len(second_path) > 1:
        traces.append(_edge_segments(
            G, list(zip(second_path, second_path[1:])),
            "#16a34a", 5, "Route 2 (Secondary)"))
    if third_path and len(third_path) > 1:
        traces.append(_edge_segments(
            G, list(zip(third_path, third_path[1:])),
            "#f59e0b", 4, "Route 3 (Tertiary)"))
            
    traces += _node_traces(G)

    fig = go.Figure(traces)
    fig.update_layout(
        title=title,
        mapbox=dict(style="open-street-map", center=CAIRO_CENTER, zoom=10.2),
        margin=dict(l=0, r=0, t=40, b=0),
        height=620,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01,
                    bgcolor="rgba(255,255,255,0.85)"),
    )
    return fig


def map_heatmap(G: nx.DiGraph, edge_load: Dict[tuple, float],
                title="Traffic load") -> go.Figure:
    max_load = max(edge_load.values()) if edge_load else 1
    seen = set(); traces = []
    
    for u, v in G.edges():
        k = tuple(sorted([str(u), str(v)]))
        if k in seen: continue
        seen.add(k)
        load = edge_load.get((u, v), 0) + edge_load.get((v, u), 0)
        ratio = load / max_load if max_load else 0
        ratio = min(1, ratio) 
        
        if ratio < 0.5:
            r = int(2 * ratio * 255); g = 200; b = 60
        else:
            r = 220; g = int(200 * (1 - (ratio - 0.5) * 2)); b = 50
            
        a, b_ = G.nodes[u], G.nodes[v]
        traces.append(go.Scattermapbox(
            lat=[a["y"], b_["y"]], lon=[a["x"], b_["x"]], mode="lines",
            line=dict(width=3 + 5 * ratio, color=f"rgb({r},{g},{b})"),
            hoverinfo="text",
            text=f"{a['name']} ↔ {b_['name']}<br>Load: {load:,.0f}",
            showlegend=False, opacity=0.9,
        ))
        
    traces += _node_traces(G)

    # --- إضافة مفتاح الألوان (Colorbar) ---
    traces.append(go.Scattermapbox(
        lat=[None], lon=[None], mode="markers",
        marker=dict(
            colorscale=[[0, "rgb(0,200,60)"], [0.5, "rgb(220,200,50)"], [1, "rgb(220,50,50)"]],
            cmin=0, cmax=max_load,
            showscale=True,
            colorbar=dict(
                title="Traffic Load<br>(Passengers)",
                thickness=15, x=0.02, y=0.5,
                bgcolor="rgba(255,255,255,0.8)"
            )
        ),
        showlegend=False, hoverinfo="none"
    ))

    fig = go.Figure(traces)
    fig.update_layout(
        title=title,
        mapbox=dict(style="carto-positron", center=CAIRO_CENTER, zoom=10.2),
        margin=dict(l=0, r=0, t=40, b=0), height=620, showlegend=False,
    )
    return fig


def bar_compare(labels, values_a, values_b, name_a, name_b, title):
    fig = go.Figure()
    fig.add_bar(x=labels, y=values_a, name=name_a, marker_color="#dc2626")
    fig.add_bar(x=labels, y=values_b, name=name_b, marker_color="#16a34a")
    fig.update_layout(title=title, barmode="group", height=380,
                      margin=dict(l=20, r=20, t=50, b=20))
    return fig