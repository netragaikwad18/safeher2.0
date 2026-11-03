import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User, EmergencyAlert, LocationHistory, Notification, EmergencyContact
from backend.security import get_current_user
from backend.services.notifier import dispatch_emergency_sms, ws_manager

router = APIRouter(prefix="/api/sos", tags=["Emergency SOS"])

class SOSTriggerSchema(BaseModel):
    latitude: float
    longitude: float
    accuracy_meters: Optional[float] = 10.0
    alert_type: Optional[str] = "SOS_BUTTON"
    silent_mode: Optional[bool] = False
    battery_level: Optional[int] = 100
    network_status: Optional[str] = "ONLINE"
    address_description: Optional[str] = None

class SOSResolveSchema(BaseModel):
    emergency_pin: str
    resolution_notes: Optional[str] = "False alarm or user safe"

@router.post("/trigger")
async def trigger_sos(
    data: SOSTriggerSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    active_alert = db.query(EmergencyAlert).filter(
        EmergencyAlert.user_id == current_user.id,
        EmergencyAlert.status == "ACTIVE"
    ).first()

    tracking_token = str(uuid.uuid4())
    maps_url = f"https://www.google.com/maps?q={data.latitude},{data.longitude}"

    if not active_alert:
        alert = EmergencyAlert(
            user_id=current_user.id,
            alert_type=data.alert_type,
            latitude=data.latitude,
            longitude=data.longitude,
            accuracy_meters=data.accuracy_meters,
            address_description=data.address_description or "Emergency Alert Triggered",
            google_maps_url=maps_url,
            status="ACTIVE",
            silent_mode=data.silent_mode,
            battery_level=data.battery_level,
            network_status=data.network_status,
            tracking_token=tracking_token,
            created_at=datetime.now(timezone.utc)
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
    else:
        alert = active_alert
        alert.latitude = data.latitude
        alert.longitude = data.longitude
        alert.battery_level = data.battery_level
        alert.google_maps_url = maps_url

    loc_point = LocationHistory(
        user_id=current_user.id,
        alert_id=alert.id,
        latitude=data.latitude,
        longitude=data.longitude,
        battery_level=data.battery_level,
        recorded_at=datetime.now(timezone.utc)
    )
    db.add(loc_point)

    contacts = db.query(EmergencyContact).filter(EmergencyContact.user_id == current_user.id).all()
    notifications_dispatched = []

    msg_body = (
        f"EMERGENCY SOS ALERT! {current_user.full_name} needs immediate help! "
        f"Location: {maps_url} (Battery: {data.battery_level}%). "
        f"Live Tracking: /tracking.html?token={alert.tracking_token}"
    )

    for c in contacts:
        status_res = dispatch_emergency_sms(c.phone, c.name, msg_body)
        notif = Notification(
            alert_id=alert.id,
            recipient_phone=c.phone,
            recipient_name=c.name,
            message_body=msg_body,
            delivery_status=status_res,
            sent_at=datetime.now(timezone.utc)
        )
        db.add(notif)
        notifications_dispatched.append({
            "contact_name": c.name,
            "phone": c.phone,
            "status": status_res
        })

    db.commit()

    event_payload = {
        "event": "SOS_TRIGGERED",
        "alert_id": alert.id,
        "user_name": current_user.full_name,
        "phone": current_user.phone,
        "latitude": data.latitude,
        "longitude": data.longitude,
        "maps_url": maps_url,
        "alert_type": data.alert_type,
        "silent_mode": data.silent_mode,
        "battery_level": data.battery_level,
        "tracking_token": alert.tracking_token,
        "timestamp": str(alert.created_at)
    }
    await ws_manager.broadcast_global(event_payload)

    return {
        "success": True,
        "alert_id": alert.id,
        "tracking_token": alert.tracking_token,
        "status": alert.status,
        "google_maps_url": maps_url,
        "contacts_notified": len(notifications_dispatched),
        "notifications": notifications_dispatched
    }

@router.get("/active")
def get_active_alert(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    alert = db.query(EmergencyAlert).filter(
        EmergencyAlert.user_id == current_user.id,
        EmergencyAlert.status == "ACTIVE"
    ).order_by(EmergencyAlert.created_at.desc()).first()

    if not alert:
        return {"has_active_alert": False, "alert": None}

    return {
        "has_active_alert": True,
        "alert": {
            "id": alert.id,
            "alert_type": alert.alert_type,
            "latitude": alert.latitude,
            "longitude": alert.longitude,
            "google_maps_url": alert.google_maps_url,
            "tracking_token": alert.tracking_token,
            "silent_mode": alert.silent_mode,
            "battery_level": alert.battery_level,
            "created_at": alert.created_at
        }
    }

@router.post("/{alert_id}/resolve")
async def resolve_sos(
    alert_id: int,
    data: SOSResolveSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.emergency_pin != data.emergency_pin:
        raise HTTPException(status_code=400, detail="Invalid Emergency PIN. Cannot resolve alert.")

    alert = db.query(EmergencyAlert).filter(
        EmergencyAlert.id == alert_id,
        EmergencyAlert.user_id == current_user.id
    ).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")

    alert.status = "RESOLVED"
    alert.resolved_at = datetime.now(timezone.utc)
    alert.resolution_notes = data.resolution_notes
    db.commit()

    await ws_manager.broadcast_global({
        "event": "SOS_RESOLVED",
        "alert_id": alert.id,
        "user_id": current_user.id,
        "status": "RESOLVED"
    })

    return {"message": "Emergency alert marked as resolved successfully", "status": "RESOLVED"}

@router.post("/{alert_id}/cancel")
async def cancel_sos_countdown(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    alert = db.query(EmergencyAlert).filter(
        EmergencyAlert.id == alert_id,
        EmergencyAlert.user_id == current_user.id
    ).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")

    alert.status = "CANCELLED"
    alert.resolved_at = datetime.now(timezone.utc)
    alert.resolution_notes = "Cancelled by user during countdown"
    db.commit()

    return {"message": "Alert cancelled by user", "status": "CANCELLED"}
