# 🚚 AI-Based Delivery Route Optimization System
### Amravati City — A* vs Uniform Cost Search

> **Academic Project** | AI & Data Science | Python · Flask · OSMnx · MongoDB · Leaflet.js · Chart.js · R

---

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
4. [Folder Structure](#folder-structure)
5. [Prerequisites](#prerequisites)
6. [Installation](#installation)
7. [MongoDB Setup](#mongodb-setup)
8. [Running the App](#running-the-app)
9. [R Analytics Setup](#r-analytics-setup)
10. [Algorithm Details](#algorithm-details)
11. [API Reference](#api-reference)
12. [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

This system implements two classic AI search algorithms — **A\*** and **Uniform Cost Search (UCS)** — on the real road network of **Amravati, Maharashtra, India** to solve the delivery route optimization problem.

The application finds:
- **Shortest Path** using A\* (heuristic-guided search)
- **Optimal Cost Path** using UCS (guaranteed minimum cost)

Both paths are visualized simultaneously on an interactive Leaflet.js map, with detailed analytics and a comparison dashboard.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🗺️ Interactive Map | Click-to-select source & destination on real Amravati map |
| 🤖 Dual Algorithm | A\* (green) and UCS (blue) run in parallel |
| 📊 Analytics Dashboard | Chart.js graphs + R statistical analysis |
| 🚦 Traffic Simulation | Random traffic multiplier on travel time |
| 🚚 Vehicle Animation | Animated marker moves along chosen route |
| 🌙 Dark / Light Mode | Toggleable theme with localStorage persistence |
| 💾 MongoDB Storage | Route results, user sessions, feedback stored |
| ⭐ Feedback System | Star rating + text feedback from users |

---

## 🛠 Tech Stack

```
Backend   : Python 3.10+, Flask 3.0
Graph     : OSMnx 1.9, NetworkX 3.2, Geopy 2.4
Frontend  : HTML5, CSS3 (custom design system), Vanilla JS
Maps      : Leaflet.js 1.9 (CDN)
Charts    : Chart.js 4.4 (CDN)
Database  : MongoDB 6+ (pymongo)
Analytics : R 4.x (mongolite, ggplot2, jsonlite)
```

---

## 📁 Folder Structure

```
amravati_delivery/
│
├── app.py                    # Flask application entry point
├── config.py                 # Configuration & environment variables
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (create manually)
│
├── algorithms/
│   ├── __init__.py
│   ├── astar.py              # A* algorithm with haversine heuristic
│   └── ucs.py                # Uniform Cost Search (Dijkstra variant)
│
├── utils/
│   ├── __init__.py
│   ├── graph_loader.py       # OSMnx loader with 3-tier fallback
│   └── cost_calculator.py    # Travel time, cost, fuel, carbon emission
│
├── templates/
│   ├── base.html             # Shared layout (navbar, toasts, loader)
│   ├── login.html            # Login page with avatar selector
│   ├── home.html             # Welcome/home page
│   ├── optimize.html         # Route optimization + Leaflet map
│   ├── result.html           # Result page + vehicle animation
│   ├── dashboard.html        # Analytics dashboard (Chart.js + R)
│   └── feedback.html         # Feedback form with star rating
│
├── static/
│   ├── css/
│   │   └── main.css          # Global design system CSS
│   └── js/
│       └── main.js           # Global JS utilities
│
├── r_scripts/
│   └── analysis.R            # R statistical analysis script
│
└── data/
    └── amravati_graph.graphml  # Cached OSMnx graph (auto-generated)
```

---

## 📦 Prerequisites

- **Python** 3.10 or higher → https://python.org
- **MongoDB** 6.0+ → https://mongodb.com/try/download/community
- **R** 4.x (optional, for analytics) → https://cran.r-project.org
- **Git** (optional)

---

## ⚙️ Installation

### Step 1 — Clone / Download the project
```bash
# If using git:
git clone <your-repo-url>
cd amravati_delivery

# Or just navigate to the project folder:
cd amravati_delivery
```

### Step 2 — Create a virtual environment (recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install Python dependencies
```bash
pip install -r requirements.txt
```

> ⚠️ **OSMnx installation note:** OSMnx requires GDAL. If installation fails on Windows, install from wheel:
> ```bash
> pip install osmnx --no-build-isolation
> ```

### Step 4 — Create `.env` file
Create a file named `.env` in the project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
MONGO_URI=mongodb://localhost:27017/
DB_NAME=amravati_delivery
```

---

## 🍃 MongoDB Setup

### Option A — Local MongoDB
1. Download and install MongoDB Community: https://mongodb.com/try/download/community
2. Start MongoDB service:
   ```bash
   # Windows (as service — already running after install)
   net start MongoDB

   # macOS
   brew services start mongodb/brew/mongodb-community

   # Linux
   sudo systemctl start mongod
   ```
3. The app auto-creates the database and collections on first run.

### Option B — MongoDB Atlas (Cloud, Free Tier)
1. Sign up at https://cloud.mongodb.com
2. Create a free cluster
3. Get the connection string and set in `.env`:
   ```env
   MONGO_URI=mongodb+srv://<user>:<password>@cluster0.xxxxx.mongodb.net/
   ```

### Option C — No MongoDB (Fallback Mode)
The app works without MongoDB! It falls back to **in-memory storage** automatically. You'll see a warning in the console but everything still works.

---

## ▶️ Running the App

```bash
# Make sure venv is activated and you're in the project folder
python app.py
```

Open your browser: **http://localhost:5000**

### First-time startup
On first run, the app will attempt to download the Amravati road network from OpenStreetMap via OSMnx. This requires internet access and takes 30–60 seconds. The graph is cached to `data/amravati_graph.graphml` for future runs.

**If no internet:** The app uses a built-in synthetic Amravati graph with 20 nodes and real landmark coordinates. All features work normally.

---

## 📈 R Analytics Setup

### Install R packages
Open R or RStudio and run:
```r
install.packages(c("mongolite", "ggplot2", "dplyr", "jsonlite"))
```

### Run the analysis script
```bash
# From project root:
Rscript r_scripts/analysis.R
```

The script:
- Connects to MongoDB (or uses sample data if unavailable)
- Performs **descriptive statistics** on route distances and times
- Runs a **Welch t-test** comparing A\* vs UCS performance
- Outputs a recommendation on which algorithm wins per scenario
- The results are also displayed in the Dashboard page via a dedicated API endpoint

---

## 🧮 Algorithm Details

### A\* (A-Star)
```
f(n) = g(n) + h(n)
  g(n) = actual cost from start to node n
  h(n) = haversine distance heuristic to goal (admissible)
```
- Uses a **min-heap priority queue** (heapq)
- Heuristic is the straight-line great-circle distance (never overestimates → admissible)
- Returns the **shortest** path in terms of distance

### Uniform Cost Search (UCS)
```
Expands node with lowest g(n) first
  g(n) = cumulative actual edge weight from start
```
- Equivalent to Dijkstra's algorithm
- No heuristic — purely cost-driven
- Returns the **optimal cost** path
- Explores more nodes than A\* but guarantees minimum total cost

### Why both?
| Criterion | A\* | UCS |
|---|---|---|
| Speed | Faster (heuristic prunes) | Slower (full expansion) |
| Path | Shortest distance | Minimum cost |
| Nodes explored | Fewer | More |
| Completeness | ✅ | ✅ |
| Optimality | ✅ (admissible h) | ✅ |

---

## 🔌 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/find_route` | POST | Run A\* + UCS, returns both paths |
| `/api/graph_info` | GET | Graph node/edge counts |
| `/api/sample_locations` | GET | 10 Amravati landmarks |
| `/api/analytics_data` | GET | Dashboard metrics |
| `/api/submit_feedback` | POST | Save feedback to MongoDB |

### `/api/find_route` Request
```json
{
  "src_lat": 20.9374, "src_lng": 77.7796,
  "dst_lat": 20.9310, "dst_lng": 77.7530,
  "category": "delivery"
}
```

### `/api/find_route` Response
```json
{
  "astar": {
    "path": [[lat, lng], ...],
    "distance_km": 3.24,
    "time_min": 7.77,
    "cost_rs": 25.92,
    "nodes_explored": 142,
    "exec_time_ms": 18.4
  },
  "ucs": { ... },
  "traffic": "Moderate",
  "traffic_multiplier": 1.3
}
```

---

## 🔧 Troubleshooting

### OSMnx download fails
The app automatically falls back to the synthetic graph. No action needed.

### MongoDB connection refused
The app uses in-memory fallback. Start MongoDB or ignore the warning.

### Port 5000 in use
```bash
python app.py  # then change port in app.py last line:
# app.run(port=5001)
```

### Chart.js not loading
Check internet connection — Chart.js loads from CDN. Alternatively, download and place in `static/js/`.

### R script errors
```r
# Check R version
R --version  # needs 4.0+

# Reinstall packages
install.packages("mongolite", dependencies=TRUE)
```

---

## 👨‍💻 Academic Project Credits

| Item | Detail |
|---|---|
| City | Amravati, Maharashtra, India |
| Map Data | © OpenStreetMap contributors |
| Algorithms | A\* Search, Uniform Cost Search |
| Subject | AI & Data Science |
| Technologies | Python, Flask, OSMnx, MongoDB, R, Leaflet.js |

---

## 📄 License

This project is for **academic purposes only**.
Map data © OpenStreetMap contributors (ODbL license).
