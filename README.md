Greater Cairo Smart Transportation Optimizer

Overview

The Greater Cairo Smart Transportation Optimizer is an advanced transportation optimization and simulation system developed as part of the Design and Analysis of Algorithms (CSE112) course at Alamein International University.

The project focuses on solving real-world transportation challenges in Greater Cairo, one of the world’s most densely populated metropolitan areas, by applying advanced algorithmic techniques including:

Minimum Spanning Tree (MST)
Shortest Path Algorithms
Dynamic Programming
Greedy Algorithms
Traffic Simulation
Machine Learning Congestion Forecasting

The system models Cairo’s transportation infrastructure as a weighted graph and provides optimized routing, congestion-aware navigation, emergency dispatching, public transportation scheduling, and infrastructure planning solutions.

Problem Statement

Greater Cairo experiences severe transportation congestion caused by:

Rapid urban population growth
High traffic density
Dynamic road conditions
Inefficient route planning
Delayed emergency response
Public transportation scheduling inefficiencies

Traditional static transportation systems fail to adapt to rapidly changing traffic conditions throughout the day. This project introduces an intelligent transportation optimization framework capable of dynamic routing, congestion forecasting, emergency optimization, and transportation infrastructure analysis.

Objectives

The project aims to:

Model Cairo as a weighted transportation graph
Optimize shortest path routing
Reduce congestion impact
Improve emergency vehicle dispatching
Optimize public transportation scheduling
Forecast traffic congestion using Machine Learning
Simulate transportation scenarios
Compare algorithmic performance in real-world use cases
Technologies & Tools

The system was implemented using:

Technology	Purpose
Python 3.11	Core programming language
Streamlit	Interactive web application
NetworkX	Graph modeling
Plotly	Visualization & maps
Scikit-learn	Machine learning
FastAPI	API integration
Heapq	Priority queue optimization

Core Features
Transportation Network Modeling
Road network represented as weighted graphs
Nodes represent intersections, districts, and facilities
Edges represent roads and transportation routes
Traffic Flow Optimization
Congestion-aware route planning
Dynamic traffic simulation
Time-dependent routing
Emergency Routing System
Emergency vehicle prioritization
Alternative route generation
Traffic-free emergency dispatch simulation
Public Transportation Optimization
Bus allocation optimization
Vehicle scheduling using Dynamic Programming
Route efficiency analysis
Infrastructure Planning
Minimum-cost road network generation
Maintenance budget optimization
Future road investment analysis
Machine Learning Congestion Forecasting
Random Forest regression model
Traffic prediction
Congestion estimation
Visualization System
Interactive maps
Traffic heatmaps
Route visualization
Congestion analysis dashboards

System Architecture

The system is divided into six major layers:

┌─────────────────────────────┐
│      Frontend Layer         │
│       Streamlit UI          │
└────────────┬────────────────┘
             │
┌────────────▼────────────────┐
│     Visualization Layer     │
│    Plotly + Mapbox Maps     │
└────────────┬────────────────┘
             │
┌────────────▼────────────────┐
│      Algorithm Engine       │
│ MST | Dijkstra | A* | DP    │
└────────────┬────────────────┘
             │
┌────────────▼────────────────┐
│      Simulation Engine      │
│ Traffic & Scenario Testing  │
└────────────┬────────────────┘
             │
┌────────────▼────────────────┐
│   Machine Learning Layer    │
│  Random Forest Prediction   │
└────────────┬────────────────┘
             │
┌────────────▼────────────────┐
│         Data Layer          │
│ Graph Construction & Data   │
└─────────────────────────────┘

Project Structure
project_root/
│
├── data/
│   └── loader.py
│
├── algorithms/
│   ├── mst.py
│   ├── shortest_path.py
│   ├── dynamic_programming.py
│   ├── greedy.py
│   └── congestion.py
│
├── simulation/
│   └── engine.py
│
├── app.py
│
└── requirements.txt

Implemented Algorithms
1. Kruskal’s Minimum Spanning Tree (MST)
Purpose

Used to determine the minimum-cost transportation infrastructure network connecting all major locations in Cairo.

Key Concepts
Greedy Algorithm
Union-Find (Disjoint Set Union)
Cycle Detection
Infrastructure Cost Minimization
Complexity
Time Complexity: O(E log E)
Space Complexity: O(V)
Transportation Usage
Road network planning
Infrastructure optimization
Maintenance cost reduction
2. Prim’s Minimum Spanning Tree
Purpose

Alternative MST generation optimized for dense graphs.

Features
Priority Queue based
Incremental graph expansion
Efficient dense-network optimization
Complexity
Time Complexity: O(E log V)
3. Dijkstra’s Shortest Path Algorithm
Purpose

Finds the shortest travel route between locations.

Features
Weighted graph routing
Traffic-aware path computation
GPS-style navigation
Transportation Modifications
Congestion penalties
Road closure handling
Emergency prioritization
Complexity
O((V + E) log V)

4. A* Search Algorithm
Purpose

Optimized emergency routing.

Features
Heuristic-based search
Faster than standard Dijkstra
Reduced node exploration
Heuristic Used
Haversine distance
Geographic shortest estimation
Performance

A* visits approximately 30–45% fewer nodes than Dijkstra in long-distance routing scenarios.

5. Dynamic Programming — Transit Scheduling
Purpose

Optimally allocates buses across transportation routes.

DP State
dp[i][b]

Where:

i = route index
b = available buses
Benefits
Maximizes served passengers
Efficient fleet utilization
6. Dynamic Programming — 0/1 Knapsack
Purpose

Road maintenance budget optimization.

Objective

Select the best combination of road repair projects within a limited maintenance budget.

Complexity
O(N × Budget)
7. Greedy Traffic Signal Optimization
Purpose

Optimize traffic light timing dynamically.

Features
Congestion-aware signal allocation
Real-time green-light distribution
Throughput maximization
8. Random Forest Congestion Forecasting
Purpose

Predict future traffic congestion.

ML Features
Hour of day
Road capacity
Distance
Traffic period
Road condition
Evaluation
MAE ≈ 72–95 vehicles/hour

Dataset & Graph Modeling
Graph Representation
Vertices → Intersections / Districts
Edges → Roads
Weights → Travel Time / Congestion Cost
Network Details
25 Nodes
30+ Existing Roads
15 Potential Roads
Time-dependent traffic data
Time Periods
Morning
Afternoon
Evening
Night
Edge Weight Formula
utilization = traffic_vph / capacity
congestion_factor = 1 + 4 * utilization^3
speed_factor = condition / 10

travel_time = base_time * congestion_factor / speed_factor

This formula simulates realistic congestion growth under high traffic utilization.

Simulation Engine

The simulation system models:

Daily transportation demand
Traffic congestion
Road closures
Accidents
Passenger movement
Emergency routing
Supported Scenarios
Road closure simulation
Accident congestion simulation
Emergency dispatch testing
User Interface

The system provides a multi-tab Streamlit application containing:

Tab	Function
Network Overview	Full transportation graph
Route Planner	Dijkstra & A* routing
Emergency Dispatch	Alternative emergency routes
Transit Optimizer	Bus scheduling & DP
Traffic Simulation	Congestion simulation
Congestion Forecast	ML predictions

Performance Evaluation
Algorithm	Runtime
Dijkstra	0.8 ms
A* Search	0.5 ms
Kruskal MST	1.2 ms
DP Transit	3.5 ms
RF Training	1.2 sec

Challenges Faced
Major Challenges
Dynamic traffic conditions
Large graph processing
Real-time updates
DP memory optimization
ML underfitting
Simulation complexity
Solutions
Priority queue optimization
Caching with Streamlit
Graph pruning
Noise-based dataset augmentation
Efficient adjacency lists

Future Improvements
Real-time GPS integration
AI traffic prediction
Smart traffic signals
Reinforcement Learning routing
IoT traffic sensors
Cloud deployment
Graph Neural Networks
Multi-modal trip planning

Results & Impact

The system successfully demonstrated:

Improved route optimization
Faster emergency response routing
Reduced congestion impact
Efficient transportation scheduling
Realistic traffic simulation
Intelligent infrastructure planning

The project proves how advanced algorithmic techniques can significantly improve smart city transportation systems.

Team Members
Menna Allah Osama
Catherine Adel Zaki
Soha Hossam
Arwa Mohey
Samira Saed
Mariam Nady
Veronica Wassim

Installation
Clone Repository
git clone <repository-url>
cd smart-city-transportation-optimizer
Install Dependencies
pip install -r requirements.txt
Run Application
streamlit run app.py
Example Use Cases
Route Planning

Find the fastest route between Cairo districts considering real-time congestion.

Emergency Dispatch

Generate alternative ambulance routes during heavy traffic.

Transit Optimization

Allocate buses efficiently across transportation routes.

Infrastructure Planning

Identify the minimum-cost road network expansion strategy.

Educational Value

This project demonstrates practical applications of:

Graph Theory
Algorithm Design
Dynamic Programming
Greedy Algorithms
Machine Learning
Transportation Engineering
Simulation Systems
License

This project was developed for educational and academic purposes under the Faculty of Computer Science & Engineering at Alamein International University.
