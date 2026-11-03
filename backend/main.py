import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.routers import auth, sos, location, contacts, risk_route, incidents, geofence_evidence, chatbot, admin
from backend.services.notifier import ws_manager
from backend.seed_data import init_and_seed_db

init_and_seed_db()

app = FastAPI(
    title=settings.APP_NAME,
    description="Smart Women Safety Alert System Backend REST APIs and Real-Time WebSocket Services",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(sos.router)
app.include_router(location.router)
app.include_router(contacts.router)
app.include_router(risk_route.router)
app.include_router(incidents.router)
app.include_router(geofence_evidence.router)
app.include_router(chatbot.router)
app.include_router(admin.router)

@app.websocket("/ws/live-tracking")
async def websocket_tracking_endpoint(websocket: WebSocket, token: str = "global"):
    await ws_manager.connect(token, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f'{{"status": "received", "data": "{data}"}}')
    except WebSocketDisconnect:
        ws_manager.disconnect(token, websocket)

app.mount("/evidence_uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="evidence_uploads")

frontend_static_dir = os.path.abspath("./frontend/static")
if os.path.exists(frontend_static_dir):
    app.mount("/static", StaticFiles(directory=frontend_static_dir), name="static")

frontend_views_dir = os.path.abspath("./frontend/templates")
if os.path.exists(frontend_views_dir):
    app.mount("/", StaticFiles(directory=frontend_views_dir, html=True), name="frontend")
