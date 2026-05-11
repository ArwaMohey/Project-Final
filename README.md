# Greater Cairo Smart Transportation Optimizer

<div align="center">

# 🚦 Greater Cairo Smart Transportation Optimizer

### AI-Powered Smart City Transportation Network Optimization System

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge\&logo=python)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red?style=for-the-badge\&logo=streamlit)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Random%20Forest-orange?style=for-the-badge)
![Algorithms](https://img.shields.io/badge/Algorithms-Graph%20Optimization-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)
![Course](https://img.shields.io/badge/Course-CSE112-purple?style=for-the-badge)

</div>

---

# 📌 Overview

The **Greater Cairo Smart Transportation Optimizer** is a comprehensive smart-city transportation optimization system developed for the **Design and Analysis of Algorithms (CSE112)** course at **Alamein International University**.

The system addresses real transportation challenges in **Greater Cairo**, one of the most densely populated metropolitan regions in the world, by integrating advanced algorithmic techniques, traffic simulation, machine learning, graph theory, and intelligent route optimization.

The project transforms Cairo’s transportation infrastructure into a dynamic weighted graph and applies optimization algorithms to:

* Reduce congestion
* Improve emergency response routing
* Optimize transportation scheduling
* Predict traffic congestion
* Simulate transportation scenarios
* Improve infrastructure planning

---

# 🌍 Real-World Motivation

Greater Cairo suffers from:

* Severe traffic congestion
* Long commute times
* Emergency vehicle delays
* Inefficient transportation scheduling
* Rapid urban expansion
* Dynamic traffic conditions throughout the day

Traditional static transportation systems cannot effectively adapt to changing traffic patterns.

This project introduces a smart transportation optimization framework capable of dynamic routing, intelligent scheduling, congestion-aware navigation, and AI-based traffic prediction.

---

# 🎯 Project Objectives

The main goals of the project are:

✅ Model Cairo as a weighted transportation graph
✅ Implement graph optimization algorithms
✅ Optimize shortest path routing
✅ Improve emergency dispatch systems
✅ Simulate traffic congestion scenarios
✅ Optimize public transportation scheduling
✅ Forecast traffic congestion using Machine Learning
✅ Build an interactive visualization dashboard

---

# 🧠 Core Algorithms Implemented

| Algorithm           | Purpose                              | Complexity     |
| ------------------- | ------------------------------------ | -------------- |
| Kruskal’s MST       | Infrastructure optimization          | O(E log E)     |
| Prim’s MST          | Dense graph optimization             | O(E log V)     |
| Dijkstra            | Shortest path routing                | O((V+E) log V) |
| A* Search           | Emergency routing optimization       | O((V+E) log V) |
| Dynamic Programming | Bus scheduling & resource allocation | O(N×W)         |
| 0/1 Knapsack        | Road maintenance optimization        | O(N×Budget)    |
| Greedy Algorithms   | Traffic signal optimization          | O(n log n)     |
| Random Forest       | Congestion forecasting               | ML-based       |

---

# 🚀 Key Features

## 🚗 Intelligent Route Optimization

* Shortest-path route generation
* Traffic-aware navigation
* Congestion-aware routing
* Real-time path optimization

## 🚑 Emergency Dispatch System

* Emergency vehicle prioritization
* Alternative route generation
* Fast emergency response optimization
* Edge-disjoint backup routes

## 🚌 Public Transportation Optimization

* Bus fleet scheduling
* Passenger demand optimization
* Dynamic Programming allocation
* Transit efficiency analysis

## 🌡 Traffic Simulation Engine

* Full-day traffic simulation
* Road closure scenarios
* Accident congestion simulation
* Edge load accumulation

## 📊 Machine Learning Congestion Forecasting

* Random Forest regression model
* Traffic volume prediction
* Congestion estimation
* Traffic trend analysis

## 🗺 Interactive Visualization System

* Interactive transportation maps
* Traffic heatmaps
* Route visualization
* Congestion dashboards
* Simulation analysis charts

---

# 🏗 System Architecture

```text
┌─────────────────────────────┐
│       Frontend Layer        │
│        Streamlit UI         │
└────────────┬────────────────┘
             │
┌────────────▼────────────────┐
│     Visualization Layer     │
│     Plotly + Mapbox Maps    │
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
```

---

# ⚙️ Technologies & Tools

| Technology   | Purpose                     |
| ------------ | --------------------------- |
| Python 3.11  | Core development            |
| Streamlit    | Interactive frontend        |
| NetworkX     | Graph modeling              |
| Plotly       | Interactive visualization   |
| Scikit-learn | Machine Learning            |
| FastAPI      | Backend/API support         |
| Heapq        | Priority queue optimization |
| Pandas       | Data processing             |
| NumPy        | Numerical computations      |

---

# 📂 Project Structure

```text
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
├── requirements.txt
│
└── README.md
```

---

# 📈 Transportation Network Modeling

The transportation network is represented as a weighted directed graph:

| Graph Component  | Transportation Meaning        |
| ---------------- | ----------------------------- |
| Vertices         | Intersections / Districts     |
| Edges            | Roads                         |
| Edge Weights     | Travel Time / Congestion Cost |
| Source Node      | Starting Location             |
| Destination Node | Target Location               |

## Network Details

* 25 Nodes
* 30+ Existing Roads
* 15 Potential Roads
* Multiple traffic periods
* Dynamic congestion-aware edge weights

---

# ⏰ Time-Dependent Traffic Modeling

The system supports four dynamic traffic periods:

| Period    | Description              |
| --------- | ------------------------ |
| Morning   | Rush Hour (6 AM – 10 AM) |
| Afternoon | Midday Traffic           |
| Evening   | Evening Rush Hour        |
| Night     | Low Traffic Period       |

This enables realistic transportation simulation and time-aware route optimization.

---

# 📐 Edge Weight Formula

The routing engine uses a congestion-aware travel-time formula:

```python
utilization = traffic_vph / capacity
congestion_factor = 1 + 4 * utilization^3
speed_factor = condition / 10

travel_time = base_time * congestion_factor / speed_factor
```

### Formula Advantages

✅ Realistic congestion growth
✅ Dynamic traffic penalties
✅ Road condition awareness
✅ Transportation engineering inspired model

---

# 🔍 Algorithm Details

---

# 1️⃣ Kruskal’s Minimum Spanning Tree

## Purpose

Used to determine the minimum-cost transportation infrastructure network connecting all major Cairo districts.

## Key Concepts

* Greedy Algorithm
* Disjoint Set Union (DSU)
* Cycle Detection
* Infrastructure Cost Optimization

## Transportation Applications

* Road infrastructure planning
* Network connectivity optimization
* Maintenance cost reduction
* Smart-city road expansion planning

---

# 2️⃣ Prim’s Algorithm

## Purpose

Alternative MST algorithm optimized for dense transportation networks.

## Features

* Priority Queue optimization
* Incremental graph expansion
* Efficient dense-network processing

---

# 3️⃣ Dijkstra’s Algorithm

## Purpose

Computes the shortest travel route between two locations.

## Features

* Weighted graph shortest path
* Traffic-aware routing
* GPS-style navigation
* Congestion-aware optimization

## Transportation Modifications

* Rush-hour penalties
* Road closure handling
* Alternative route generation
* Emergency prioritization

## Complexity

```text
O((V + E) log V)
```

---

# 4️⃣ A* Search Algorithm

## Purpose

Optimized emergency routing.

## Advantages Over Dijkstra

| Dijkstra                | A*                          |
| ----------------------- | --------------------------- |
| Explores many nodes     | Uses heuristic guidance     |
| Slower for large graphs | Faster goal-directed search |
| No heuristic            | Haversine heuristic         |

## Heuristic Used

The system uses the **Haversine Distance** heuristic to estimate remaining travel time.

### Benefits

✅ Faster emergency response
✅ Reduced node exploration
✅ Improved routing efficiency

---

# 5️⃣ Dynamic Programming — Transit Scheduling

## Purpose

Optimally allocates buses across transportation routes.

## Objective

Maximize passengers served while respecting fleet limits.

## Applications

* Bus scheduling
* Fleet optimization
* Passenger demand allocation
* Transportation resource management

---

# 6️⃣ Dynamic Programming — 0/1 Knapsack

## Purpose

Optimize road maintenance projects under limited budgets.

## Objective

Select the most beneficial road repair projects while staying within budget.

## Applications

* Smart-city maintenance planning
* Infrastructure investment optimization
* Budget allocation systems

---

# 7️⃣ Greedy Traffic Signal Optimization

## Purpose

Optimize traffic signal timing dynamically.

## Features

* Flow-based green time allocation
* Congestion reduction
* Throughput maximization
* Real-time signal optimization

---

# 8️⃣ Machine Learning Congestion Forecasting

## Model Used

Random Forest Regressor

## Features Used

* Traffic period
* Hour of day
* Road capacity
* Road condition
* Distance

## Expected Results

```text
MAE ≈ 72–95 vehicles/hour
```

## Benefits

✅ Congestion prediction
✅ Traffic forecasting
✅ Improved route planning
✅ Better transportation analysis

---

# 🧪 Traffic Simulation Engine

The simulation engine models:

* Daily transportation demand
* Passenger movement
* Congestion accumulation
* Road closures
* Accidents
* Emergency dispatching

## Supported Scenarios

| Scenario            | Description                   |
| ------------------- | ----------------------------- |
| Road Closure        | Simulates blocked roads       |
| Accident Scenario   | Simulates heavy congestion    |
| Full-Day Simulation | Simulates all traffic periods |
| Emergency Dispatch  | Simulates emergency routing   |

---

# 📊 Visualization System

The project includes an advanced visualization dashboard built using Plotly and Streamlit.

## Visual Components

* Interactive transportation maps
* Route highlighting
* Traffic heatmaps
* Congestion analysis charts
* Transit route visualization
* Simulation dashboards

---

# 🖥 User Interface

The Streamlit application is organized into multiple tabs:

| Tab                 | Function                              |
| ------------------- | ------------------------------------- |
| Network Overview    | Full Cairo transportation graph       |
| Route Planner       | Dijkstra & A* route optimization      |
| Emergency Dispatch  | Alternative emergency routes          |
| Transit Optimizer   | DP scheduling & Knapsack optimization |
| Traffic Simulation  | Scenario simulation                   |
| Congestion Forecast | ML traffic prediction                 |

---

# 📈 Performance Evaluation

| Algorithm              | Runtime |
| ---------------------- | ------- |
| Dijkstra               | 0.8 ms  |
| A* Search              | 0.5 ms  |
| Kruskal MST            | 1.2 ms  |
| Transit DP             | 3.5 ms  |
| Random Forest Training | 1.2 sec |

## Key Findings

✅ A* visits 30–45% fewer nodes than Dijkstra
✅ Efficient real-time routing performance
✅ Accurate congestion forecasting
✅ Effective emergency route optimization

---

# 🚧 Challenges & Solutions

| Challenge                  | Solution                      |
| -------------------------- | ----------------------------- |
| Dynamic traffic conditions | Time-dependent weights        |
| Graph disconnectivity      | Bidirectional edge handling   |
| Emergency route overlap    | Edge-disjoint path generation |
| DP memory optimization     | 1D rolling arrays             |
| ML underfitting            | Dataset augmentation          |
| Streamlit recomputation    | Caching optimization          |

---

# 🔮 Future Improvements

The system can be extended with:

* Real-time GPS integration
* AI traffic prediction
* Reinforcement Learning signal control
* IoT traffic sensors
* Graph Neural Networks
* Cloud deployment
* Multi-modal transportation planning
* Autonomous vehicle coordination

---

# 💡 Educational Value

This project demonstrates practical applications of:

* Graph Theory
* Design & Analysis of Algorithms
* Dynamic Programming
* Greedy Algorithms
* Machine Learning
* Transportation Engineering
* Smart-City Systems
* Simulation Systems

---

# 👥 Team Members

* Menna Allah Osama
* Catherine Adel Zaki
* Soha Hossam
* Arwa Mohey
* Samira Saed
* Mariam Nady
* Veronica Wassim

---

# 🛠 Installation Guide

## 1️⃣ Clone Repository

```bash
git clone <repository-url>
cd smart-city-transportation-optimizer
```

## 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

## 3️⃣ Run Streamlit Application

```bash
streamlit run app.py
```

---

# 📦 Required Libraries

```bash
pip install streamlit
pip install networkx
pip install plotly
pip install scikit-learn
pip install pandas
pip install numpy
```

---

# 📸 Suggested Screenshots

You can later add:

```text
/screenshots
    network_overview.png
    route_planner.png
    emergency_dispatch.png
    traffic_heatmap.png
    congestion_forecast.png
```

Example:

```md
## Network Overview
![Network](screenshots/network_overview.png)
```

---

# 🌟 Real-World Applications

## 🚦 Smart Cities

Used for intelligent urban transportation management.

## 🚑 Emergency Systems

Improves ambulance and fire truck routing.

## 🚌 Public Transportation

Optimizes bus and metro scheduling.

## 🛣 Infrastructure Planning

Supports road expansion and maintenance decisions.

---

# 🏆 Conclusion

The **Greater Cairo Smart Transportation Optimizer** successfully demonstrates how advanced algorithmic techniques can solve real-world smart-city transportation challenges.

By combining:

* Graph Theory
* Dynamic Programming
* Greedy Algorithms
* Machine Learning
* Traffic Simulation
* Interactive Visualization

The system provides an intelligent transportation optimization framework capable of improving urban mobility, emergency response efficiency, and transportation infrastructure planning.

---

# 📚 References

* NetworkX Documentation
* Plotly Documentation
* Streamlit Documentation
* Scikit-learn Documentation
* Transportation Engineering Research
* Dijkstra & A* Research Papers
* Smart City Transportation Studies

---

# 📄 License

This project was developed for educational and academic purposes under the Faculty of Computer Science & Engineering at Alamein International University.

---

<div align="center">

# ⭐ Thank You ⭐

### Smart Transportation Systems for Smarter Cities 🚦

</div>
