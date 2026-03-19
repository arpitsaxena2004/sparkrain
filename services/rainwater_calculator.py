import joblib
import numpy as np
import os
import re
from difflib import get_close_matches

# ✅ Load valid districts once at import time
BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml_models')

try:
    VALID_DISTRICTS = set(joblib.load(os.path.join(BASE, 'valid_districts.pkl')))
except Exception:
    VALID_DISTRICTS = set()  # fallback if pkl not found
    print("Warning: valid_districts.pkl not found. Run train_models.py first.")

def extract_base_district(name):
    name = str(name).strip().lower()
    name = re.sub(r"\s*-\s*block\s+.*", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\s*\(.*?\)", "", name)
    return name.strip()

# Load district -> rainfall mapping (created by train_models.py)
try:
    RAINFALL_MAP = joblib.load(os.path.join(BASE, 'rainfall_map.pkl'))
    print("Loaded rainfall map.")
except Exception:
    RAINFALL_MAP = {}
    print("Warning: rainfall_map.pkl not found - run train_models.py first.")


def get_district_rainfall(city: str):
    """Returns average annual rainfall for a district from training data."""
    city_clean = extract_base_district(city)
    return RAINFALL_MAP.get(city_clean, None)

# Load ML models lazily
suitability_model = None
scaler = None
encoder = None
cost_model = None
cost_encoder = None

def _load_ml_models():
    """Lazy load heavy ML models to save RAM globally."""
    global suitability_model, scaler, encoder, cost_model, cost_encoder
    if cost_model is not None:
        return
    try:
        suitability_model = joblib.load(os.path.join(BASE, 'suitability_model.pkl'))
        scaler            = joblib.load(os.path.join(BASE, 'scaler.pkl'))
        encoder           = joblib.load(os.path.join(BASE, 'encoder.pkl'))
        cost_model        = joblib.load(os.path.join(BASE, 'cost_model.pkl'))
        cost_encoder      = joblib.load(os.path.join(BASE, 'cost_encoder.pkl'))
    except Exception as e:
        print(f"Warning: model load error: {e}")


def validate_district(city: str):
    """
    Returns (is_valid, suggestion_or_none)
    e.g. ("agra", True, None)  or  ("narnia", False, None)
    or   ("lucknw", False, "lucknow")  <- fuzzy suggestion
    """
    city_clean = extract_base_district(city)

    if city_clean in VALID_DISTRICTS:
        return True, None  # exact match ✅

    # Try fuzzy match for typos (e.g. "lucknw" → "lucknow")
    close = get_close_matches(city_clean, list(VALID_DISTRICTS), n=1, cutoff=0.75)
    if close:
        return False, close[0]  # typo — suggest correction

    return False, None  # completely invalid city

def validate_inputs(rooftop_area, tank_capacity):
    """Validate numeric ranges. Returns error string or None."""
    if not (1 <= rooftop_area <= 50000):
        return "Rooftop area must be between 1 and 50,000 sq meters."
    if not (500 <= tank_capacity <= 1000000):
        return "Tank capacity must be between 500 and 10,00,000 liters."
    return None  # all valid ✅


def calculate_water(area, rainfall, runoff=0.8):
    """Calculate captured water in liters."""
    water = area * rainfall * runoff
    return round(water, 2)


def predict_suitability_and_cost(soil_type, rainfall, rooftop_area, tank_capacity, runoff=0.85):
    """
    Run both ML models and return results dict.
    Call only AFTER validate_district and validate_inputs pass.
    """
    _load_ml_models()
    
    # Suitability model
    soil_encoded = encoder.transform([soil_type])[0]
    pre_monsoon_depth  = 5.0   # default — add as form field later if needed
    post_monsoon_depth = 3.0

    features = np.array([[pre_monsoon_depth, post_monsoon_depth, rainfall, soil_encoded]])
    features_scaled = scaler.transform(features)
    cluster = suitability_model.predict(features_scaled)[0]

    suitability_map = {0: 'High', 1: 'Medium', 2: 'Low', 3: 'Very Low'}
    suitability = suitability_map.get(int(cluster), 'Medium')

    # Cost model
    suitability_encoded = cost_encoder.transform([suitability])[0]
    cost_features = np.array([[suitability_encoded, rooftop_area, rainfall, tank_capacity, runoff]])
    predicted_cost = cost_model.predict(cost_features)[0]

    # Water potential
    water_liters = calculate_water(rooftop_area, rainfall, runoff)

    return {
        "suitability": suitability,
        "predicted_cost": round(float(predicted_cost), 2),
        "water_potential_liters": water_liters,
    }

