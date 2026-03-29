import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
import random
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report
import numpy as np
import warnings
warnings.filterwarnings('ignore')


def create_traffic_graph():
    G = nx.Graph()
    
    intersections = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    G.add_nodes_from(intersections)
    

    roads = [
        ('A', 'B'), ('A', 'C'), ('B', 'D'), ('B', 'E'),
        ('C', 'D'), ('C', 'F'), ('D', 'G'), ('E', 'G'),
        ('F', 'H'), ('G', 'H'), ('E', 'F'), ('B', 'F')
    ]
    G.add_edges_from(roads)
    return G


def dfs_path(graph, start, goal):
    """Depth First Search - Deep exploration"""
    stack = [(start, [start])]
    visited = set()
    
    while stack:
        current, path = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        
        if current == goal:
            return path
        
        for neighbor in graph.neighbors(current):
            if neighbor not in visited:
                stack.append((neighbor, path + [neighbor]))
    return None

def bfs_path(graph, start, goal):
    """Breadth First Search - Shortest Path"""
    queue = deque([(start, [start])])
    visited = set([start])
    
    while queue:
        current, path = queue.popleft()
        
        if current == goal:
            return path
        
        for neighbor in graph.neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return None


def generate_dataset(G, num_samples=1000):
    data = []
    nodes = list(G.nodes())
    
    for _ in range(num_samples):
        start = random.choice(nodes)
        goal = random.choice(nodes)
        while goal == start:
            goal = random.choice(nodes)
        
        dfs_p = dfs_path(G, start, goal)
        bfs_p = bfs_path(G, start, goal)
        
        if not dfs_p or not bfs_p:
            continue
        
        features = {
            'start_degree': G.degree(start),
            'goal_degree': G.degree(goal),
            'shortest_path_length': len(bfs_p) - 1,
            'graph_density': round(nx.density(G), 4),
            'euclidean_sim': abs(ord(start) - ord(goal))
        }
        
        
        label = 0 if len(dfs_p) <= len(bfs_p) else 1
        
        row = list(features.values()) + [label]
        data.append(row)
    
    columns = list(features.keys()) + ['better_algo']
    df = pd.DataFrame(data, columns=columns)
    return df


def train_ml_model(df):
    X = df.drop(['better_algo'], axis=1)
    y = df['better_algo']
    
    
    if len(y.unique()) < 2:
        print("  Only one class found in dataset. ML classification skipped.")
        print("BFS usually performs better for shortest path in traffic networks.")
        return None
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    
    model = DecisionTreeClassifier(max_depth=6, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    print(f"\n ML Model Accuracy: {acc:.2f} ({acc*100:.1f}%)")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, 
                                labels=[0, 1], 
                                target_names=['DFS Better', 'BFS Better'],
                                zero_division=0))
    return model


def visualize_path(G, path, title, color='red'):
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_color='lightblue', 
            node_size=800, font_size=12, edge_color='gray')
    
    if path:
        path_edges = list(zip(path, path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, 
                               edge_color=color, width=3)
        nx.draw_networkx_nodes(G, pos, nodelist=path, 
                               node_color=color, node_size=900)
    
    plt.title(title)
    plt.show()


if __name__ == "__main__":
    print("=== AI-Powered Traffic Signal Optimizer ===\n")
    
    G = create_traffic_graph()
    
    
    start, goal = 'A', 'H'
    print(f"Finding route from {start} to {goal}...\n")
    
    dfs_route = dfs_path(G, start, goal)
    bfs_route = bfs_path(G, start, goal)
    
    print(f"DFS Route (Any Path)     : {dfs_route}")
    print(f"BFS Route (Shortest Path): {bfs_route}\n")
    
    
    visualize_path(G, dfs_route, "DFS Exploration Path", 'orange')
    visualize_path(G, bfs_route, "BFS Shortest Path - Best for Traffic Clearance", 'green')
    
    
    print("Generating dataset from traffic scenarios...")
    df = generate_dataset(G, num_samples=1000)
    print(f"Dataset created with {len(df)} samples\n")
    
    print("Training Machine Learning Model to predict best algorithm...")
    model = train_ml_model(df)
    
    print("\n Project executed successfully!")
    print("BFS is generally better for finding shortest routes in traffic networks.")