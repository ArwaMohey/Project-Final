"""
Greater Cairo — Smart Transportation Optimizer
CSE112 · Design & Analysis of Algorithms · Alamein International University
=============================================================================
Run:   PYTHONPATH=. streamlit run app.py
"""
import time
import math
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import networkx as nx

from src.data.loader import load_dataset
from src.algorithms import (
    kruskal_mst, dijkstra, a_star, time_dependent_dijkstra,
    optimize_transit_schedule, road_maintenance_allocation,
    traffic_signal_optimization, emergency_priority, MemoizedRouter,
)
from src.simulation import simulate_period, scenario_road_closure, scenario_accident
from src.visualization.interactive import (
    map_network, map_heatmap, bar_compare,
    _edge_segments, _node_traces, CAIRO_CENTER,
)

# ══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Cairo Smart Transport",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
:root {
  --brand:#0ea5e9; --brand-dark:#0284c7; --accent:#f59e0b;
  --danger:#ef4444; --success:#22c55e;
  --surface:#f8fafc; --surface2:#f1f5f9; --border:#e2e8f0;
  --text:#0f172a; --muted:#64748b;
}
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; color:var(--text); font-size:16px; }
h1,h2,h3,h4 { font-family:'Syne',sans-serif !important; letter-spacing:-0.02em; font-size:1.5em; }
h1 { font-size:2em; }
h3 { font-size:1.3em; }
p, li, div { font-size:16px; line-height:1.6; }
#MainMenu, footer, header { visibility:hidden; }
.block-container { max-width:1600px; padding-top:1.2rem; }

[data-testid="stSidebar"] {
  background:linear-gradient(175deg,#0f172a 0%,#1e293b 60%,#0f172a 100%);
  border-right:1px solid #334155;
}
[data-testid="stSidebar"] * { color:#e2e8f0 !important; }
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3
  { color:#f1f5f9 !important; font-family:'Syne',sans-serif !important; }
[data-testid="stSidebar"] [data-testid="stMetricLabel"] { color:#94a3b8 !important; }
[data-testid="stSidebar"] [data-testid="stMetricValue"]
  { color:#38bdf8 !important; font-size:1.6rem !important; font-weight:700 !important; }
[data-testid="stSidebar"] hr { border-color:#334155 !important; }

[data-testid="stMetricValue"]
  { font-family:'Syne',sans-serif !important; font-weight:800 !important;
    font-size:1.8rem !important; color:var(--brand) !important; }
[data-testid="stMetricLabel"]
  { font-size:0.78rem !important; color:var(--muted) !important;
    text-transform:uppercase; letter-spacing:0.06em; }

.stTabs [data-baseweb="tab-list"]
  { gap:4px; background:var(--surface2); padding:4px; border-radius:12px;
    border:1px solid var(--border); }
.stTabs [data-baseweb="tab"]
  { border-radius:8px; padding:0.45rem 1rem; font-weight:600; font-size:0.83rem;
    color:var(--muted); border:none !important; background:transparent; transition:all 0.2s; }
.stTabs [aria-selected="true"]
  { background:white !important; color:var(--brand) !important;
    box-shadow:0 1px 4px rgba(0,0,0,0.08); }

.hero {
  background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 50%,#0c4a6e 100%);
  border-radius:18px; padding:2rem 2.4rem; margin-bottom:1.4rem;
  position:relative; overflow:hidden;
}
.hero::before {
  content:''; position:absolute; top:-40px; right:-60px;
  width:280px; height:280px;
  background:radial-gradient(circle,rgba(14,165,233,0.25) 0%,transparent 70%);
  border-radius:50%;
}
.hero h1 { color:white !important; font-size:2rem !important; font-weight:800 !important; margin:0 !important; }
.hero p  { color:#94a3b8; font-size:0.95rem; margin:0.5rem 0 0; font-weight:300; }
.hero-tag {
  display:inline-block; padding:3px 12px; border-radius:999px;
  background:rgba(14,165,233,0.2); border:1px solid rgba(14,165,233,0.4);
  color:#7dd3fc !important; font-size:0.72rem; font-weight:600;
  letter-spacing:0.08em; text-transform:uppercase; margin-bottom:0.6rem;
}

.algo-badge {
  display:inline-flex; align-items:center; gap:5px;
  padding:4px 10px; border-radius:999px;
  background:#eff6ff; border:1px solid #bfdbfe;
  color:#1d4ed8; font-size:0.72rem; font-weight:600; margin:2px;
}

.section-header {
  display:flex; align-items:center; gap:10px;
  margin-bottom:1rem; padding-bottom:0.6rem; border-bottom:2px solid var(--border);
}
.section-header h3 { margin:0 !important; font-size:1.15rem !important; font-weight:700 !important; }

.complexity {
  font-size:0.78rem; background:#f1f5f9; border:1px solid #e2e8f0;
  border-radius:8px; padding:6px 12px; color:#475569;
  display:inline-block; margin-top:6px; font-family:monospace;
}

.info-callout {
  background:#eff6ff; border:1px solid #bfdbfe; border-radius:10px;
  padding:10px 14px; font-size:0.83rem; color:#1e40af; margin-bottom:0.8rem;
}
.warn-callout {
  background:#fffbeb; border:1px solid #fcd34d; border-radius:10px;
  padding:10px 14px; font-size:0.83rem; color:#92400e; margin-bottom:0.8rem;
}

.stButton > button
  { border-radius:10px !important; font-weight:600 !important; transition:all 0.18s !important; }
.stButton > button[kind="primary"]
  { background:linear-gradient(135deg,var(--brand),var(--brand-dark)) !important;
    color:white !important; box-shadow:0 2px 8px rgba(14,165,233,0.35) !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# DATA + CACHE
# ══════════════════════════════════════════════════════════════
@st.cache_resource
def _load():
    ds = load_dataset()
    router = MemoizedRouter(ds["graph_existing"])
    return ds, router

DS, ROUTER = _load()
G  = DS["graph_existing"]
GF = DS["graph_full"]

# 1. Full Node List (For standard point-to-point routing)
all_nodes = sorted(G.nodes(), key=lambda n: G.nodes[n]["name"])
NODE_OPTIONS = {f"{G.nodes[n]['name']} ({n})": n for n in all_nodes}
NODE_LABELS  = list(NODE_OPTIONS.keys())

def _idx(node_id):
    for i, k in enumerate(NODE_LABELS):
        if NODE_OPTIONS[k] == node_id:
            return i
    return 0

# 2. Hospital Node List (Strictly for Emergency Routing destinations)
HOSPITAL_OPTIONS = {f"{G.nodes[n]['name']} ({n})": n for n in all_nodes if G.nodes[n].get("type") == "Medical"}
HOSPITAL_LABELS = list(HOSPITAL_OPTIONS.keys())

def _h_idx(node_id):
    for i, k in enumerate(HOSPITAL_LABELS):
        if HOSPITAL_OPTIONS[k] == node_id:
            return i
    return 0


# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:0.5rem 0 1rem">
      <div style="font-family:'Syne',sans-serif;font-size:1.25rem;
                  font-weight:800;color:#f1f5f9;line-height:1.2">
        Cairo<br>Smart Transport
      </div>
      <div style="font-size:0.72rem;color:#64748b;margin-top:4px;
                  text-transform:uppercase;letter-spacing:0.1em">
        CSE112 · Alamein International University
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Network Statistics**")
    ca, cb = st.columns(2)
    ca.metric("Nodes",    GF.number_of_nodes())
    cb.metric("Roads",    GF.number_of_edges() // 2)
    ca.metric("Districts", 15)
    cb.metric("Facilities", 10)
    st.markdown("---")
    st.markdown("**Algorithm Modules**")
    
    modules = [
        "Kruskal MST", "Dijkstra", "A* Search",
        "Time-Dep. SP", "DP Scheduling", "DP Knapsack",
        "Greedy Signals", "Simulation", "ML Forecast"
    ]
    for label in modules:
        st.markdown(f'<span class="algo-badge">{label}</span>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(
        '<div style="font-size:0.72rem;color:#475569">'
        'REST API: <code>uvicorn src.backend.api:app</code><br>'
        '<a href="http://localhost:8000/docs" style="color:#38bdf8">localhost:8000/docs</a>'
        '</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <div class="hero-tag">CSE112 · Design & Analysis of Algorithms</div>
  <h1>Greater Cairo — Smart Transportation Optimizer</h1>
  <p>Graph algorithms · Dynamic programming · Greedy heuristics · ML forecasting —
     running live on the Greater Cairo metropolitan dataset.</p>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════
tabs = st.tabs([
    "Network Overview", "MST", "Routing", "Dijkstra vs A*",
    "Emergency Priority", "Simulation", "Transit DP",
    "Maintenance DP", "Signal Greedy", "ML Forecast",
])

# ──────────────────────────────────────────
# TAB 0: Network Overview
# ──────────────────────────────────────────
with tabs[0]:
    st.markdown('<div class="section-header"><h3>Greater Cairo Transportation Network</h3></div>',
                unsafe_allow_html=True)
    c1, c2 = st.columns([3,1])
    with c2:
        show_pot = st.checkbox("Show planned roads", True)
        st.markdown("---")
        st.markdown("**Districts** — sized by population")
        st.markdown("**Facilities**")
        st.markdown("─── Existing roads")
        st.markdown("╌╌╌ Planned roads")
    with c1:
        fig = map_network(GF if show_pot else G, title="")
        fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=560)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True}, key="mst_map")

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Districts & Neighborhoods**")
        st.dataframe(pd.DataFrame([
            {"ID":n,"Name":d["name"],"Type":d["type"],
             "Population":f"{d.get('pop',0):,}","Lon":d["x"],"Lat":d["y"]}
            for n,d in G.nodes(data=True) if d["kind"]=="district"
        ]), use_container_width=True, height=340, hide_index=True)
    with c2:
        st.markdown("**Key Facilities**")
        st.dataframe(pd.DataFrame([
            {"ID":n,"Name":d["name"],"Type":d["type"],"Lon":d["x"],"Lat":d["y"]}
            for n,d in G.nodes(data=True) if d["kind"]=="facility"
        ]), use_container_width=True, height=340, hide_index=True)


# ──────────────────────────────────────────
# TAB 1: MST
# ──────────────────────────────────────────
with tabs[1]:
    st.markdown('<div class="section-header"><h3>Minimum Spanning Tree — Kruskal\'s Algorithm</h3></div>',
                unsafe_allow_html=True)
    st.markdown("""<div class="info-callout">
    Edge costs: <strong>distance × (11 − condition)</strong> for existing roads and
    <strong>construction cost (M EGP)</strong> for potential roads — discounted for
    high-population districts (×0.7) and critical facilities (×0.6).
    </div>""", unsafe_allow_html=True)

    res = kruskal_mst(GF)
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Edges in MST",   res["n_edges"])
    m2.metric("Construction",   f"{res['construction_cost_MEGP']:,.0f} M EGP")
    m3.metric("Build-All Cost", f"{res['baseline_construction_MEGP']:,.0f} M EGP")
    m4.metric("Savings",     f"{res['savings_construction_MEGP']:,.0f} M EGP")

    mst_set  = {(str(u),str(v)) for u,v,_ in res["edges"]}
    mst_set |= {(v,u) for u,v in mst_set}
    fig = go.Figure([
        _edge_segments(GF, [(u,v) for u,v in GF.edges()
                            if (str(u),str(v)) not in mst_set], "#cbd5e1", 1.2, "Other roads"),
        _edge_segments(GF, [(u,v) for u,v,_ in res["edges"]], "#16a34a", 4.5, "MST edges"),
        *_node_traces(GF),
    ])
    fig.update_layout(
        mapbox=dict(style="open-street-map",center=CAIRO_CENTER,zoom=10.2),
        margin=dict(l=0,r=0,t=0,b=0), height=580,
        legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01,
                    bgcolor="rgba(255,255,255,0.9)",bordercolor="#e2e8f0",borderwidth=1))
    st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True}, key="mst_heatmap")
    st.markdown(f'<div class="complexity">O(E log E) time, O(V) space</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────
# TAB 2: Routing
# ──────────────────────────────────────────
with tabs[2]:
    st.markdown('<div class="section-header"><h3>Time-Dependent Shortest Path</h3></div>',
                unsafe_allow_html=True)
    st.markdown("""<div class="info-callout">
    <strong>Point-to-Point Routing:</strong> Select any origin and destination (District or Facility) to calculate the shortest path.
    </div>""", unsafe_allow_html=True)

    c1,c2,c3 = st.columns([2,2,1])
    src_lbl = c1.selectbox("From", NODE_LABELS, index=_idx(12), key="rt_src")
    dst_lbl = c2.selectbox("To",   NODE_LABELS, index=_idx("F1"), key="rt_dst")
    period  = c3.selectbox("Period",
                            ["morning","afternoon","evening","night"],
                            format_func=lambda p: p.title())

    src, dst = NODE_OPTIONS[src_lbl], NODE_OPTIONS[dst_lbl]
    if src == dst:
        st.warning("Please select two different nodes.")
    else:
        path, cost = ROUTER.query(src, dst, period)
        if not path:
            st.error("No reachable route between these nodes. Ensure the network is connected.")
        else:
            dist_total = sum(
                G[path[i]][path[i+1]]["distance"]
                for i in range(len(path)-1) if G.has_edge(path[i],path[i+1]))
            m1,m2,m3,m4 = st.columns(4)
            m1.metric("Travel Time", f"{cost:.1f} min")
            m2.metric("Stops", len(path))
            m3.metric("Distance", f"{dist_total:.1f} km")
            m4.metric("Cache H/M", f"{ROUTER.hits}/{ROUTER.misses}")

            fig = map_network(G, highlight_path=path, title="")
            fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=520)
            st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True}, key="routing_map")

            steps = ' <span style="color:#94a3b8">→</span> '.join(
                f'<span style="background:#eff6ff;color:#1d4ed8;padding:2px 8px;'
                f'border-radius:6px;font-weight:600;font-size:0.8rem">'
                f'{G.nodes[n]["name"]}</span>' for n in path)
            st.markdown(steps, unsafe_allow_html=True)
            st.markdown('<div class="complexity">O((V+E) log V) Dijkstra · Memoized repeated queries &lt;1 µs</div>',
                        unsafe_allow_html=True)


# ──────────────────────────────────────────
# TAB 3: Dijkstra vs A*
# ──────────────────────────────────────────
with tabs[3]:
    st.markdown('<div class="section-header"><h3>Algorithm Race — Dijkstra vs A*</h3></div>',
                unsafe_allow_html=True)
    st.markdown("""<div class="info-callout">
    A* heuristic: <strong>haversine distance / 90 km/h → minutes</strong> (admissible).
    Guarantees the same optimal cost as Dijkstra while expanding fewer nodes.
    </div>""", unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    s_lbl = c1.selectbox("From ", NODE_LABELS, index=_idx(12), key="cmp_s")
    d_lbl = c2.selectbox("To ",   NODE_LABELS, index=_idx("F1"), key="cmp_d")
    s, d = NODE_OPTIONS[s_lbl], NODE_OPTIONS[d_lbl]

    if s == d:
        st.warning("Select different nodes.")
    else:
        t0 = time.perf_counter()
        p_dij, c_dij, st_dij = dijkstra(G, s, d)
        ms_dij = (time.perf_counter()-t0)*1000

        t0 = time.perf_counter()
        p_ast, c_ast, st_ast = a_star(G, s, d)
        ms_ast = (time.perf_counter()-t0)*1000

        col1,col2 = st.columns(2)
        with col1:
            st.markdown("### Dijkstra")
            m1,m2,m3 = st.columns(3)
            m1.metric("Cost", f"{c_dij:.1f} min")
            m2.metric("Nodes", st_dij["visited"])
            m3.metric("Time",  f"{ms_dij:.2f} ms")
        with col2:
            st.markdown("### A* Search")
            m1,m2,m3 = st.columns(3)
            m1.metric("Cost", f"{c_ast:.1f} min")
            m2.metric("Nodes", st_ast["visited"])
            m3.metric("Time",  f"{ms_ast:.2f} ms")

        if st_dij["visited"] > 0:
            pct = (1 - st_ast["visited"]/st_dij["visited"])*100
            st.markdown(
                f'<div class="info-callout">A* visited <strong>{pct:.0f}% fewer nodes</strong> '
                f'({st_ast["visited"]} vs {st_dij["visited"]}) at the same optimal cost.</div>',
                unsafe_allow_html=True)

        if p_dij and p_ast:
            # Check if paths are exactly identical to prevent double plotting confusion
            if p_dij == p_ast:
                st.success("Identical Routes! As mathematically guaranteed, A* found the exact same optimal path as Dijkstra. The map below shows this shared optimal route.")
                fig = map_network(G, highlight_path=p_dij, title="")
            else:
                fig = map_network(G, highlight_path=p_dij, second_path=p_ast, title="")
                
            fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=500)
            st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True}, key="comparison_map")

            fig2 = bar_compare(
                ["Nodes Visited","Time (ms)"],
                [st_dij["visited"],ms_dij],
                [st_ast["visited"],ms_ast],
                "Dijkstra","A*","Search Effort Comparison")
            fig2.update_layout(height=300, margin=dict(l=20,r=20,t=40,b=20))
            st.plotly_chart(fig2, use_container_width=True, config={'scrollZoom': True}, key="comparison_bar")

        st.markdown('<div class="complexity">Both O((V+E) log V) worst-case · A* heuristic-pruned in practice</div>',
                    unsafe_allow_html=True)


# ──────────────────────────────────────────
# TAB 4: Emergency Fleet
# ──────────────────────────────────────────
# ──────────────────────────────────────────
# TAB 4: Emergency Fleet
# ──────────────────────────────────────────
with tabs[4]:
    st.markdown('<div class="section-header"><h3>Emergency Vehicle Priority Dispatch</h3></div>',
                unsafe_allow_html=True)
    st.markdown("""<div class="warn-callout">
    <strong>Preemption System:</strong> The vehicle routes via A* with an emergency preemption weight function (bypassing normal congestion delays). 
    <br><strong>Requirement strictly enforced:</strong> Destination is locked to <i>Medical Facilities Only</i>.
    </div>""", unsafe_allow_html=True)

    requests = []
    c1, c2, c3, c4 = st.columns([2, 3, 3, 2])
    c1.markdown(f"<div style='margin-top:2rem'><strong>Ambulance</strong></div>", unsafe_allow_html=True)
    sl = c2.selectbox("Origin", NODE_LABELS, index=_idx(12), key="e_src_0")
    dl = c3.selectbox("Destination (Hospitals Only)", HOSPITAL_LABELS, index=_h_idx("F9"), key="e_dst_0")
    
    period_e = c4.selectbox("Traffic Period",
                             ["morning","afternoon","evening","night"],
                             format_func=lambda p: p.title(),
                             key="e_period")

    requests.append({"id": "Ambulance", "src": NODE_OPTIONS[sl], "dst": HOSPITAL_OPTIONS[dl]})

    if any(r["src"]==r["dst"] for r in requests):
        st.warning("Vehicle needs different start and end nodes.")
    else:
        out = emergency_priority(G, requests, period_e)
        rows = []
        for r in out:
            rows.append({
                "Vehicle": r["id"],
                "Route 1 ETA": "Infinity" if r["eta1"] is None or r["eta1"]==float("inf") else f"{r['eta1']:.1f} min",
                "Route 2 ETA": "Infinity" if r["eta2"] is None or r["eta2"]==float("inf") else f"{r['eta2']:.1f} min",
                "Route 3 ETA": "Infinity" if r["eta3"] is None or r["eta3"]==float("inf") else f"{r['eta3']:.1f} min",
                "Available Routes": r["num_routes"],
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        valid = [r for r in out if r["path1"] and r["eta1"]!=float("inf")]
        if valid:
            r = valid[0] 
            fig = map_network(G, highlight_path=r["path1"], second_path=r["path2"], third_path=r["path3"], title="")
            fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=520)
            st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True}, key="emergency_map")
            st.markdown(f'<div class="info-callout">Mapped up to 3 alternate edge-disjoint routes for <strong>{r["id"]}</strong>. <br> <span style="color:#dc2626">■ Route 1</span> | <span style="color:#16a34a">■ Route 2</span> | <span style="color:#f59e0b">■ Route 3</span></div>',
                        unsafe_allow_html=True)
        st.markdown('<div class="complexity">O((V+E) log V) · Finds up to 3 edge-disjoint paths evaluated via A* preemption</div>',
                    unsafe_allow_html=True)
# ──────────────────────────────────────────
# TAB 5: Simulation
# ──────────────────────────────────────────
with tabs[5]:
    st.markdown('<div class="section-header"><h3>Citywide Traffic Simulation</h3></div>',
                unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns([1.2,1.2,1.2,1])
    period_s = c1.selectbox("Period ",
                             ["morning","afternoon","evening","night"],
                             format_func=lambda p: p.title(),
                             key="sim_p")
    accident = c2.checkbox("Accident: Giza - Helwan")
    closure  = c3.checkbox("Close: Downtown - Heliopolis")
    severity = c4.slider("Severity Multiplier", 2, 10, 5)

    H = G
    if accident: H = scenario_accident(H, (8,12), severity=severity)
    if closure:  H = scenario_road_closure(H, [(3,5)])

    res = simulate_period(H, DS["transit_demand"], period_s)

    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Served",   f"{res['served']:,}")
    m2.metric("Unreachable", f"{res['unreachable']:,}")
    m3.metric("Avg Min/Pax", f"{res['avg_minutes_per_pax']:.1f}")
    m4.metric("Loaded Edges", len(res["edge_load"]))

    fig = map_heatmap(H, res["edge_load"],
                      title=f"Traffic heatmap — {period_s.title()}")
    fig.update_layout(margin=dict(l=0,r=0,t=30,b=0), height=560)
    st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True}, key="simulation_map")

    fig2 = go.Figure([go.Bar(
        x=["Served","Unreachable"],
        y=[res["served"],res["unreachable"]],
        marker_color=["#22c55e","#ef4444"],
        text=[f"{res['served']:,}",f"{res['unreachable']:,}"],
        textposition="outside")])
    fig2.update_layout(title="Demand Fulfillment", height=280,
                       margin=dict(l=20,r=20,t=40,b=20),
                       yaxis_title="Daily passengers")
    st.plotly_chart(fig2, use_container_width=True, config={'scrollZoom': True}, key="simulation_bar")
    st.markdown('<div class="complexity">O(D × (V+E) log V) — D = demand pairs</div>',
                unsafe_allow_html=True)


# ──────────────────────────────────────────
# TAB 6: Transit DP & Routing
# ──────────────────────────────────────────
# ──────────────────────────────────────────
# TAB 6: Transit DP & Routing
# ──────────────────────────────────────────
# ──────────────────────────────────────────
# TAB 6: Transit DP & Routing
# ──────────────────────────────────────────
with tabs[6]:
    # ... (الجزء الأول الخاص بـ Fleet Allocation يظل كما هو) ...

    # ---------------------------------------------------------
    # الميزة المحدثة: Point-to-Point Transit Planner (مسار متصل وملون)
    # ---------------------------------------------------------
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header"><h3>Point-to-Point Transit Planner</h3></div>', unsafe_allow_html=True)
    
    transit_mode = st.radio("Select Transit Mode", 
                            ["Integrated (Bus + Metro)", "Bus Only", "Metro Only"], 
                            horizontal=True)

    # 1. بناء شبكة النقل المختارة
    Gt = nx.DiGraph()
    if transit_mode in ["Integrated (Bus + Metro)", "Metro Only"]:
        for mid, mname, stops, pax in DS["metro_lines"]:
            for i in range(len(stops)-1):
                u, v = stops[i], stops[i+1]
                # حفظ بيانات الخط والوسيلة داخل الـ Edge
                Gt.add_edge(u, v, mode="Metro", line=mid, name=mname)
                Gt.add_edge(v, u, mode="Metro", line=mid, name=mname)

    if transit_mode in ["Integrated (Bus + Metro)", "Bus Only"]:
        for rid, stops, buses, pax in DS["bus_routes"]:
            for i in range(len(stops)-1):
                u, v = stops[i], stops[i+1]
                Gt.add_edge(u, v, mode="Bus", line=rid, name=f"Route {rid}")
                Gt.add_edge(v, u, mode="Bus", line=rid, name=f"Route {rid}")

    transit_nodes = set(Gt.nodes())
    if not transit_nodes:
        st.warning(f"No routes available for {transit_mode}.")
    else:
        T_LABELS = [lbl for lbl in NODE_LABELS if NODE_OPTIONS[lbl] in transit_nodes]
        c1, c2 = st.columns(2)
        t_src_lbl = c1.selectbox("Transit Origin", T_LABELS, index=0, key="t_src")
        t_dst_lbl = c2.selectbox("Transit Destination", T_LABELS, index=min(1, len(T_LABELS)-1), key="t_dst")
        
        t_src, t_dst = NODE_OPTIONS[t_src_lbl], NODE_OPTIONS[t_dst_lbl]

        if t_src == t_dst:
            st.warning("Please select different points.")
        else:
            try:
                # حساب أقصر مسار في شبكة النقل (أقل عدد محطات)
                t_path = nx.shortest_path(Gt, t_src, t_dst)
                
                # مصفوفة لتجميع "قطع" المسار للرسم
                path_traces = []
                instructions = []
                
                # متغيرات لتتبع تغير الخطوط
                current_line = None
                start_node = t_path[0]
                prev_mode = None

                for i in range(len(t_path)-1):
                    u, v = t_path[i], t_path[i+1]
                    edge_data = Gt[u][v]
                    mode = edge_data["mode"]
                    line_name = edge_data["name"]
                    
                    # تحديد اللون: أزرق للمترو، أخضر للباص
                    color = "#1d4ed8" if mode == "Metro" else "#16a34a"
                    
                    # إضافة الوصلة الحالية لمجموعة الرسم (لضمان الاتصال الجغرافي)
                    path_traces.append(_edge_segments(G, [(u, v)], color, 6, f"{mode}: {line_name}"))
                    
                    # تجميع التعليمات المكتوبة
                    if line_name != current_line:
                        if current_line is not None:
                            instructions.append({"mode": prev_mode, "line": current_line, "from": start_node, "to": u})
                        current_line = line_name
                        prev_mode = mode
                        start_node = u
                
                # إضافة آخر خطوة
                instructions.append({"mode": prev_mode, "line": current_line, "from": start_node, "to": t_path[-1]})

                st.markdown(f"#### Trip Directions ({transit_mode})")
                
                # عرض كروت الاتجاهات
                for step in instructions:
                    f_name = G.nodes[step['from']]['name']
                    t_name = G.nodes[step['to']]['name']
                    icon = "🚇" if step['mode'] == 'Metro' else "🚌"
                    st.info(f"{icon} **{step['mode']} ({step['line']})**: Board at **{f_name}** and get off at **{t_name}**")

                # رسم المسار الكامل المتصل والملون
                # ندمج كل الـ traces مع بعضها في خريطة واحدة
                fig_transit = go.Figure(data=path_traces + _node_traces(G))
                fig_transit.update_layout(
                    mapbox=dict(style="open-street-map", center=CAIRO_CENTER, zoom=10.5),
                    margin=dict(l=0, r=0, t=40, b=0), height=550,
                    showlegend=True,
                    legend=dict(bgcolor="rgba(255,255,255,0.8)", yanchor="top", y=0.99, xanchor="left", x=0.01)
                )
                st.plotly_chart(fig_transit, use_container_width=True, key="connected_transit_map")
                
            except nx.NetworkXNoPath:
                st.error("No integrated transit route found.")


# ──────────────────────────────────────────
# TAB 7: Maintenance DP
# ──────────────────────────────────────────
with tabs[7]:
    st.markdown('<div class="section-header"><h3>Road Maintenance — 0/1 Knapsack DP</h3></div>',
                unsafe_allow_html=True)
    st.markdown("""<div class="info-callout">
    <strong>Goal:</strong> maximise population benefit under budget.
    Cost = distance × (11 − condition) × 4 M EGP. Only roads with condition ≤ 7 are candidates.
    </div>""", unsafe_allow_html=True)

    budget = st.slider("Budget (M EGP)", 100, 2000, 800, 50)

    seen, candidates = set(), []
    for u,v,dd in G.edges(data=True):
        k = tuple(sorted([str(u),str(v)]))
        if k in seen or dd["kind"]!="existing": continue
        seen.add(k)
        if dd["condition"]>7: continue
        cost = dd["distance"]*(11-dd["condition"])*4
        benefit = (G.nodes[u].get("pop",50000)+G.nodes[v].get("pop",50000))/1000
        candidates.append({"id":f"{u}-{v}",
                            "from":G.nodes[u]["name"],"to":G.nodes[v]["name"],
                            "cost_MEGP":round(cost,1),"benefit":round(benefit,1),
                            "condition":dd["condition"]})

    out = road_maintenance_allocation(
        [{"id":c["id"],"cost_MEGP":c["cost_MEGP"],"benefit":c["benefit"]}
         for c in candidates], budget)

    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Roads Selected", len(out["selected"]))
    m2.metric("Total Spent",     f"{out['spent_MEGP']:,.0f} M EGP")
    m3.metric("Remaining", f"{budget-out['spent_MEGP']:,.0f} M EGP")
    m4.metric("Benefit Score",   f"{out['total_benefit']:.0f}")

    df_c = pd.DataFrame(candidates)
    df_c["Selected"] = df_c["id"].isin(out["selected"])
    df_show = df_c[["from","to","condition","cost_MEGP","benefit","Selected"]]
    df_show.columns = ["From","To","Condition","Cost (M EGP)","Benefit","Selected"]
    st.dataframe(df_show, use_container_width=True, hide_index=True)

    # Map
    sel_edges = []
    for sel_id in out["selected"]:
        parts = sel_id.split("-",1)
        if len(parts)==2:
            u_s,v_s = parts
            u = int(u_s) if u_s.isdigit() else u_s
            v = int(v_s) if v_s.isdigit() else v_s
            if G.has_edge(u,v): sel_edges.append((u,v))
            elif G.has_edge(v,u): sel_edges.append((v,u))

    other = [(u,v) for u,v in G.edges()
             if (u,v) not in sel_edges and (v,u) not in sel_edges]
    fig = go.Figure([
        _edge_segments(G, other, "#e2e8f0", 1, "Other roads"),
        _edge_segments(G, sel_edges, "#dc2626", 5, "Selected for repair"),
        *_node_traces(G),
    ])
    fig.update_layout(
        mapbox=dict(style="open-street-map",center=CAIRO_CENTER,zoom=10.2),
        margin=dict(l=0,r=0,t=0,b=0), height=520,
        legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01,
                    bgcolor="rgba(255,255,255,0.9)"))
    st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True}, key="maintenance_map")
    st.markdown('<div class="complexity">O(N × Budget) time and space</div>',
                unsafe_allow_html=True)


# ──────────────────────────────────────────
# TAB 8: Signal Greedy
# ──────────────────────────────────────────
with tabs[8]:
    st.markdown('<div class="section-header"><h3>Greedy Traffic Signal Timing</h3></div>',
                unsafe_allow_html=True)
    st.markdown("""<div class="info-callout">
    Green time proportional to incoming vehicle counts with a per-direction floor.
    Compared to Webster's formula. Suboptimal (≥10% worse) when saturation flows
    differ sharply between approaches.
    </div>""", unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    v_n = c1.number_input("North (vph)", 0, 5000, 1500)
    v_s = c2.number_input("South (vph)", 0, 5000, 1300)
    v_e = c3.number_input("East (vph)",  0, 5000,  900)
    v_w = c4.number_input("West (vph)",  0, 5000, 1100)

    sig = traffic_signal_optimization({"N":v_n,"S":v_s,"E":v_e,"W":v_w})

    df_sig = pd.DataFrame({
        "Direction":     ["North","South","East","West"],
        "Input vph":     [v_n,v_s,v_e,v_w],
        "Greedy (s)":    list(sig["greedy_plan_seconds"].values()),
        "Webster (s)":   list(sig["webster_reference"].values()),
        "Diff vs Webster":  [sig["greedy_plan_seconds"][k]-sig["webster_reference"][k]
                          for k in ["N","S","E","W"]],
    })
    st.dataframe(df_sig, use_container_width=True, hide_index=True)

    fig = go.Figure()
    fig.add_bar(x=["North","South","East","West"],
                y=list(sig["greedy_plan_seconds"].values()),
                name="Greedy",marker_color="#0ea5e9",
                text=list(sig["greedy_plan_seconds"].values()),textposition="outside")
    fig.add_bar(x=["North","South","East","West"],
                y=list(sig["webster_reference"].values()),
                name="Webster ref",marker_color="#f59e0b",
                text=list(sig["webster_reference"].values()),textposition="outside")
    fig.update_layout(
        title=f"Signal Plan — {sig['cycle_seconds']}s cycle",
        barmode="group", height=360,
        margin=dict(l=20,r=20,t=50,b=20),
        yaxis_title="Green time (seconds)",
        legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
    st.plotly_chart(fig, use_container_width=True, key="signal_bar")

    max_diff = max(abs(sig["greedy_plan_seconds"][d]-sig["webster_reference"][d])
                   for d in ["N","S","E","W"])
    if max_diff<=4:
        st.markdown('<div class="info-callout"><strong>Greedy is near-optimal</strong> for this flow distribution (within 5% of Webster).</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="warn-callout"><strong>Greedy is suboptimal</strong> — uneven saturation flows cause up to {max_diff}s deviation vs Webster.</div>',
                    unsafe_allow_html=True)

    st.markdown('<div class="complexity">O(K log K) — K = number of approaches</div>',
                unsafe_allow_html=True)


# ──────────────────────────────────────────
# TAB 9: ML Forecast
# ──────────────────────────────────────────
with tabs[9]:
    st.markdown('<div class="section-header"><h3>Congestion Forecast — RandomForest (scikit-learn)</h3></div>',
                unsafe_allow_html=True)
    st.markdown("""<div class="info-callout">
    Trained on synthetic-expanded per-edge per-period data (6 noisy samples per edge×period).
    Features: hour, period (one-hot), distance, capacity, condition. Target: vehicles/hour.
    </div>""", unsafe_allow_html=True)

    if "ml_model" not in st.session_state:
        st.markdown("**Model not yet trained.** Click below to train on the Cairo dataset.")
        if st.button("Train RandomForest Model", type="primary"):
            from src.ml.congestion import train_model
            with st.spinner("Training on synthetic-expanded traffic data…"):
                model, metrics = train_model()
            st.session_state["ml_model"]   = model
            st.session_state["ml_metrics"] = metrics
            st.rerun()
    else:
        m = st.session_state["ml_metrics"]
        c1,c2,c3 = st.columns(3)
        c1.metric("Model MAE", f"{m['mae_vph']:.1f} vph")
        c2.metric("Train Samples", f"{m['n_train']:,}")
        c3.metric("Test Samples",  f"{m['n_test']:,}")

        from src.ml.congestion import predict_congestion

        edges_avail = [(u,v) for u,v in G.edges()
                       if u!=v and G[u][v]["kind"]=="existing"][:40]
        edge_labels = [f"{G.nodes[u]['name']} → {G.nodes[v]['name']}"
                       for u,v in edges_avail]

        c1,c2 = st.columns([3,1])
        edge_sel = c1.selectbox("Road segment", edge_labels)
        hour = c2.slider("Hour", 0, 23, 8)

        idx_e = edge_labels.index(edge_sel)
        eu,ev = edges_avail[idx_e]
        pred = predict_congestion(st.session_state["ml_model"], G[eu][ev], hour)
        cap  = G[eu][ev]["capacity"]
        ratio = pred/cap

        m1,m2,m3 = st.columns(3)
        m1.metric("Predicted vph", f"{pred:,.0f}")
        m2.metric("Capacity", f"{cap:,}")
        m3.metric("Utilization", f"{ratio*100:.1f}%")

        level = ("Heavy congestion" if ratio>0.9
                 else "Moderate congestion" if ratio>0.7
                 else "Free flow")
        color_c = "#fef2f2" if ratio>0.9 else "#fffbeb" if ratio>0.7 else "#f0fdf4"
        st.markdown(
            f'<div style="background:{color_c};border-radius:10px;padding:10px 14px;'
            f'font-weight:600;font-size:0.9rem;margin:0.5rem 0">{level} '
            f'({pred:,.0f} / {cap:,} capacity)</div>', unsafe_allow_html=True)

        # 24-hour forecast
        st.markdown("**24-hour forecast for selected road:**")
        preds_24 = [predict_congestion(st.session_state["ml_model"], G[eu][ev], h)
                    for h in range(24)]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(24)), y=preds_24,
            mode="lines+markers", name="Predicted vph",
            line=dict(color="#0ea5e9",width=3),
            fill="tozeroy", fillcolor="rgba(14,165,233,0.1)"))
        fig.add_trace(go.Scatter(
            x=list(range(24)), y=[cap]*24,
            mode="lines", name="Capacity limit",
            line=dict(color="#ef4444",width=2,dash="dash")))
        fig.add_vline(x=hour, line_dash="dot", line_color="#f59e0b",
                      annotation_text=f"  {hour}:00",
                      annotation_position="top right")
        fig.update_layout(height=300, margin=dict(l=20,r=20,t=30,b=20),
                          xaxis_title="Hour", yaxis_title="vph",
                          legend=dict(orientation="h",yanchor="bottom",y=1.02))
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True}, key="ml_line_chart")

        # Map highlight
        other_e = [(u,v) for u,v in G.edges()
                   if (u,v)!=(eu,ev) and (u,v)!=(ev,eu)]
        fig2 = go.Figure([
            _edge_segments(G, other_e, "#e2e8f0", 1, "Other roads"),
            _edge_segments(G, [(eu,ev)], "#dc2626", 5, f"{pred:,.0f} vph predicted"),
            *_node_traces(G),
        ])
        fig2.update_layout(
            mapbox=dict(style="open-street-map",center=CAIRO_CENTER,zoom=10.5),
            margin=dict(l=0,r=0,t=0,b=0), height=380,
            legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01,
                        bgcolor="rgba(255,255,255,0.9)"))
        st.plotly_chart(fig2, use_container_width=True, config={'scrollZoom': True}, key="ml_map")

        if st.button("Reset model"):
            del st.session_state["ml_model"], st.session_state["ml_metrics"]
            st.rerun()

        st.markdown('<div class="complexity">Training: O(T × N log N) · Inference: O(T × depth)</div>',
                    unsafe_allow_html=True)