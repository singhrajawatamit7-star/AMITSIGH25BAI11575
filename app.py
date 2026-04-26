import os
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import networkx as nx

from AIMLTRAFFICcode import create_traffic_graph, dfs_path, bfs_path, generate_dataset, train_ml_model

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

# Initialize graph and model
G = create_traffic_graph()
df = generate_dataset(G, num_samples=300)
model = train_ml_model(df)

@app.route('/api/network', methods=['GET'])
def get_network():
    nodes = list(G.nodes())
    edges = list(G.edges())
    # Generate some simple coordinates for frontend visualization to use as base
    # (Optional: frontend can recalculate better layout)
    return jsonify({"nodes": nodes, "edges": edges})

@app.route('/api/route', methods=['GET'])
def get_route():
    start = request.args.get('start', 'A')
    goal = request.args.get('goal', 'H')
    
    if start not in G.nodes() or goal not in G.nodes():
        return jsonify({"error": "Invalid start or goal node"}), 400
        
    dfs_route = dfs_path(G, start, goal)
    bfs_route = bfs_path(G, start, goal)
    
    return jsonify({
        "dfs": dfs_route,
        "bfs": bfs_route
    })

@app.route('/api/ml-prediction', methods=['GET'])
def get_ml_prediction():
    start = request.args.get('start', 'A')
    goal = request.args.get('goal', 'H')
    
    if model is None:
        return jsonify({"prediction": "BFS", "confidence": 1.0, "reason": "No model trained (only 1 class)"})
        
    if start not in G.nodes() or goal not in G.nodes() or start == goal:
        return jsonify({"error": "Invalid start or goal node"}), 400
        
    bfs_route = bfs_path(G, start, goal)
    features = [
        G.degree(start),
        G.degree(goal),
        len(bfs_route) - 1,
        round(nx.density(G), 4),
        abs(ord(start) - ord(goal))
    ]
    
    # Predict (0 = DFS Better, 1 = BFS Better)
    pred = model.predict([features])[0]
    prob = model.predict_proba([features])[0][pred]
    
    recommended = "BFS" if pred == 1 else "DFS"
    
    return jsonify({
        "recommended": recommended,
        "probability": float(prob)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
