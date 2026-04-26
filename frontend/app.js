const API_BASE = 'http://localhost:5000/api';

const canvas = document.getElementById('traffic-map');
const ctx = canvas.getContext('2d');

let networkData = { nodes: [], edges: [] };
let nodePositions = {};
let currentPaths = { dfs: [], bfs: [] };
let animationProgress = 0;
let animating = false;

// Custom layout for our 8 nodes to make it look like a city map
const PRESET_LAYOUT = {
    'A': { x: 0.2, y: 0.2 },
    'B': { x: 0.4, y: 0.2 },
    'C': { x: 0.2, y: 0.5 },
    'D': { x: 0.4, y: 0.5 },
    'E': { x: 0.6, y: 0.5 },
    'F': { x: 0.2, y: 0.8 },
    'G': { x: 0.6, y: 0.2 },
    'H': { x: 0.8, y: 0.8 }
};

function resizeCanvas() {
    const parent = canvas.parentElement;
    canvas.width = parent.clientWidth;
    canvas.height = parent.clientHeight;
    calculateNodePositions();
    drawMap();
}

window.addEventListener('resize', resizeCanvas);

function calculateNodePositions() {
    nodePositions = {};
    const padding = 60;
    const w = canvas.width - padding * 2;
    const h = canvas.height - padding * 2;

    networkData.nodes.forEach(node => {
        // Fallback to random if not in preset (for robustness)
        const preset = PRESET_LAYOUT[node] || { x: Math.random(), y: Math.random() };
        nodePositions[node] = {
            x: padding + preset.x * w,
            y: padding + preset.y * h
        };
    });
}

async function fetchNetwork() {
    try {
        const res = await fetch(`${API_BASE}/network`);
        networkData = await res.json();
        
        // Populate dropdowns
        const startSelect = document.getElementById('start-node');
        const goalSelect = document.getElementById('goal-node');
        startSelect.innerHTML = '';
        goalSelect.innerHTML = '';
        
        networkData.nodes.forEach(node => {
            startSelect.add(new Option(`Intersection ${node}`, node));
            goalSelect.add(new Option(`Intersection ${node}`, node));
        });
        
        goalSelect.value = 'H'; // Default
        
        resizeCanvas();
    } catch (err) {
        console.error("Failed to load network", err);
    }
}

function drawMap() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw all edges
    ctx.lineWidth = 4;
    networkData.edges.forEach(([n1, n2]) => {
        const p1 = nodePositions[n1];
        const p2 = nodePositions[n2];
        if(!p1 || !p2) return;
        
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.strokeStyle = 'rgba(51, 65, 85, 0.8)'; // var(--edge-color)
        ctx.stroke();
    });

    // Draw active paths
    if (currentPaths.dfs.length > 0) {
        drawPath(currentPaths.dfs, '#f59e0b', 8, Math.min(1, animationProgress));
    }
    if (currentPaths.bfs.length > 0) {
        drawPath(currentPaths.bfs, '#10b981', 4, Math.max(0, animationProgress - 1));
    }

    // Draw nodes
    networkData.nodes.forEach(node => {
        const p = nodePositions[node];
        if(!p) return;
        
        ctx.beginPath();
        ctx.arc(p.x, p.y, 16, 0, Math.PI * 2);
        ctx.fillStyle = '#1e293b';
        ctx.fill();
        ctx.lineWidth = 3;
        ctx.strokeStyle = '#3b82f6';
        ctx.stroke();

        ctx.fillStyle = '#f8fafc';
        ctx.font = 'bold 14px Outfit';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(node, p.x, p.y);
    });
}

function drawPath(path, color, width, progress) {
    if (path.length < 2 || progress <= 0) return;
    
    const totalSegments = path.length - 1;
    const segmentsToDraw = progress * totalSegments;
    
    ctx.lineWidth = width;
    ctx.strokeStyle = color;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    
    ctx.beginPath();
    ctx.moveTo(nodePositions[path[0]].x, nodePositions[path[0]].y);
    
    for (let i = 0; i < Math.floor(segmentsToDraw); i++) {
        const p = nodePositions[path[i+1]];
        ctx.lineTo(p.x, p.y);
    }
    
    const remainder = segmentsToDraw % 1;
    if (remainder > 0) {
        const p1 = nodePositions[path[Math.floor(segmentsToDraw)]];
        const p2 = nodePositions[path[Math.ceil(segmentsToDraw)]];
        const x = p1.x + (p2.x - p1.x) * remainder;
        const y = p1.y + (p2.y - p1.y) * remainder;
        ctx.lineTo(x, y);
    }
    
    ctx.stroke();
}

function animate() {
    if (!animating) return;
    animationProgress += 0.03; // speed
    drawMap();
    if (animationProgress < 2) {
        requestAnimationFrame(animate);
    } else {
        animating = false;
    }
}

document.getElementById('find-route-btn').addEventListener('click', async () => {
    const start = document.getElementById('start-node').value;
    const goal = document.getElementById('goal-node').value;
    
    const btnText = document.querySelector('.btn-text');
    const loader = document.querySelector('.loader');
    
    btnText.classList.add('hidden');
    loader.classList.remove('hidden');
    
    document.getElementById('ml-loading').classList.remove('hidden');
    document.getElementById('ml-result').classList.add('hidden');

    try {
        const [routeRes, mlRes] = await Promise.all([
            fetch(`${API_BASE}/route?start=${start}&goal=${goal}`),
            fetch(`${API_BASE}/ml-prediction?start=${start}&goal=${goal}`)
        ]);
        
        const routeData = await routeRes.json();
        const mlData = await mlRes.json();
        
        currentPaths = routeData;
        animationProgress = 0;
        animating = true;
        animate();
        
        document.getElementById('ml-loading').classList.add('hidden');
        document.getElementById('ml-result').classList.remove('hidden');
        
        const algoRec = document.getElementById('algo-rec');
        algoRec.innerText = mlData.recommended;
        algoRec.style.color = mlData.recommended === 'BFS' ? 'var(--bfs-color)' : 'var(--dfs-color)';
        document.getElementById('algo-conf').innerText = `${(mlData.probability * 100).toFixed(1)}%`;
        
    } catch (err) {
        console.error(err);
        alert("Failed to find route. Make sure backend is running.");
    } finally {
        btnText.classList.remove('hidden');
        loader.classList.add('hidden');
    }
});

// Init
fetchNetwork();
