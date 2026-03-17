import pandas as pd
import numpy as np
import joblib
import os
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

os.makedirs('ml_models', exist_ok=True)

print("Starting Suitability Model Training...")
DISTRICTS_DATASET_PATH = os.environ.get(
    "DISTRICTS_DATASET_PATH",
    r"C:\Users\College\Desktop\JalNidhi_Extended_1M.xlsx",
)
df = pd.read_excel(DISTRICTS_DATASET_PATH)
df.columns = ["id", "district", "state", "pre_monsoon_depth", "post_monsoon_depth", "rainfall", "soil_suitability", "source"]

le = LabelEncoder()
df["soil_encoded"] = le.fit_transform(df["soil_suitability"])
features = df[["pre_monsoon_depth", "post_monsoon_depth", "rainfall", "soil_encoded"]]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(features)

kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df["cluster"] = kmeans.fit_predict(X_scaled)

joblib.dump(kmeans, "ml_models/suitability_model.pkl")
joblib.dump(scaler, "ml_models/scaler.pkl")
joblib.dump(le, "ml_models/encoder.pkl")
print("Suitability Model Saved.")

print("Starting Cost Prediction Model Training...")
COST_DATASET_PATH = os.environ.get(
    "COST_DATASET_PATH",
    r"C:\Users\College\Desktop\RWH.xlsx",
)
cost_df = pd.read_excel(COST_DATASET_PATH)
cost_df = cost_df.iloc[:, 1:7]
cost_df.columns = ["suitability", "rooftop_area", "rainfall", "tank_capacity", "runoff_coefficient", "cost"]

cost_encoder = LabelEncoder()
cost_df["suitability_encoded"] = cost_encoder.fit_transform(cost_df["suitability"])

X = cost_df[["suitability_encoded", "rooftop_area", "rainfall", "tank_capacity", "runoff_coefficient"]]
y = cost_df["cost"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

joblib.dump(model, "ml_models/cost_model.pkl")
joblib.dump(cost_encoder, "ml_models/cost_encoder.pkl")

predictions = model.predict(X_test)
print("Cost Model Saved.")
print("MAE:", mean_absolute_error(y_test, predictions))

import re

def extract_base_district(name):
    # Extract base district name from "adilabad - block a (10033)" → "adilabad"
    name = str(name).strip().lower()
    # Remove block codes and anything in brackets
    name = re.sub(r"\s*-\s*block\s+.*", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\s*\(.*?\)", "", name)
    return name.strip()

# Apply base district extraction to ALL rows including block rows
df["base_district"] = df["district"].apply(extract_base_district)

# Save valid districts (unique base names only)
district_list = df["base_district"].unique().tolist()
joblib.dump(district_list, "ml_models/valid_districts.pkl")
print(f"✅ Saved {len(district_list)} valid districts to ml_models/valid_districts.pkl")

# Save rainfall map (average of ALL rows including blocks per district)
rainfall_map = df.groupby("base_district")["rainfall"].mean().round(1).to_dict()
joblib.dump(rainfall_map, "ml_models/rainfall_map.pkl")
print(f"✅ Saved rainfall map for {len(rainfall_map)} districts")

print("All models successfully trained.")
