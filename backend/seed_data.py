from backend.database import SessionLocal, engine, Base
from backend.models import User, AdminUser, EmergencyContact, IncidentReport, SafeZone
from backend.security import get_password_hash

def init_and_seed_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if db.query(User).count() == 0:
            demo_user = User(
                full_name="Pooja Sharma",
                email="pooja@example.com",
                phone="+919876543210",
                password_hash=get_password_hash("Password123!"),
                emergency_pin="4321",
                blood_group="B+",
                medical_notes="Asthma inhaler in purse. Allergic to penicillin.",
                address="Brigade Road, Bengaluru, Karnataka 560025",
                role="user"
            )
            admin_user_account = User(
                full_name="Dr. Anita Roy (Safety Admin)",
                email="admin@example.com",
                phone="+919876500000",
                password_hash=get_password_hash("AdminPass123!"),
                emergency_pin="9999",
                role="admin"
            )
            db.add(demo_user)
            db.add(admin_user_account)
            db.commit()
            db.refresh(demo_user)

            admin_cell = AdminUser(
                username="safety_admin",
                email="admin@example.com",
                password_hash=get_password_hash("AdminPass123!"),
                badge_number="KA-BLR-POL-4412",
                department="Women & Child Safety Rapid Response Cell",
                is_superadmin=True
            )
            db.add(admin_cell)

            contacts = [
                EmergencyContact(
                    user_id=demo_user.id,
                    name="Radha Sharma (Mother)",
                    phone="+919876501234",
                    relationship_type="Mother",
                    is_primary=True,
                    email="radha.sharma@example.com"
                ),
                EmergencyContact(
                    user_id=demo_user.id,
                    name="Vikram Sharma (Father)",
                    phone="+919876505678",
                    relationship_type="Father",
                    is_primary=False,
                    email="vikram.sharma@example.com"
                ),
                EmergencyContact(
                    user_id=demo_user.id,
                    name="Sneha Verma (Friend)",
                    phone="+919876509999",
                    relationship_type="Friend",
                    is_primary=False,
                    email="sneha.v@example.com"
                )
            ]
            db.add_all(contacts)

            safe_zones = [
                SafeZone(
                    user_id=demo_user.id,
                    zone_name="Home (Brigade Road)",
                    latitude=12.971598,
                    longitude=77.594562,
                    radius_meters=300,
                    notify_on_exit=True,
                    notify_on_entry=True
                ),
                SafeZone(
                    user_id=demo_user.id,
                    zone_name="College Campus (MG Road)",
                    latitude=12.975600,
                    longitude=77.605000,
                    radius_meters=500,
                    notify_on_exit=True,
                    notify_on_entry=False
                )
            ]
            db.add_all(safe_zones)

        if db.query(IncidentReport).count() == 0:
            incidents = [
                IncidentReport(
                    title="Poor Street Lighting & Deserted Alley",
                    category="Poor Lighting",
                    severity="HIGH",
                    latitude=12.9716,
                    longitude=77.5946,
                    location_name="Cubbon Park South Exit & Kasturba Rd Cross",
                    description="Streetlights are not functional after 8 PM; frequent complaints of harassment.",
                    is_anonymous=False,
                    is_verified=True
                ),
                IncidentReport(
                    title="Suspicious Group Loitering & Catcalling",
                    category="Eve Teasing",
                    severity="HIGH",
                    latitude=12.9352,
                    longitude=77.6245,
                    location_name="Koramangala 5th Block Inner 80ft Road",
                    description="Multiple reports of aggressive comments and following women walking home from metro.",
                    is_anonymous=True,
                    is_verified=True
                ),
                IncidentReport(
                    title="Isolated Construction Stretch",
                    category="Suspicious Activity",
                    severity="MEDIUM",
                    latitude=12.9784,
                    longitude=77.6408,
                    location_name="Indiranagar 100ft Road Back Alley",
                    description="Poorly lit road near unfinished commercial building with high blind spots.",
                    is_anonymous=False,
                    is_verified=True
                ),
                IncidentReport(
                    title="Verbal Harassment & Stalking",
                    category="Stalking",
                    severity="CRITICAL",
                    latitude=12.9279,
                    longitude=77.6271,
                    location_name="BTM Layout 2nd Stage Ring Road Bus Stop",
                    description="Repeated vehicle following reported between 10 PM and 1 AM.",
                    is_anonymous=True,
                    is_verified=True
                ),
                IncidentReport(
                    title="Commercial Well-Lit Area (Low Risk)",
                    category="Commercial District",
                    severity="LOW",
                    latitude=12.9738,
                    longitude=77.6119,
                    location_name="Church Street Pedestrian Walkway",
                    description="Well-lit, high footfall, active security guards and police kiosk.",
                    is_anonymous=False,
                    is_verified=True
                ),
                IncidentReport(
                    title="Commercial Hub (Low Risk)",
                    category="Commercial District",
                    severity="LOW",
                    latitude=12.9345,
                    longitude=77.6101,
                    location_name="Forum Mall Outer Ring Road Transit",
                    description="Active patrol and continuous street illumination.",
                    is_anonymous=False,
                    is_verified=True
                )
            ]
            db.add_all(incidents)

        db.commit()
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_and_seed_db()
