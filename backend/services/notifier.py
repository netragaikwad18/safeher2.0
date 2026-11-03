import json
from typing import Dict, List
from fastapi import WebSocket
from backend.config import settings

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, channel: str, websocket: WebSocket):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)

    def disconnect(self, channel: str, websocket: WebSocket):
        if channel in self.active_connections:
            if websocket in self.active_connections[channel]:
                self.active_connections[channel].remove(websocket)
            if not self.active_connections[channel]:
                del self.active_connections[channel]

    async def broadcast_to_channel(self, channel: str, message: dict):
        if channel in self.active_connections:
            for connection in self.active_connections[channel]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception:
                    pass

    async def broadcast_global(self, message: dict):
        for channel, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception:
                    pass

ws_manager = ConnectionManager()

def dispatch_emergency_sms(recipient_phone: str, recipient_name: str, message_body: str) -> str:
    if settings.SMS_PROVIDER == "TWILIO" and settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
        try:
            import requests
            url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"
            resp = requests.post(
                url,
                data={
                    "From": settings.TWILIO_PHONE_NUMBER,
                    "To": recipient_phone,
                    "Body": message_body
                },
                auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
                timeout=10
            )
            return "SENT" if resp.status_code in (200, 201) else f"FAILED ({resp.status_code})"
        except Exception as e:
            return f"FAILED ({str(e)})"
    else:
        return "SIMULATED_SUCCESS"
