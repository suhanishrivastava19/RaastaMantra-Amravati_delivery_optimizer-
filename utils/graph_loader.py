"""
Graph Loader — Amravati, Maharashtra Road Network
────────────────────────────────────────────────
Uses OSMnx to download or load cached Amravati road network.
Falls back to a synthetic graph if OSMnx/internet not available.
"""

import os
import json
import math
import logging
import networkx as nx
from typing import Optional, List, Tuple

logger = logging.getLogger(__name__)

# Cache file path
CACHE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "amravati_graph.graphml")

# Amravati city center
AMRAVATI_CENTER = (20.9374, 77.7796)  # lat, lng
AMRAVATI_BBOX = {
    "north": 20.980,
    "south": 20.890,
    "east": 77.840,
    "west": 77.720
}


class GraphLoader:
    """
    Loads and manages the Amravati road network graph.
    Tries OSMnx first, then cached GraphML, then synthetic fallback.
    """

    def __init__(self):
        self.G: Optional[nx.MultiDiGraph] = None
        self.node_coords = {}  # node_id -> (lat, lng)

    def load_graph(self) -> nx.MultiDiGraph:
        """Load graph — uses built-in synthetic Amravati graph (no internet needed)"""
        logger.info("✅ Loading built-in Amravati graph (offline mode)")
        self.G = self._create_synthetic_graph()
        self._build_node_coords()
        logger.info(f"✅ Graph ready: {len(self.G.nodes)} nodes, {len(self.G.edges)} edges")
        return self.G

    def _load_from_osmnx(self) -> nx.MultiDiGraph:
        """Download Amravati road network using OSMnx"""
        import osmnx as ox
        ox.settings.log_console = False
        ox.settings.use_cache = True

        G = ox.graph_from_place(
            "Amravati, Maharashtra, India",
            network_type="drive",
            simplify=True
        )
        # Add speed and travel time data
        G = ox.add_edge_speeds(G)
        G = ox.add_edge_travel_times(G)
        return G

    def _load_from_cache(self) -> nx.MultiDiGraph:
        """Load graph from saved GraphML file"""
        import osmnx as ox
        return ox.load_graphml(CACHE_PATH)

    def _save_cache(self):
        """Save graph to cache for future use"""
        try:
            import osmnx as ox
            os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
            ox.save_graphml(self.G, CACHE_PATH)
            logger.info("Graph cached successfully")
        except Exception as e:
            logger.warning(f"Cache save failed: {e}")

    def _create_synthetic_graph(self) -> nx.MultiDiGraph:
        """
        Create a realistic synthetic road network for Amravati.
        Based on actual layout of major roads and landmarks.
        """
        G = nx.MultiDiGraph()
        G.graph["crs"] = "epsg:4326"

        # Real-ish Amravati locations as nodes
        nodes = {
            1:  {"y": 20.9374, "x": 77.7796, "name": "Railway Station"},
            2:  {"y": 20.9320, "x": 77.7523, "name": "Bus Stand"},
            3:  {"y": 20.9360, "x": 77.7430, "name": "Ambadevi Temple"},
            4:  {"y": 20.9310, "x": 77.7530, "name": "Irwin Square"},
            5:  {"y": 20.9290, "x": 77.7560, "name": "Cotton Market"},
            6:  {"y": 20.9185, "x": 77.7620, "name": "Vidyut Nagar"},
            7:  {"y": 20.9070, "x": 77.7420, "name": "PRMA University"},
            8:  {"y": 20.9160, "x": 77.8100, "name": "Badnera Junction"},
            9:  {"y": 20.9450, "x": 77.7380, "name": "Paratwada Road"},
            10: {"y": 20.9400, "x": 77.7700, "name": "Collector Office"},
            11: {"y": 20.9250, "x": 77.7650, "name": "Shivaji Nagar"},
            12: {"y": 20.9350, "x": 77.7800, "name": "Gandhi Nagar"},
            13: {"y": 20.9280, "x": 77.7480, "name": "Old Town"},
            14: {"y": 20.9420, "x": 77.7580, "name": "New Hanuman Nagar"},
            15: {"y": 20.9200, "x": 77.7750, "name": "Tapovan"},
            16: {"y": 20.9480, "x": 77.7700, "name": "Camp Area"},
            17: {"y": 20.9330, "x": 77.7680, "name": "Rajkamal Chowk"},
            18: {"y": 20.9100, "x": 77.7550, "name": "Dastur Nagar"},
            19: {"y": 20.9380, "x": 77.7900, "name": "Nanded Road"},
            20: {"y": 20.9240, "x": 77.7860, "name": "Chhatrapati Nagar"},
        }

        for nid, data in nodes.items():
            G.add_node(nid, **data)

        # Edges (bidirectional roads with realistic distances in meters)
        edges = [
            (1, 12, 600), (12, 2, 1200), (2, 4, 300),
            (4, 3, 800), (4, 5, 400), (5, 6, 900),
            (6, 7, 1800), (2, 13, 500), (13, 3, 700),
            (4, 17, 350), (17, 12, 450), (17, 11, 600),
            (11, 15, 700), (15, 8, 3200), (1, 8, 2500),
            (8, 20, 1800), (20, 15, 900), (12, 10, 800),
            (10, 16, 700), (16, 9, 1200), (9, 3, 1100),
            (14, 16, 900), (14, 10, 600), (1, 19, 800),
            (19, 8, 1500), (6, 18, 1000), (18, 7, 1200),
            (5, 11, 700), (13, 18, 1400), (7, 13, 2000),
        ]

        for u, v, length in edges:
            # Add bidirectional edges with realistic attributes
            speed_kmh = 30  # average urban speed
            travel_time = (length / 1000) / speed_kmh * 3600  # seconds
            G.add_edge(u, v, key=0, length=float(length),
                       speed_kph=speed_kmh, travel_time=travel_time)
            G.add_edge(v, u, key=0, length=float(length),
                       speed_kph=speed_kmh, travel_time=travel_time)

        return G

    def _build_node_coords(self):
        """Pre-build node → (lat, lng) lookup"""
        self.node_coords = {}
        for node, data in self.G.nodes(data=True):
            lat = data.get("y", 0)
            lng = data.get("x", 0)
            self.node_coords[node] = (lat, lng)

    def nearest_node(self, lat: float, lng: float) -> Optional[int]:
        """
        Find the nearest graph node to a given lat/lng coordinate.
        Uses Haversine distance for accuracy.
        """
        if not self.node_coords:
            return None

        min_dist = float("inf")
        nearest = None

        for node, (n_lat, n_lng) in self.node_coords.items():
            dist = self._haversine(lat, lng, n_lat, n_lng)
            if dist < min_dist:
                min_dist = dist
                nearest = node

        return nearest

    def path_to_coords(self, path: List[int]) -> List[List[float]]:
        """Convert list of node IDs to list of [lat, lng] coordinates"""
        coords = []
        for node in path:
            if node in self.node_coords:
                lat, lng = self.node_coords[node]
                coords.append([lat, lng])
        return coords

    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Haversine distance in km"""
        R = 6371
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        return 2*R*math.asin(math.sqrt(a))
