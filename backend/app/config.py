"""
⚙️ Central configuration for AI Support Copilot.
All values are loaded from environment variables (see .env.example).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- MongoDB Atlas ---
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "ai_support_copilot"

    # --- JWT Auth ---
    jwt_secret: str = "change-me-super-secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24  # 24h

    # --- OTP ---
    otp_expire_minutes: int = 5
    otp_length: int = 6

    # --- Brevo (Sendinblue) transactional email for OTP ---
    brevo_api_key: str = ""
    brevo_sender_email: str = "no-reply@ai-support-copilot.dev"
    brevo_sender_name: str = "AI Support Copilot"

    # --- Gemini AI ---
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # --- ChromaDB ---
    chroma_persist_dir: str = "./chroma_data"

    # --- Uploads ---
    upload_dir: str = "./uploads"
    max_upload_mb: int = 8

    # --- CORS ---
    frontend_origin: str = "http://localhost:5173"

    # --- App ---
    env: str = "development"
    # Set to true to skip real OTP emails and log the code to console instead
    dev_mode_log_otp: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
