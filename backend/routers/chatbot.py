from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter(prefix="/api/chatbot", tags=["AI Safety Assistant Chatbot"])

class ChatQueryRequest(BaseModel):
    message: str
    language: str = "en"

SAFETY_KNOWLEDGE_BASE = [
    {
        "keywords": ["helpline", "number", "police", "dial", "call", "ಸಹಾಯವಾಣಿ", "ಪೊಲೀಸ್", "112"],
        "en": (
            "📞 VERIFIED EMERGENCY HELPLINES:\n"
            "• National Emergency Response Support: 112\n"
            "• Women Helpline (All India): 1091 / 181\n"
            "• National Commission for Women (NCW) 24/7: 7827170170\n"
            "• Cyber Crime Helpline: 1930\n"
            "• Bengaluru City Police Parihar Safety Cell: 080-22943225"
        ),
        "kn": (
            "📞 ಪ್ರಮುಖ ತುರ್ತು ಸಹಾಯವಾಣಿ ಸಂಖ್ಯೆಗಳು:\n"
            "• ರಾಷ್ಟ್ರೀಯ ತುರ್ತು ಬೆಂಬಲ ಸಂಖ್ಯೆ: 112\n"
            "• ಮಹಿಳಾ ಸಹಾಯವಾಣಿ: 1091 / 181\n"
            "• ಸೈಬರ್ ಕ್ರೈಮ್ ಸಹಾಯವಾಣಿ: 1930\n"
            "• ಬೆಂಗಳೂರು ಪರಿಹಾರ ಮಹಿಳಾ ಸಹಾಯವಾಣಿ: 080-22943225"
        )
    },
    {
        "keywords": ["sos", "danger", "attack", "save me", "help me", "ಕಾಪಾಡಿ"],
        "en": (
            "⚠️ IF YOU ARE IN IMMEDIATE DANGER: Press the large red SOS button on your screen. "
            "A 5-second countdown will begin, and high-priority SMS alerts with your real-time GPS location "
            "will be dispatched to all your primary emergency contacts and the safety rapid cell (Hotline 112). "
            "You can also activate SOS silently by checking 'Silent SOS'."
        ),
        "kn": (
            "⚠️ ನೀವು ತಕ್ಷಣದ ಅಪಾಯದಲ್ಲಿದ್ದರೆ: ಪರದೆಯ ಮೇಲಿನ ದೊಡ್ಡ ಕೆಂಪು SOS ಬಟನ್ ಅನ್ನು ಒತ್ತಿರಿ. "
            "5 ಸೆಕೆಂಡುಗಳ ಕೌಂಟ್‌ಡೌನ್ ಪ್ರಾರಂಭವಾಗುತ್ತದೆ ಮತ್ತು ನಿಮ್ಮ ನೈಜ-ಸಮಯದ GPS ಸ್ಥಳದೊಂದಿಗೆ ನಿಮ್ಮ "
            "ತುರ್ತು ಸಂಪರ್ಕಗಳಿಗೆ ಎಚ್ಚರಿಕೆ ಸಂದೇಶ ರವಾನೆಯಾಗುತ್ತದೆ (ತುರ್ತು ಸಂಖ್ಯೆ 112)."
        )
    },
    {
        "keywords": ["voice", "speech", "command", "ಧ್ವನಿ"],
        "en": (
            "🎙️ VOICE ACTIVATION GUIDE: You can trigger emergency SOS by speaking either in English "
            "('HELP ME', 'SAVE ME', 'EMERGENCY') or in Kannada ('ಕಾಪಾಡಿ', 'ಸಹಾಯ ಮಾಡಿ'). "
            "Ensure microphone permissions are enabled on the Emergency SOS page."
        ),
        "kn": (
            "🎙️ ಧ್ವನಿ ಆಧಾರಿತ ತುರ್ತು ಸಕ್ರಿಯಗೊಳಿಸುವಿಕೆ: ನೀವು 'ಕಾಪಾಡಿ', 'ಸಹಾಯ ಮಾಡಿ' ಅಥವಾ 'HELP ME' "
            "ಎಂದು ಧ್ವನಿ ಆಜ್ಞೆ ನೀಡುವ ಮೂಲಕ ತುರ್ತು SOS ಅನ್ನು ಸಕ್ರಿಯಗೊಳಿಸಬಹುದು."
        )
    },
    {
        "keywords": ["shake", "phone", "ವೈಬ್ರೇಷನ್"],
        "en": (
            "📱 SHAKE ACTIVATION GUIDE: If you vigorously shake your smartphone back and forth 3 times, "
            "the system detects high-acceleration shake patterns and triggers the 5-second emergency countdown."
        ),
        "kn": (
            "📱 ಮೊಬೈಲ್ ಶೇಕ್ ಸಕ್ರಿಯಗೊಳಿಸುವಿಕೆ: ನಿಮ್ಮ ಸ್ಮಾರ್ಟ್‌ಫೋನ್ ಅನ್ನು 3 ಬಾರಿ ಬಲವಾಗಿ ಅಲುಗಾಡಿಸಿದರೆ (shake), "
            "ವ್ಯವಸ್ಥೆಯು ಸ್ವಯಂಚಾಲಿತವಾಗಿ 5-ಸೆಕೆಂಡುಗಳ SOS ಕೌಂಟ್‌ಡೌನ್ ಪ್ರಾರಂಭಿಸುತ್ತದೆ."
        )
    },
    {
        "keywords": ["route", "safe", "walk", "travel", "ರಸ್ತೆ", "ಮಾರ್ಗ"],
        "en": (
            "🗺️ SAFE ROUTE RECOMMENDATION: Our AI routing engine uses Dijkstra's algorithm to analyze "
            "verified crime reports, street lighting, and footfall to suggest the safest route between "
            "your source and destination, rather than simply the shortest path."
        ),
        "kn": (
            "🗺️ ಸುರಕ್ಷಿತ ಮಾರ್ಗ ಶಿಫಾರಸು: ನಮ್ಮ AI ಮಾರ್ಗ ಯೋಜಕವು ಕಡಿಮೆ ಅಪರಾಧ ಘಟನೆಗಳು ಮತ್ತು ಉತ್ತಮ ಬೆಳಕಿನ "
            "ವ್ಯವಸ್ಥೆ ಹೊಂದಿರುವ ಸುರಕ್ಷಿತ ರಸ್ತೆಗಳನ್ನು ಶಿಫಾರಸು ಮಾಡುತ್ತದೆ."
        )
    },
    {
        "keywords": ["fake", "call", "ಕಾಲ್"],
        "en": (
            "📲 FAKE INCOMING CALL: Use the 'Fake Call' button in the dashboard or SOS view. "
            "It simulates a realistic phone ring with customizable caller name (e.g., 'Dad' or 'Police Desk') "
            "allowing you to excuse yourself from uncomfortable or suspicious situations."
        ),
        "kn": (
            "📲 ನಕಲಿ ಒಳಬರುವ ಕರೆ: ಅನುಮಾನಾಸ್ಪದ ಸನ್ನಿವೇಶಗಳಿಂದ ಸುರಕ್ಷಿತವಾಗಿ ತಪ್ಪಿಸಿಕೊಳ್ಳಲು ಡ್ಯಾಶ್‌ಬೋರ್ಡ್‌ನಲ್ಲಿರುವ "
            "'Fake Call' ವೈಶಿಷ್ಟ್ಯವನ್ನು ಬಳಸಿ."
        )
    }
]

DEFAULT_FALLBACK = {
    "en": (
        "I am your AI Safety Assistant. I can guide you on emergency SOS actions, safe routes, "
        "verified helpline contacts (112, 1091), voice triggers (English/Kannada), and fake call tools.\n"
        "Important: If you are in immediate physical danger, dial 112 or press the SOS button immediately."
    ),
    "kn": (
        "ನಾನು ನಿಮ್ಮ AI ಮಹಿಳಾ ಸುರಕ್ಷತಾ ಸಹಾಯಕ. ತುರ್ತು SOS, ಸುರಕ್ಷಿತ ಮಾರ್ಗಗಳು, 112 ಸಹಾಯವಾಣಿ ಸಂಖ್ಯೆಗಳು "
        "ಮತ್ತು ಧ್ವನಿ ಸಕ್ರಿಯಗೊಳಿಸುವಿಕೆ ಕುರಿತು ನಾನು ಮಾಹಿತಿ ನೀಡಬಲ್ಲೆ.\n"
        "ನೀವು ತಕ್ಷಣದ ಅಪಾಯದಲ್ಲಿದ್ದರೆ ದಯವಿಟ್ಟು 112 ಗೆ ಕರೆ ಮಾಡಿ ಅಥವಾ SOS ಬಟನ್ ಒತ್ತಿರಿ."
    )
}

@router.post("/query")
def chat_query(data: ChatQueryRequest):
    msg_lower = data.message.lower().strip()
    lang = "kn" if data.language == "kn" else "en"

    matched_response = None
    for item in SAFETY_KNOWLEDGE_BASE:
        if any(kw in msg_lower for kw in item["keywords"]):
            matched_response = item[lang]
            break

    if not matched_response:
        matched_response = DEFAULT_FALLBACK[lang]

    return {
        "reply": matched_response,
        "language": lang,
        "disclaimer": "The AI Safety Assistant provides informational guidance only and is not a replacement for official police or 112 emergency services."
    }
