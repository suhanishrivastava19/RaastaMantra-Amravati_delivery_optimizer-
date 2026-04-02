"""
Cost Calculator for Delivery Route Optimization
────────────────────────────────────────────────
Calculates travel time and delivery cost based on:
- Distance (km)
- Category (delivery, urgent, normal)
- Vehicle speed assumptions
"""


class CostCalculator:
    """
    Calculates realistic travel time and cost estimates
    for the Amravati delivery system.
    """

    # Speed profiles (km/h) per category
    SPEED_PROFILES = {
        "delivery": 25,   # Delivery vehicle in city traffic
        "urgent":   40,   # Faster, priority routing
        "normal":   30,   # Normal journey
    }

    # Cost per km (INR) per category
    COST_PER_KM = {
        "delivery": 8.0,   # ₹8/km for delivery
        "urgent":   15.0,  # ₹15/km for urgent (premium)
        "normal":   5.0,   # ₹5/km for normal
    }

    # Base fare (INR)
    BASE_FARE = {
        "delivery": 20.0,
        "urgent":   50.0,
        "normal":   15.0,
    }

    def __init__(self, category: str = "normal"):
        self.category = category.lower()
        if self.category not in self.SPEED_PROFILES:
            self.category = "normal"

    def travel_time(self, distance_km: float) -> float:
        """
        Estimate travel time in minutes.
        Args:
            distance_km: Path distance in kilometers
        Returns:
            Travel time in minutes
        """
        speed = self.SPEED_PROFILES[self.category]
        hours = distance_km / speed
        return hours * 60  # minutes

    def delivery_cost(self, distance_km: float) -> float:
        """
        Calculate delivery cost in INR.
        Args:
            distance_km: Path distance in kilometers
        Returns:
            Cost in Indian Rupees
        """
        base = self.BASE_FARE[self.category]
        per_km = self.COST_PER_KM[self.category]
        return base + (per_km * distance_km)

    def fuel_cost(self, distance_km: float, fuel_price: float = 105.0) -> float:
        """
        Estimate fuel cost (assuming 15 km/litre for delivery vehicle).
        Args:
            distance_km: Distance in km
            fuel_price: Fuel price per litre in INR (default ₹105)
        Returns:
            Fuel cost in INR
        """
        mileage = 15.0  # km per litre
        litres = distance_km / mileage
        return litres * fuel_price

    def carbon_emission(self, distance_km: float) -> float:
        """
        Estimate CO2 emissions in grams.
        Assumes petrol vehicle: ~120g CO2/km
        """
        return distance_km * 120.0
