"""
AI-Based Delivery Route Optimization System
City: Amravati, Maharashtra, India
Backend: Flask + OSMnx + NetworkX + MongoDB
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import time
import random
from datetime import datetime
import os
import logging

try:
    from pymongo import MongoClient
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False

# Algorithm imports
from algorithms.astar import astar_algorithm
from algorithms.ucs import ucs_algorithm
from utils.graph_loader import GraphLoader
from utils.cost_calculator import CostCalculator

# ─────────────────────────────────────────
# App Configuration
# ─────────────────────────────────────────
app = Flask(__name__)
app.secret_key = "amravati_route_optimizer_2024_secret"
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────
# MongoDB Connection
# ─────────────────────────────────────────
try:
    if not PYMONGO_AVAILABLE:
        raise Exception("pymongo not installed")
    mongo_client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)
    mongo_client.server_info()
    db = mongo_client["amravati_delivery_db"]
    users_collection = db["users"]
    routes_collection = db["routes"]
    feedback_collection = db["feedback"]
    analytics_collection = db["analytics"]
    logger.info("✅ MongoDB connected successfully")
    MONGO_AVAILABLE = True
except Exception as e:
    logger.warning(f"⚠️ MongoDB not available: {e}. Using in-memory storage.")
    MONGO_AVAILABLE = False
    # Fallback in-memory storage
    in_memory_users = {}
    in_memory_routes = []
    in_memory_feedback = []
    in_memory_analytics = []

# ─────────────────────────────────────────
# Graph Loader (Amravati city map)
# ─────────────────────────────────────────
graph_loader = GraphLoader()
G = graph_loader.load_graph()

# ─────────────────────────────────────────
# Helper: MongoDB / In-memory abstraction
# ─────────────────────────────────────────
def save_user(user_data):
    if MONGO_AVAILABLE:
        result = users_collection.insert_one(user_data)
        return str(result.inserted_id)
    else:
        uid = str(len(in_memory_users) + 1)
        in_memory_users[uid] = user_data
        return uid

def get_all_users():
    if MONGO_AVAILABLE:
        return list(users_collection.find({}, {"_id": 0}).sort("login_time", -1))
    else:
        return list(in_memory_users.values())

def get_all_routes():
    if MONGO_AVAILABLE:
        return list(routes_collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(50))
    else:
        return in_memory_routes[-50:]

def save_route(route_data):
    if MONGO_AVAILABLE:
        routes_collection.insert_one(route_data)
    else:
        in_memory_routes.append(route_data)

def save_feedback_db(fb_data):
    if MONGO_AVAILABLE:
        feedback_collection.insert_one(fb_data)
    else:
        in_memory_feedback.append(fb_data)

def get_all_feedback():
    if MONGO_AVAILABLE:
        return list(feedback_collection.find({}, {"_id": 0}).sort("timestamp", -1))
    else:
        return in_memory_feedback

def save_analytics(data):
    if MONGO_AVAILABLE:
        analytics_collection.insert_one(data)
    else:
        in_memory_analytics.append(data)

def get_analytics():
    if MONGO_AVAILABLE:
        return list(analytics_collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(100))
    else:
        return in_memory_analytics[-100:]

# ─────────────────────────────────────────
# Routes
# ─────────────────────────────────────────

@app.route("/")
def index():
    """Redirect to login page"""
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page"""
    if request.method == "POST":
        data = request.get_json()
        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        avatar = data.get("avatar", "1")

        if not username:
            return jsonify({"success": False, "error": "Username is required"})

        user_data = {
            "username": username,
            "email": email,
            "avatar": avatar,
            "login_time": datetime.now().isoformat(),
            "created_at": datetime.now()
        }

        user_id = save_user(user_data)
        session["user_id"] = user_id
        session["username"] = username
        session["avatar"] = avatar

        return jsonify({"success": True, "username": username})

    return render_template("login.html")

@app.route("/home")
def home():
    """Home / Welcome page"""
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("home.html",
                           username=session.get("username"),
                           avatar=session.get("avatar", "1"))

@app.route("/optimize")
def optimize():
    """Route optimization page"""
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("optimize.html",
                           username=session.get("username"))

@app.route("/result")
def result():
    """Result page"""
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("result.html",
                           username=session.get("username"))

@app.route("/dashboard")
def dashboard():
    """Analytics dashboard"""
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html",
                           username=session.get("username"))

@app.route("/feedback")
def feedback():
    """Feedback page"""
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("feedback.html",
                           username=session.get("username"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/admin")
def admin():
    """Admin panel displaying user data and feedback"""
    users = get_all_users()
    feedbacks = get_all_feedback()
    return render_template("admin.html", users=users, feedbacks=feedbacks)

# ─────────────────────────────────────────
# API Endpoints
# ─────────────────────────────────────────

@app.route("/api/find_route", methods=["POST"])
def find_route():
    """
    Core API: Run A* and UCS on Amravati graph.
    Returns both paths with metrics.
    """
    try:
        data = request.get_json()
        src_lat = float(data["src_lat"])
        src_lng = float(data["src_lng"])
        dst_lat = float(data["dst_lat"])
        dst_lng = float(data["dst_lng"])
        category = data.get("category", "normal")

        logger.info(f"Route request: ({src_lat},{src_lng}) → ({dst_lat},{dst_lng}), category={category}")

        # Find nearest nodes in graph
        src_node = graph_loader.nearest_node(src_lat, src_lng)
        dst_node = graph_loader.nearest_node(dst_lat, dst_lng)

        if src_node is None or dst_node is None:
            return jsonify({"success": False, "error": "Could not find nearest road nodes. Try clicking closer to a road."})

        if src_node == dst_node:
            return jsonify({"success": False, "error": "Source and destination are the same location."})

        # ── Run A* Algorithm ──
        t0 = time.time()
        astar_result = astar_algorithm(G, src_node, dst_node)
        astar_time_ms = round((time.time() - t0) * 1000, 2)

        # ── Run UCS Algorithm ──
        t0 = time.time()
        ucs_result = ucs_algorithm(G, src_node, dst_node)
        ucs_time_ms = round((time.time() - t0) * 1000, 2)

        if not astar_result["success"] or not ucs_result["success"]:
            return jsonify({"success": False, "error": "No path found between these points. Roads may not be connected."})

        # ── Cost Calculator ──
        calc = CostCalculator(category)

        astar_coords = graph_loader.path_to_coords(astar_result["path"])
        ucs_coords = graph_loader.path_to_coords(ucs_result["path"])

        astar_distance = astar_result["distance"]
        ucs_distance = ucs_result["distance"]

        astar_time_est = calc.travel_time(astar_distance)
        ucs_time_est = calc.travel_time(ucs_distance)

        astar_cost = calc.delivery_cost(astar_distance)
        ucs_cost = calc.delivery_cost(ucs_distance)

        # Deterministic traffic based on distance (no randomness)
        if astar_distance < 2:
            traffic_level = "Low"
        elif astar_distance < 5:
            traffic_level = "Moderate"
        else:
            traffic_level = "High"
        traffic_mult = {"Low": 1.0, "Moderate": 1.2, "High": 1.5}[traffic_level]

        result_data = {
            "success": True,
            "astar": {
                "path": astar_coords,
                "distance_km": round(astar_distance, 3),
                "time_minutes": round(astar_time_est * traffic_mult, 1),
                "cost_inr": round(astar_cost, 2),
                "nodes_explored": astar_result["nodes_explored"],
                "algo_time_ms": astar_time_ms,
                "traffic": traffic_level
            },
            "ucs": {
                "path": ucs_coords,
                "distance_km": round(ucs_distance, 3),
                "time_minutes": round(ucs_time_est * traffic_mult, 1),
                "cost_inr": round(ucs_cost, 2),
                "nodes_explored": ucs_result["nodes_explored"],
                "algo_time_ms": ucs_time_ms,
                "traffic": traffic_level
            },
            "category": category,
            "traffic_level": traffic_level,
            "src": {"lat": src_lat, "lng": src_lng},
            "dst": {"lat": dst_lat, "lng": dst_lng}
        }

        # Store in DB
        route_record = {
            **result_data,
            "username": session.get("username", "anonymous"),
            "timestamp": datetime.now().isoformat()
        }
        route_record.pop("success")
        save_route(route_record)

        # Analytics
        save_analytics({
            "astar_distance": astar_distance,
            "ucs_distance": ucs_distance,
            "astar_time_ms": astar_time_ms,
            "ucs_time_ms": ucs_time_ms,
            "astar_nodes": astar_result["nodes_explored"],
            "ucs_nodes": ucs_result["nodes_explored"],
            "category": category,
            "timestamp": datetime.now().isoformat()
        })

        return jsonify(result_data)

    except Exception as e:
        logger.error(f"Route finding error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/submit_feedback", methods=["POST"])
def submit_feedback():
    """Save user feedback"""
    try:
        data = request.get_json()
        fb = {
            "name": data.get("name", "Anonymous"),
            "rating": int(data.get("rating", 3)),
            "message": data.get("message", ""),
            "username": session.get("username", "guest"),
            "timestamp": datetime.now().isoformat()
        }
        save_feedback_db(fb)
        return jsonify({"success": True, "message": "Thank you for your feedback!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/analytics_data", methods=["GET"])
def analytics_data():
    """Return analytics for dashboard charts"""
    try:
        records = get_analytics()
        feedback = get_all_feedback()

        # Build chart data
        astar_times = [r["astar_time_ms"] for r in records if "astar_time_ms" in r]
        ucs_times = [r["ucs_time_ms"] for r in records if "ucs_time_ms" in r]
        astar_dists = [r["astar_distance"] for r in records if "astar_distance" in r]
        ucs_dists = [r["ucs_distance"] for r in records if "ucs_distance" in r]
        categories = [r.get("category", "normal") for r in records]

        # Category counts
        cat_counts = {}
        for c in categories:
            cat_counts[c] = cat_counts.get(c, 0) + 1

        # Algorithm winner analysis
        astar_wins = sum(1 for a, u in zip(astar_dists, ucs_dists) if a <= u)
        ucs_wins = len(astar_dists) - astar_wins

        # Rating distribution
        ratings = [f["rating"] for f in feedback]
        rating_dist = {str(i): ratings.count(i) for i in range(1, 6)}

        # Recent 10 comparisons for line chart
        recent = records[-10:]
        labels = [f"Run {i+1}" for i in range(len(recent))]
        r_astar = [r.get("astar_distance", 0) for r in recent]
        r_ucs = [r.get("ucs_distance", 0) for r in recent]
        r_astar_t = [r.get("astar_time_ms", 0) for r in recent]
        r_ucs_t = [r.get("ucs_time_ms", 0) for r in recent]

        return jsonify({
            "success": True,
            "total_routes": len(records),
            "total_feedback": len(feedback),
            "avg_astar_time": round(sum(astar_times)/len(astar_times), 2) if astar_times else 0,
            "avg_ucs_time": round(sum(ucs_times)/len(ucs_times), 2) if ucs_times else 0,
            "avg_astar_dist": round(sum(astar_dists)/len(astar_dists), 3) if astar_dists else 0,
            "avg_ucs_dist": round(sum(ucs_dists)/len(ucs_dists), 3) if ucs_dists else 0,
            "astar_wins": astar_wins,
            "ucs_wins": ucs_wins,
            "category_distribution": cat_counts,
            "rating_distribution": rating_dist,
            "avg_rating": round(sum(ratings)/len(ratings), 1) if ratings else 0,
            "comparison_labels": labels,
            "astar_distances": r_astar,
            "ucs_distances": r_ucs,
            "astar_times_ms": r_astar_t,
            "ucs_times_ms": r_ucs_t,
        })
    except Exception as e:
        logger.error(f"Analytics error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/graph_info", methods=["GET"])
def graph_info():
    """Return basic graph stats"""
    try:
        return jsonify({
            "nodes": len(G.nodes),
            "edges": len(G.edges),
            "city": "Amravati, Maharashtra, India",
            "crs": "EPSG:4326"
        })
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/api/sample_locations", methods=["GET"])
def sample_locations():
    """Return famous Amravati locations for quick selection"""
    locations = [
        {"name": "Amravati Bus Stand", "lat": 20.9320, "lng": 77.7523},
        {"name": "Amravati Railway Station", "lat": 20.9374, "lng": 77.7800},
        {"name": "Vidyut Nagar", "lat": 20.9185, "lng": 77.7620},
        {"name": "Rajkamal Chowk", "lat": 20.9320, "lng": 77.7540},
        {"name": "PRMA University", "lat": 20.9070, "lng": 77.7420},
        {"name": "Shri Shaktipeeth Ambadevi Temple", "lat": 20.9360, "lng": 77.7430},
        {"name": "Cotton Market", "lat": 20.9290, "lng": 77.7560},
        {"name": "Irwin Square", "lat": 20.9310, "lng": 77.7530},
        {"name": "Badnera Junction", "lat": 20.9160, "lng": 77.8100},
        {"name": "Paratwada Road", "lat": 20.9450, "lng": 77.7380},
        {"name": "Vilas Nagar", "lat": 20.9295, "lng": 77.7810},
        {"name": "Township Area", "lat": 20.9410, "lng": 77.7650},
        {"name": "Shivaji Nagar", "lat": 20.9250, "lng": 77.7650},
        {"name": "Gandhi Nagar", "lat": 20.9350, "lng": 77.7800},
        {"name": "Camp Area", "lat": 20.9480, "lng": 77.7700},
        {"name": "Collector Office", "lat": 20.9400, "lng": 77.7700},
        {"name": "Dastur Nagar", "lat": 20.9100, "lng": 77.7550},
        {"name": "Tapovan", "lat": 20.9200, "lng": 77.7750},
        {"name": "Chhatrapati Nagar", "lat": 20.9240, "lng": 77.7860},
        {"name": "Jaistambh Chowk", "lat": 20.9312, "lng": 77.7518},
        {"name": "Hanuman Nagar", "lat": 20.9420, "lng": 77.7580},
        {"name": "Nanded Road", "lat": 20.9380, "lng": 77.7900},
        {"name": "Sant Gadge Baba Amravati University", "lat": 20.9340, "lng": 77.7487},
        {"name": "Frazerpura", "lat": 20.9268, "lng": 77.7695},
    ]
    return jsonify({"success": True, "locations": locations})


# ─────────────────────────────────────────
# Run
# ─────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
