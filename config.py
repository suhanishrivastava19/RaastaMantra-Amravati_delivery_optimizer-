import os
from dotenv import load_dotenv

load_dotenv()

# ─── Flask ────────────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "amravati-ai-route-2024-secret")
DEBUG      = os.getenv("DEBUG", "True").lower() == "true"

# ─── MongoDB ──────────────────────────────────────────────────────────────────
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME   = os.getenv("DB_NAME", "amravati_delivery")

# ─── OSMnx ────────────────────────────────────────────────────────────────────
CITY_NAME  = "Amravati, Maharashtra, India"
GRAPH_FILE = os.path.join(os.path.dirname(__file__), "data", "amravati_graph.graphml")

# ─── Cost per km (₹) & speed (km/h) ──────────────────────────────────────────
VEHICLE_PROFILES = {
    "delivery": {"cost_per_km": 8,  "speed_kmh": 25, "label": "Delivery Van"},
    "urgent":   {"cost_per_km": 15, "speed_kmh": 40, "label": "Urgent Courier"},
    "normal":   {"cost_per_km": 5,  "speed_kmh": 30, "label": "Normal Journey"},
}
