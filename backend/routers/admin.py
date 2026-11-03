from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend.models import User, AdminUser, EmergencyAlert, IncidentReport, Notification
from backend.security import get_current_admin

router = APIRouter(prefix="/api/admin", tags=["Admin Dashboard"])

@router.get("/metrics")
def get_system_metrics(
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    total_users = db.query(User).count()
    total_alerts = db.query(EmergencyAlert).count()
    active_alerts = db.query(EmergencyAlert).filter(EmergencyAlert.status == "ACTIVE").count()
    resolved_alerts = db.query(EmergencyAlert).filter(EmergencyAlert.status == "RESOLVED").count()
    total_incidents = db.query(IncidentReport).count()
    total_notifications = db.query(Notification).count()

    severity_counts = db.query(
        IncidentReport.severity,
        func.count(IncidentReport.id)
    ).group_by(IncidentReport.severity).all()

    category_counts = db.query(
        IncidentReport.category,
        func.count(IncidentReport.id)
    ).group_by(IncidentReport.category).all()

    return {
        "total_registered_users": total_users,
        "total_emergency_alerts": total_alerts,
        "active_emergencies": active_alerts,
        "resolved_emergencies": resolved_alerts,
        "total_incidents_reported": total_incidents,
        "total_notifications_dispatched": total_notifications,
        "incidents_by_severity": {s: count for s, count in severity_counts},
        "incidents_by_category": {c: count for c, count in category_counts}
    }

@router.get("/alerts")
def get_admin_alerts(
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    alerts = db.query(EmergencyAlert).order_by(EmergencyAlert.created_at.desc()).limit(100).all()
    return [
        {
            "id": a.id,
            "user_id": a.user_id,
            "user_name": a.user.full_name if a.user else "Anonymous",
            "user_phone": a.user.phone if a.user else "N/A",
            "alert_type": a.alert_type,
            "latitude": a.latitude,
            "longitude": a.longitude,
            "status": a.status,
            "silent_mode": a.silent_mode,
            "battery_level": a.battery_level,
            "google_maps_url": a.google_maps_url,
            "tracking_token": a.tracking_token,
            "created_at": a.created_at,
            "resolved_at": a.resolved_at
        }
        for a in alerts
    ]

@router.get("/users")
def get_admin_users(
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    users = db.query(User).order_by(User.created_at.desc()).limit(100).all()
    return [
        {
            "id": u.id,
            "full_name": u.full_name,
            "email": u.email,
            "phone": u.phone,
            "blood_group": u.blood_group,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at
        }
        for u in users
    ]
