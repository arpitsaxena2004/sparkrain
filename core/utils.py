import joblib
import numpy as np
import os
from django.conf import settings

model_path = os.path.join(settings.BASE_DIR, "ml_models")

kmeans = None
scaler = None
suitability_encoder = None
cost_model = None
cost_encoder = None


def _load_models():
    """
    Lazy-load ML model artifacts.

    This avoids crashing the whole site on environments where the `ml_models/`
    artifacts haven't been generated yet (common on first deploy).
    """
    global kmeans, scaler, suitability_encoder, cost_model, cost_encoder

    if all(obj is not None for obj in [kmeans, scaler, suitability_encoder, cost_model, cost_encoder]):
        return

    required = [
        "suitability_model.pkl",
        "scaler.pkl",
        "encoder.pkl",
        "cost_model.pkl",
        "cost_encoder.pkl",
    ]
    missing = [name for name in required if not os.path.exists(os.path.join(model_path, name))]
    if missing:
        raise RuntimeError(
            "ML models are not available. Missing files in `ml_models/`: "
            + ", ".join(missing)
            + ". Run `python train_models.py` to generate them."
        )

    kmeans = joblib.load(os.path.join(model_path, "suitability_model.pkl"))
    scaler = joblib.load(os.path.join(model_path, "scaler.pkl"))
    suitability_encoder = joblib.load(os.path.join(model_path, "encoder.pkl"))
    cost_model = joblib.load(os.path.join(model_path, "cost_model.pkl"))
    cost_encoder = joblib.load(os.path.join(model_path, "cost_encoder.pkl"))


def predict_suitability(pre_depth, post_depth, rainfall, soil):
    """
    Predict site suitability using KMeans clustering.
    Raises ValueError if soil type is not in the encoder's known classes.
    """
    _load_models()
    known_soils = list(suitability_encoder.classes_)

    # ✅ FIX: raise instead of silently encoding unknown soil as 0
    if soil not in known_soils:
        raise ValueError(f"Unknown soil type '{soil}'. Expected one of: {known_soils}")

    soil_encoded = suitability_encoder.transform([soil])[0]

    features = np.array([[pre_depth, post_depth, rainfall, soil_encoded]])
    scaled   = scaler.transform(features)
    cluster  = kmeans.predict(scaled)[0]

    mapping = {
        0: "Very Low",
        1: "Low",
        2: "High",
        3: "Very High",
    }
    return mapping.get(int(cluster), "Moderate")


def predict_cost(suitability, area, rainfall, tank, runoff):
    """
    Predict installation cost using RandomForest.
    Raises ValueError if suitability label is not recognised by the encoder.
    """
    _load_models()
    known_labels = list(cost_encoder.classes_)

    # ✅ FIX: raise instead of silently encoding unknown suitability as 0
    if suitability not in known_labels:
        raise ValueError(f"Unknown suitability '{suitability}'. Expected one of: {known_labels}")

    suit_encoded = cost_encoder.transform([suitability])[0]

    features = [[suit_encoded, area, rainfall, tank, runoff]]
    cost     = cost_model.predict(features)[0]

    return round(float(cost), 2)
