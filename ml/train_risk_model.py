"""
Synthetic Risk Dataset Generator and Model Trainer for Smart Women Safety System.
NOTE: In accordance with project requirements, this uses synthetic training data clearly
distinguished from real incident data. The model does not guarantee personal safety.
"""
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def generate_synthetic_risk_data(n_samples=2500, random_state=42):
    np.random.seed(random_state)

    hours = np.random.randint(0, 24, size=n_samples)
    incident_distance = np.random.exponential(scale=600, size=n_samples)
    incident_distance = np.clip(incident_distance, 10, 3500)
    incident_density = np.random.poisson(lam=2.5, size=n_samples)
    lighting = np.random.choice([0, 1, 2], size=n_samples, p=[0.25, 0.35, 0.40])
    footfall = np.random.choice([0, 1, 2], size=n_samples, p=[0.30, 0.40, 0.30])
    route_deviation = np.random.choice([0, 1], size=n_samples, p=[0.85, 0.15])
    movement_anomaly = np.random.choice([0, 1], size=n_samples, p=[0.88, 0.12])

    is_late_night = ((hours >= 22) | (hours <= 5)).astype(int)
    is_evening = ((hours >= 19) & (hours < 22)).astype(int)

    base_score = 15.0
    time_penalty = is_late_night * 28.0 + is_evening * 14.0
    dist_penalty = np.clip((1500 - incident_distance) / 25.0, 0, 30.0)
    density_penalty = np.clip(incident_density * 3.5, 0, 20.0)
    lighting_penalty = (2 - lighting) * 9.0
    footfall_penalty = (2 - footfall) * 8.0
    deviation_penalty = route_deviation * 16.0
    movement_penalty = movement_anomaly * 14.0
    noise = np.random.normal(0, 3.0, size=n_samples)

    raw_score = (base_score + time_penalty + dist_penalty + density_penalty +
                 lighting_penalty + footfall_penalty + deviation_penalty +
                 movement_penalty + noise)
    risk_score = np.clip(raw_score, 0.0, 100.0)

    labels = np.zeros(n_samples, dtype=int)
    labels[risk_score >= 40.0] = 1
    labels[risk_score >= 70.0] = 2

    df = pd.DataFrame({
        "hour": hours,
        "incident_distance_m": incident_distance,
        "incident_density_1km": incident_density,
        "lighting_level": lighting,
        "footfall_level": footfall,
        "route_deviation": route_deviation,
        "movement_anomaly": movement_anomaly,
        "risk_score": risk_score,
        "risk_class": labels
    })
    return df

def train_and_export_model():
    df = generate_synthetic_risk_data(n_samples=3000)
    features = [
        "hour",
        "incident_distance_m",
        "incident_density_1km",
        "lighting_level",
        "footfall_level",
        "route_deviation",
        "movement_anomaly"
    ]
    X = df[features]
    y = df["risk_class"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        min_samples_split=4,
        random_state=42
    )
    model.fit(X_train, y_train)

    os.makedirs("./ml", exist_ok=True)
    joblib_path = "./ml/risk_model.joblib"
    joblib.dump({"model": model, "feature_names": features, "is_synthetic": True}, joblib_path)
    df.head(100).to_csv("./ml/synthetic_risk_sample.csv", index=False)

if __name__ == "__main__":
    train_and_export_model()
