# Smart Women Safety Alert System

An advanced, intelligent, and real-time women safety alert system developed as an engineering major project. Built using **FastAPI**, **MySQL / SQLite**, **Scikit-learn**, **Bootstrap 5**, and interactive **Leaflet / OpenStreetMap** with WebSockets, Web Speech, and Device Motion APIs.

---

## 1. System Architecture

The architecture consists of four tightly-integrated tiers:
1. **Frontend Presentation Layer**: Built with responsive HTML5/CSS3/JavaScript (Bootstrap 5) with custom dark navy/purple/pink styling. Integrates HTML5 Geolocation, Battery Status API, Network Information API, Web Speech API (speech recognition in English & Kannada), and Device Motion sensor acceleration triggers.
2. **Backend Application Layer**: FastAPI ASGI asynchronous web server exposing modular REST APIs and WebSockets (`/ws/live-tracking`) for low-latency emergency telemetry.
3. **Machine Learning & Risk Engine**:
   - Random Forest Classifier trained using Scikit-Learn on spatial, temporal, lighting, velocity, and incident density features to predict real-time safety risk categories (SAFE, WARNING, HIGH RISK).
   - Dijkstra's pathfinding graph algorithm prioritizing safety over distance by incorporating crime hotspot penalties.
4. **Database & Storage Layer**:
   - Normalized relational schema supporting MySQL and SQLite via SQLAlchemy.
   - Tables: `users`, `emergency_contacts`, `emergency_alerts`, `location_history`, `incident_reports`, `risk_predictions`, `safe_zones`, `notifications`, `incident_evidence`, `admin_users`.

---

## 2. Project Folder Structure

```
.
├── backend/
│   ├── config.py             # Environment configuration & settings
│   ├── database.py           # SQLAlchemy engine & session factory
│   ├── main.py               # FastAPI application entrypoint & static mounts
│   ├── models.py             # Relational ORM models
│   ├── security.py           # Bcrypt hashing & JWT token handlers
│   ├── seed_data.py          # Demo user, contact, and hotspot seeding
│   ├── routers/
│   │   ├── admin.py          # Police & rapid response cell dispatch endpoints
│   │   ├── auth.py           # Registration, login, profile, and password reset
│   │   ├── chatbot.py        # Bilingual AI safety assistant (English & Kannada)
│   │   ├── contacts.py       # CRUD for trusted emergency contacts
│   │   ├── geofence_evidence.py # Safe zone notifications and audio evidence
│   │   ├── incidents.py      # Anonymous crowd-sourced hazard & hotspot reporting
│   │   ├── location.py       # Live GPS updates & WebSocket tracking room
│   │   ├── risk_route.py     # AI risk prediction & Dijkstra safe route optimizer
│   │   └── sos.py            # 5-second countdown SOS alert trigger & resolution
│   └── services/
│       ├── notifier.py       # SMS / WhatsApp notification dispatcher
│       ├── risk_engine.py    # Feature extractor & Scikit-Learn inference
│       └── route_engine.py   # Dijkstra safe routing pathfinder
├── database/
│   └── schema.sql            # Full MySQL / SQLite DDL script
├── frontend/
│   ├── static/
│   │   ├── css/styles.css    # Dark navy, purple & pink design theme
│   │   └── js/app.js         # SOS countdown, speech, shake, audio simulation
│   └── templates/
│       ├── admin.html        # Police dispatch command center
│       ├── chatbot.html      # Bilingual AI safety assistant
│       ├── contacts.html     # Trusted emergency contact management
│       ├── dashboard.html    # Core safety command hub
│       ├── forgot_password.html # Password recovery
│       ├── history.html      # Incident audit history
│       ├── hotspots.html     # Interactive crime hotspot map
│       ├── index.html        # Landing page
│       ├── login.html        # User & admin authentication
│       ├── profile.html      # Profile & emergency PIN configuration
│       ├── register.html     # User registration
│       ├── risk.html         # AI risk prediction testbed
│       ├── route.html        # Dijkstra safe route recommender
│       ├── sos.html          # Full-screen emergency SOS trigger & countdown
│       └── tracking.html     # Real-time GPS tracking dashboard
├── ml/
│   ├── risk_model.joblib     # Serialized Scikit-learn Random Forest model
│   ├── synthetic_risk_sample.csv # Synthetic incident training records
│   └── train_risk_model.py   # Model training & evaluation script
├── tests/
│   └── test_safety_system.py # Comprehensive unit and API test suite
├── .env.example              # Sample environment configurations
├── .gitignore                # Git exclusions
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation & execution guide
```

---

## 3. Installation & Setup Guide

### Prerequisites
- Python 3.10+ (Tested on Python 3.12)
- Pip package manager
- (Optional) MySQL Server 8.0+

### Step 1: Clone and Create Virtual Environment
```bash
git clone <repository-url>
cd women-safety-alert-system
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy the `.env.example` file:
```bash
cp .env.example .env
```
*(Default settings run seamlessly with SQLite `sqlite:///./safety_system.db`)*

### Step 4: Train Machine Learning Model (Pre-trained model included)
```bash
python ml/train_risk_model.py
```

### Step 5: Seed Demo Accounts and Hotspots
```bash
python -m backend.seed_data
```
**Default Credentials:**
- **User Account:** `pooja@example.com` / `Password123!` (Emergency PIN: `4321`)
- **Admin Account:** `admin@example.com` / `AdminPass123!`

---

## 4. Running the Application

Start the FastAPI application with Uvicorn:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Access the system in your browser:
- **Landing Page:** [http://localhost:8000/](http://localhost:8000/)
- **Dashboard:** [http://localhost:8000/dashboard](http://localhost:8000/dashboard)
- **Emergency SOS:** [http://localhost:8000/sos](http://localhost:8000/sos)
- **Live Tracking:** [http://localhost:8000/tracking](http://localhost:8000/tracking)
- **AI Risk Engine:** [http://localhost:8000/risk](http://localhost:8000/risk)
- **Safe Routes:** [http://localhost:8000/route](http://localhost:8000/route)
- **Crime Hotspots:** [http://localhost:8000/hotspots](http://localhost:8000/hotspots)
- **AI Safety Chatbot:** [http://localhost:8000/chatbot](http://localhost:8000/chatbot)
- **Admin Command Center:** [http://localhost:8000/admin](http://localhost:8000/admin)
- **Interactive Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 5. Running Automated Tests

Run the test suite using Pytest:
```bash
PYTHONPATH=. pytest tests/test_safety_system.py -v
```

All 8 core test suites (Authentication, Contacts, Risk AI Model, Dijkstra Router, SOS Trigger/Resolution, Chatbot, and Incident Hotspots) execute and pass cleanly.

---

## 6. Major Features Highlight

1. **SOS Emergency Countdown**: 5-second countdown with immediate cancellation or silent/siren dispatch with Google Maps link generation.
2. **Bilingual AI Voice Activation**: Voice recognition triggers SOS on English keywords ("help me", "emergency") or Kannada keywords ("kapaadi", "sahaya madi").
3. **Smartphone Shake Detection**: DeviceMotion accelerometer monitoring triggers SOS countdown upon rapid shaking.
4. **Simulated Fake Incoming Call**: Web Audio synthesizer generates realistic call ringtone and interface to escape uncomfortable situations.
5. **Battery & Offline Resiliency**: Monitors battery status below 15% to alert contacts and queues GPS updates locally when offline.
