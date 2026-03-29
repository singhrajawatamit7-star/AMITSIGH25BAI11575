# TRAFFIC SIGNAL POWERED BY ARTIFICIAL INTELLIGENCE
An intelligent urban traffic routing system that combines graph traversal algorithms (BFS & DFS) with a machine learning model to determine optimal pathfinding strategies across a simulated road network.
## ABOUT PROJECT
The project is made to control the traffic network of the city using BFS and DFS.
## PROJECT STRUCTURE

```
traffic-optimizer/
│
├── traffic_optimizer.py     # Main source file
├── README.md                # Project documentation
└── requirements.txt         # Python dependencies
```

---

## HOW IT WORKS

### 1. GRAPH
A graph of 8 intersections (`A` through `H`) is created with 11 road connections, simulating a small urban road network.

```
A - B - D - G
|   |   |   |
C - D   E - G - H
|       |
F ----- E
|
H
```

### 2. BFS & DFS (Implemented from Scratch)

| Algorithm | Strategy | Best For |
|---|---|---|
| **DFS** | Stack-based deep exploration | Finding *any* valid path |
| **BFS** | Queue-based level-by-level | Finding the *shortest* path |

### 3. DATASET GENERATION
300 random source–destination pairs are sampled. For each pair, both algorithms run and key features are extracted:

- Start/goal node degrees
- Graph density
- Shortest path length (BFS)
- Euclidean proximity proxy (character distance)

### 4. ML MODEL 
A `DecisionTreeClassifier` (max depth = 5) is trained on the generated dataset to predict which algorithm — DFS or BFS — would explore fewer nodes for a given scenario.

- **Label 0** → DFS performs better
- **Label 1** → BFS performs better

### 5. VISUALIZATION
Two path visualizations are generated:
- 🟠 **Orange** — DFS exploration path
- 🟢 **Green** — BFS shortest path

---

## GET STARTED

### Prerequisites

- Python 3.8 or higher
- pip

### INSTALLATION

```bash
# Clone the repository
git clone https://github.com/your-username/traffic-signal-optimizer.git
cd traffic-signal-optimizer

# Install dependencies
pip install -r requirements.txt
```

### `requirements.txt`

```
networkx
matplotlib
pandas
scikit-learn
numpy
```

---

## USAGE

```bash
python traffic_optimizer.py
```

The script will:
1. Build the road network graph
2. Find routes from node `A` to node `H` using both DFS and BFS
3. Display path visualizations
4. Generate a 300-sample training dataset
5. Train and evaluate the ML model
6. Print accuracy and classification report

---

## 📤 OUTPUT

```
=== AI-Powered Traffic Signal Optimizer ===

Finding route from A to H...
DFS Route (any path):  ['A', 'C', 'F', 'H']
BFS Route (shortest):  ['A', 'B', 'E', 'G', 'H']

Generating dataset from 300+ traffic scenarios...
Dataset shape: (298, 9)

Training ML model to predict best algorithm...
ML Model Accuracy: 0.87

              precision    recall  f1-score   support
 DFS Better       0.85      0.82      0.83        39
 BFS Better       0.88      0.90      0.89        51
    accuracy                          0.87        90
```

---

## SCOPES

- [ ] Add **weighted edges** (travel time) and implement **Dijkstra's algorithm**
- [ ] Simulate **dynamic congestion** by blocking edges at runtime
- [ ] Implement **signal timing logic** based on queue length at intersections
- [ ] Build an **animated vehicle movement** simulation using Pygame
- [ ] Integrate **real-world map data** via OpenStreetMap APIs

---

## License

This project is licensed under the [MIT License](LICENSE).

---
