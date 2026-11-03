from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Boolean, Float, Text, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship
from backend.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    emergency_pin = Column(String(10), default="1234")
    blood_group = Column(String(10), default="O+")
    medical_notes = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    role = Column(String(20), default="user")
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    contacts = relationship("EmergencyContact", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("EmergencyAlert", back_populates="user", cascade="all, delete-orphan")
    locations = relationship("LocationHistory", back_populates="user", cascade="all, delete-orphan")
    safe_zones = relationship("SafeZone", back_populates="user", cascade="all, delete-orphan")
    evidence = relationship("IncidentEvidence", back_populates="user", cascade="all, delete-orphan")

class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    badge_number = Column(String(50), nullable=True)
    department = Column(String(100), default="Emergency Response & Safety Cell")
    is_superadmin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)

class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    relationship_type = Column("relationship", String(50), nullable=False)
    is_primary = Column(Boolean, default=False)
    email = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="contacts")

class EmergencyAlert(Base):
    __tablename__ = "emergency_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    alert_type = Column(String(50), default="SOS_BUTTON")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    accuracy_meters = Column(Float, default=10.0)
    address_description = Column(Text, nullable=True)
    google_maps_url = Column(Text, nullable=False)
    status = Column(String(30), default="ACTIVE", index=True)
    silent_mode = Column(Boolean, default=False)
    battery_level = Column(Integer, default=100)
    network_status = Column(String(20), default="ONLINE")
    tracking_token = Column(String(64), unique=True, index=True)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    resolved_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="alerts")
    locations = relationship("LocationHistory", back_populates="alert")
    notifications = relationship("Notification", back_populates="alert", cascade="all, delete-orphan")
    evidence = relationship("IncidentEvidence", back_populates="alert", cascade="all, delete-orphan")

class LocationHistory(Base):
    __tablename__ = "location_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    alert_id = Column(Integer, ForeignKey("emergency_alerts.id", ondelete="SET NULL"), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed = Column(Float, default=0.0)
    heading = Column(Float, default=0.0)
    battery_level = Column(Integer, default=100)
    is_offline_sync = Column(Boolean, default=False)
    recorded_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="locations")
    alert = relationship("EmergencyAlert", back_populates="locations")

class IncidentReport(Base):
    __tablename__ = "incident_reports"

    id = Column(Integer, primary_key=True, index=True)
    reported_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(150), nullable=False)
    category = Column(String(60), nullable=False)
    severity = Column(String(20), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    is_anonymous = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=True)
    reported_at = Column(DateTime, default=utc_now)

class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    time_of_day_hour = Column(Integer, nullable=False)
    calculated_risk_score = Column(Float, nullable=False)
    risk_category = Column(String(20), nullable=False)
    reason_warning = Column(Text, nullable=False)
    recommended_action = Column(Text, nullable=False)
    predicted_at = Column(DateTime, default=utc_now)

class SafeZone(Base):
    __tablename__ = "safe_zones"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    zone_name = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius_meters = Column(Integer, default=200)
    notify_on_exit = Column(Boolean, default=True)
    notify_on_entry = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="safe_zones")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("emergency_alerts.id", ondelete="CASCADE"), nullable=True)
    recipient_phone = Column(String(20), nullable=False)
    recipient_name = Column(String(100), nullable=False)
    message_body = Column(Text, nullable=False)
    channel = Column(String(20), default="SMS")
    delivery_status = Column(String(20), default="SENT")
    sent_at = Column(DateTime, default=utc_now)

    alert = relationship("EmergencyAlert", back_populates="notifications")

class IncidentEvidence(Base):
    __tablename__ = "incident_evidence"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("emergency_alerts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_type = Column(String(20), default="AUDIO")
    file_path = Column(String(255), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    duration_seconds = Column(Integer, default=0)
    recorded_at = Column(DateTime, default=utc_now)

    alert = relationship("EmergencyAlert", back_populates="evidence")
    user = relationship("User", back_populates="evidence")
