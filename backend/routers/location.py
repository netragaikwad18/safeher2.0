from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User, LocationHistory, EmergencyAlert, SafeZone
from backend.security import get_current_user
from backend.services.notifier import ws_manager
from backend.services.risk_engine import haversine_distance

router = APIRouter(prefix="/api/location", tags=["Location & GPS Tracking"])

class LocationUpdateSchema(BaseModel):
    latitude: float
    longitude: float
    speed: Optional[float] = 0.0
    heading: Optional[float] = 0.0
    battery_level: Optional[int] = 100
    is_offline_sync: Optional[bool] = False

@router.post("/update")
async def update_location(
    data: LocationUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    active_alert = db.query(EmergencyAlert).filter(
        EmergencyAlert.user_id == current_user.id,
        EmergencyAlert.status == "ACTIVE"
    ).first()

    loc = LocationHistory(
        user_id=current_user.id,
        alert_id=active_alert.id if active_alert else None,
        latitude=data.latitude,
        longitude=data.longitude,
        speed=data.speed,
        heading=data.heading,
        battery_level=data.battery_level,
        is_offline_sync=data.is_offline_sync,
        recorded_at=datetime.now(timezone.utc)
    )
    db.add(loc)

    safe_zones = db.query(SafeZone).filter(
        SafeZone.user_id == current_user.id,
        SafeZone.is_active == True
    ).all()

    geofence_events = []
    for zone in safe_zones:
        dist = haversine_distance(data.latitude, data.longitude, zone.latitude, zone.longitude)
        is_inside = dist <= zone.radius_meters
        if not is_inside and zone.notify_on_exit:
            geofence_events.append({
                "zone_name": zone.zone_name,
                "event": "EXIT_SAFE_ZONE",
                "distance_meters": round(dist, 1)
            })
        elif is_inside and zone.notify_on_entry:
            geofence_events.append({
                "zone_name": zone.zone_name,
                "event": "ENTER_SAFE_ZONE",
                "distance_meters": round(dist, 1)
            })

    db.commit()

    if active_alert:
        await ws_manager.broadcast_to_channel(
            active_alert.tracking_token,
            {
                "event": "LIVE_GPS_UPDATE",
                "alert_id": active_alert.id,
                "latitude": data.latitude,
                "longitude": data.longitude,
                "battery_level": data.battery_level,
                "speed": data.speed,
                "timestamp": str(loc.recorded_at)
            }
        )

    return {
        "status": "Location recorded",
        "has_active_alert": active_alert is not None,
        "geofence_events": geofence_events
    }

@router.get("/track/{tracking_token}")
def track_emergency_location(
    tracking_token: str,
    db: Session = Depends(get_db)
):
    alert = db.query(EmergencyAlert).filter(EmergencyAlert.tracking_token == tracking_token).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Live tracking link invalid or expired.")

    breadcrumbs = db.query(LocationHistory).filter(
        LocationHistory.user_id == alert.user_id
    ).order_by(LocationHistory.recorded_at.desc()).limit(30).all()

    breadcrumbs_data = [
        {
            "latitude": b.latitude,
            "longitude": b.longitude,
            "speed": b.speed,
            "battery_level": b.battery_level,
            "recorded_at": b.recorded_at
        }
        for b in reversed(breadcrumbs)
    ]

    return {
        "alert_id": alert.id,
        "user_name": alert.user.full_name,
        "user_phone": alert.user.phone,
        "blood_group": alert.user.blood_group,
        "status": alert.status,
        "alert_type": alert.alert_type,
        "current_latitude": alert.latitude,
        "current_longitude": alert.longitude,
        "battery_level": alert.battery_level,
        "network_status": alert.network_status,
        "created_at": alert.created_at,
        "resolved_at": alert.resolved_at,
        "breadcrumbs": breadcrumbs_data
    }

@router.get("/history")
def get_user_location_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    points = db.query(LocationHistory).filter(
        LocationHistory.user_id == current_user.id
    ).order_by(LocationHistory.recorded_at.desc()).limit(50).all()

    return [
        {
            "id": p.id,
            "latitude": p.latitude,
            "longitude": p.longitude,
            "speed": p.speed,
            "battery_level": p.battery_level,
            "recorded_at": p.recorded_at
        }
        for p in points
    ]
