from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User, RiskPrediction
from backend.security import get_current_user_optional
from backend.services.risk_engine import risk_engine
from backend.services.route_engine import recommend_routes

router = APIRouter(prefix="/api/risk", tags=["AI Risk & Route Recommendation"])

class RiskPredictionRequest(BaseModel):
    latitude: float
    longitude: float
    hour: Optional[int] = None
    lighting_level: Optional[int] = 1
    footfall_level: Optional[int] = 1
    route_deviation: Optional[int] = 0
    movement_anomaly: Optional[int] = 0

class RouteRecommendationRequest(BaseModel):
    start_latitude: float
    start_longitude: float
    dest_latitude: float
    dest_longitude: float

@router.post("/predict")
def predict_safety_risk(
    data: RiskPredictionRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    evaluation = risk_engine.evaluate_risk(
        db=db,
        latitude=data.latitude,
        longitude=data.longitude,
        hour=data.hour,
        lighting_level=data.lighting_level,
        footfall_level=data.footfall_level,
        route_deviation=data.route_deviation,
        movement_anomaly=data.movement_anomaly
    )

    if current_user:
        prediction_record = RiskPrediction(
            user_id=current_user.id,
            latitude=data.latitude,
            longitude=data.longitude,
            time_of_day_hour=data.hour if data.hour is not None else datetime.now().hour,
            calculated_risk_score=evaluation["risk_score"],
            risk_category=evaluation["risk_category"],
            reason_warning=evaluation["reason_warning"],
            recommended_action=evaluation["recommended_action"],
            predicted_at=datetime.now(timezone.utc)
        )
        db.add(prediction_record)
        db.commit()

    return evaluation

@router.post("/routes/recommend")
def get_safe_route_recommendation(
    data: RouteRecommendationRequest,
    db: Session = Depends(get_db)
):
    return recommend_routes(
        db=db,
        start_lat=data.start_latitude,
        start_lon=data.start_longitude,
        dest_lat=data.dest_latitude,
        dest_lon=data.dest_longitude
    )
