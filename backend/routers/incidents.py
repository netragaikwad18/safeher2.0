from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import IncidentReport, User
from backend.security import get_current_user_optional

router = APIRouter(prefix="/api/incidents", tags=["Incidents & Hotspots"])

class IncidentCreateSchema(BaseModel):
    title: str
    category: str
    severity: str
    latitude: float
    longitude: float
    location_name: str
    description: Optional[str] = None
    is_anonymous: Optional[bool] = False

@router.get("")
def list_incidents(
    category: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(IncidentReport)
    if category and category != "ALL":
        query = query.filter(IncidentReport.category == category)
    if severity and severity != "ALL":
        query = query.filter(IncidentReport.severity == severity)

    incidents = query.order_by(IncidentReport.reported_at.desc()).limit(limit).all()

    return [
        {
            "id": inc.id,
            "title": inc.title,
            "category": inc.category,
            "severity": inc.severity,
            "latitude": inc.latitude,
            "longitude": inc.longitude,
            "location_name": inc.location_name,
            "description": inc.description,
            "is_anonymous": inc.is_anonymous,
            "is_verified": inc.is_verified,
            "reported_at": inc.reported_at
        }
        for inc in incidents
    ]

@router.post("/report")
def report_incident(
    data: IncidentCreateSchema,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    user_id = None if data.is_anonymous or not current_user else current_user.id

    incident = IncidentReport(
        reported_by_user_id=user_id,
        title=data.title,
        category=data.category,
        severity=data.severity.upper(),
        latitude=data.latitude,
        longitude=data.longitude,
        location_name=data.location_name,
        description=data.description,
        is_anonymous=data.is_anonymous or False,
        is_verified=True,
        reported_at=datetime.now(timezone.utc)
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    return {
        "message": "Incident reported successfully. Thank you for helping keep the community safe.",
        "incident_id": incident.id,
        "is_anonymous": incident.is_anonymous
    }
