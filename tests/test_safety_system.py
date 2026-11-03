import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal
from backend.models import User, IncidentReport
from backend.services.risk_engine import risk_engine
from backend.services.route_engine import recommend_routes

client = TestClient(app)

def test_health_check_routes():
    response = client.get("/")
    assert response.status_code == 200
    assert "WomenSafety AI" in response.text

def test_user_authentication_flow():
    res = client.post("/api/auth/login", json={
        "email": "pooja@example.com",
        "password": "Password123!"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "pooja@example.com"

    bad_res = client.post("/api/auth/login", json={
        "email": "pooja@example.com",
        "password": "WrongPassword!"
    })
    assert bad_res.status_code == 400

def test_emergency_contacts_api():
    login_res = client.post("/api/auth/login", json={
        "email": "pooja@example.com",
        "password": "Password123!"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/contacts", headers=headers)
    assert res.status_code == 200
    contacts = res.json()
    assert len(contacts) >= 1
    assert any(c["relationship"] == "Mother" for c in contacts)

def test_ai_risk_prediction_engine():
    db = SessionLocal()
    risk_res = risk_engine.evaluate_risk(
        db=db,
        latitude=12.9716,
        longitude=77.5946,
        hour=23,
        lighting_level=0,
        footfall_level=0,
        route_deviation=1
    )
    assert risk_res["risk_category"] in ("WARNING", "HIGH RISK")
    assert risk_res["risk_score"] > 40.0
    assert "model_synthetic_notice" in risk_res

    safe_res = risk_engine.evaluate_risk(
        db=db,
        latitude=12.9756,
        longitude=77.6050,
        hour=14,
        lighting_level=2,
        footfall_level=2,
        route_deviation=0
    )
    assert safe_res["risk_score"] <= 60.0
    db.close()

def test_dijkstra_safe_route_engine():
    db = SessionLocal()
    routes = recommend_routes(
        db=db,
        start_lat=12.9716,
        start_lon=77.5946,
        dest_lat=12.9352,
        dest_lon=77.6245
    )
    assert "recommended_safe_route" in routes
    assert "direct_route" in routes
    assert len(routes["recommended_safe_route"]["waypoints"]) >= 2
    assert routes["recommended_safe_route"]["safety_score"] > 0
    assert len(routes["nearby_emergency_services"]) > 0
    db.close()

def test_sos_trigger_and_resolve_flow():
    login_res = client.post("/api/auth/login", json={
        "email": "pooja@example.com",
        "password": "Password123!"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    sos_res = client.post("/api/sos/trigger", json={
        "latitude": 12.9716,
        "longitude": 77.5946,
        "alert_type": "SOS_BUTTON",
        "silent_mode": False,
        "battery_level": 88
    }, headers=headers)
    assert sos_res.status_code == 200
    sos_data = sos_res.json()
    assert sos_data["success"] is True
    alert_id = sos_data["alert_id"]
    tracking_token = sos_data["tracking_token"]

    track_res = client.get(f"/api/location/track/{tracking_token}")
    assert track_res.status_code == 200
    assert track_res.json()["status"] == "ACTIVE"

    resolve_res = client.post(f"/api/sos/{alert_id}/resolve", json={
        "emergency_pin": "4321",
        "resolution_notes": "User reached safe haven"
    }, headers=headers)
    assert resolve_res.status_code == 200
    assert resolve_res.json()["status"] == "RESOLVED"

def test_ai_chatbot_safety_queries():
    en_res = client.post("/api/chatbot/query", json={
        "message": "What is the emergency helpline number?",
        "language": "en"
    })
    assert en_res.status_code == 200
    assert "112" in en_res.json()["reply"]

    kn_res = client.post("/api/chatbot/query", json={
        "message": "ಸಹಾಯವಾಣಿ ಸಂಖ್ಯೆ ತಿಳಿಸಿ",
        "language": "kn"
    })
    assert kn_res.status_code == 200
    assert "112" in kn_res.json()["reply"]

def test_incident_hotspot_reporting():
    rep_res = client.post("/api/incidents/report", json={
        "title": "Streetlight failure test report",
        "category": "Poor Lighting",
        "severity": "MEDIUM",
        "latitude": 12.9730,
        "longitude": 77.5960,
        "location_name": "Richmond Road Corner",
        "description": "Dark corner reported.",
        "is_anonymous": True
    })
    assert rep_res.status_code == 200
    assert rep_res.json()["is_anonymous"] is True
