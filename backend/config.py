import os

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Smart Women Safety Alert System")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "smart-women-safety-super-secret-jwt-key-2025")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./safety_system.db")

    SMS_PROVIDER: str = os.getenv("SMS_PROVIDER", "SIMULATED")
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")

    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./evidence_uploads")
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./ml/risk_model.joblib")

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
