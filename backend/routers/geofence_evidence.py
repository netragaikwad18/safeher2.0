import os
import shutil
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User, SafeZone, IncidentEvidence, EmergencyAlert
from backend.security import get_current_user
from backend.config import settings

router = APIRouter(tags=["Geofencing & Evidence"])

class SafeZoneCreateSchema(BaseModel):
    zone_name: str
    latitude: float
    longitude: float
    radius_meters: Optional[int] = 200
    notify_on_exit: Optional[bool] = True
    notify_on_entry: Optional[bool] = False

@router.get("/api/geofence")
def get_safe_zones(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    zones = db.query(SafeZone).filter(SafeZone.user_id == current_user.id).all()
    return [
        {
            "id": z.id,
            "zone_name": z.zone_name,
            "latitude": z.latitude,
            "longitude": z.longitude,
            "radius_meters": z.radius_meters,
            "notify_on_exit": z.notify_on_exit,
            "notify_on_entry": z.notify_on_entry,
            "is_active": z.is_active,
            "created_at": z.created_at
        }
        for z in zones
    ]

@router.post("/api/geofence")
def create_safe_zone(data: SafeZoneCreateSchema, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    zone = SafeZone(
        user_id=current_user.id,
        zone_name=data.zone_name,
        latitude=data.latitude,
        longitude=data.longitude,
        radius_meters=data.radius_meters or 200,
        notify_on_exit=data.notify_on_exit,
        notify_on_entry=data.notify_on_entry,
        is_active=True
    )
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return {"message": "Safe zone created successfully", "id": zone.id, "zone_name": zone.zone_name}

@router.delete("/api/geofence/{zone_id}")
def delete_safe_zone(zone_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    zone = db.query(SafeZone).filter(SafeZone.id == zone_id, SafeZone.user_id == current_user.id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Safe zone not found")
    db.delete(zone)
    db.commit()
    return {"message": "Safe zone removed"}

@router.post("/api/evidence/upload")
async def upload_evidence(
    alert_id: int = Form(...),
    duration_seconds: int = Form(0),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    alert = db.query(EmergencyAlert).filter(
        EmergencyAlert.id == alert_id,
        EmergencyAlert.user_id == current_user.id
    ).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Emergency alert not found for this user")

    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    file_ext = os.path.splitext(file.filename)[1] or ".webm"
    safe_filename = f"evidence_user_{current_user.id}_alert_{alert_id}_{timestamp_str}{file_ext}"
    dest_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(dest_path)

    evidence = IncidentEvidence(
        alert_id=alert_id,
        user_id=current_user.id,
        file_type="AUDIO",
        file_path=dest_path,
        file_size_bytes=file_size,
        duration_seconds=duration_seconds,
        recorded_at=datetime.now(timezone.utc)
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    return {
        "message": "Emergency audio evidence uploaded and encrypted safely.",
        "evidence_id": evidence.id,
        "recorded_at": evidence.recorded_at,
        "duration_seconds": evidence.duration_seconds
    }

@router.get("/api/evidence")
def list_evidence(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = db.query(IncidentEvidence).filter(IncidentEvidence.user_id == current_user.id).order_by(IncidentEvidence.recorded_at.desc()).all()
    return [
        {
            "id": r.id,
            "alert_id": r.alert_id,
            "file_type": r.file_type,
            "file_size_bytes": r.file_size_bytes,
            "duration_seconds": r.duration_seconds,
            "recorded_at": r.recorded_at
        }
        for r in records
    ]

@router.delete("/api/evidence/{evidence_id}")
def delete_evidence(evidence_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rec = db.query(IncidentEvidence).filter(
        IncidentEvidence.id == evidence_id,
        IncidentEvidence.user_id == current_user.id
    ).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Evidence record not found")

    if os.path.exists(rec.file_path):
        try:
            os.remove(rec.file_path)
        except Exception:
            pass

    db.delete(rec)
    db.commit()
    return {"message": "Evidence deleted securely"}
