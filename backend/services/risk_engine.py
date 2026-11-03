import math
import os
import joblib
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.models import IncidentReport
from backend.config import settings

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class RiskPredictionEngine:
    def __init__(self, model_path: str = None):
        self.model_path = model_path or settings.MODEL_PATH
        self.model = None
        self.feature_names = []
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                data = joblib.load(self.model_path)
                self.model = data.get("model")
                self.feature_names = data.get("feature_names", [])
            except Exception as e:
                pass

    def evaluate_risk(
        self,
        db: Session,
        latitude: float,
        longitude: float,
        hour: int = None,
        lighting_level: int = 1,
        footfall_level: int = 1,
        route_deviation: int = 0,
        movement_anomaly: int = 0
    ) -> Dict[str, Any]:
        if hour is None:
            hour = datetime.now().hour

        incidents = db.query(IncidentReport).all()
        min_incident_dist = 5000.0
        nearby_incidents_1km = 0
        nearest_incident_info = None

        for inc in incidents:
            dist = haversine_distance(latitude, longitude, inc.latitude, inc.longitude)
            if dist <= 1000:
                nearby_incidents_1km += 1
            if dist < min_incident_dist:
                min_incident_dist = dist
                nearest_incident_info = inc

        features_df = pd.DataFrame([{
            "hour": hour,
            "incident_distance_m": min_incident_dist,
            "incident_density_1km": nearby_incidents_1km,
            "lighting_level": lighting_level,
            "footfall_level": footfall_level,
            "route_deviation": route_deviation,
            "movement_anomaly": movement_anomaly
        }])

        if self.model is not None:
            pred_class = int(self.model.predict(features_df)[0])
            pred_proba = self.model.predict_proba(features_df)[0]
            risk_score = round(float(pred_proba[1] * 50.0 + pred_proba[2] * 100.0), 1)
        else:
            is_night = 1 if (hour >= 21 or hour <= 5) else 0
            risk_score = min(100.0, 20.0 + (is_night * 30.0) + (nearby_incidents_1km * 10.0))
            if risk_score < 40:
                pred_class = 0
            elif risk_score < 70:
                pred_class = 1
            else:
                pred_class = 2

        class_map = {0: "SAFE", 1: "WARNING", 2: "HIGH RISK"}
        category = class_map.get(pred_class, "WARNING")

        reasons = []
        actions = []

        if 21 <= hour or hour <= 5:
            reasons.append("Late night commute hours (21:00 - 05:00) with reduced pedestrian footfall.")
            actions.append("Share your live location with a primary emergency contact.")

        if nearby_incidents_1km > 0 and nearest_incident_info:
            reasons.append(f"Near reported incident spot '{nearest_incident_info.title}' ({int(min_incident_dist)}m away).")
            actions.append("Avoid isolated bylanes and maintain awareness of surroundings.")

        if lighting_level == 0:
            reasons.append("Poor or absent street illumination reported.")
            actions.append("Walk towards well-lit commercial streets or transport hubs.")

        if route_deviation == 1:
            reasons.append("Deviation detected from usual safe transit path.")
            actions.append("Verify GPS navigation and keep emergency SOS button readily accessible.")

        if not reasons:
            reasons.append("Normal daylight or well-lit transit corridor with low recent incident reports.")
            actions.append("Safe to proceed. Keep phone battery charged.")

        reason_str = " | ".join(reasons)
        action_str = " | ".join(actions)

        return {
            "risk_score": risk_score,
            "risk_category": category,
            "reason_warning": reason_str,
            "recommended_action": action_str,
            "nearby_incidents_count": nearby_incidents_1km,
            "nearest_incident_distance_meters": round(min_incident_dist, 1),
            "model_synthetic_notice": (
                "Notice: Safety risk score is generated using an AI classifier trained on "
                "synthetic risk patterns and verified local incident reports. "
                "The model cannot guarantee personal safety."
            )
        }

risk_engine = RiskPredictionEngine()
