from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "RecruitX"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # LiveKit Configuration
    LIVEKIT_API_KEY: str = os.getenv("LIVEKIT_API_KEY", "")
    LIVEKIT_API_SECRET: str = os.getenv("LIVEKIT_API_SECRET", "")
    LIVEKIT_URL: str = os.getenv("LIVEKIT_URL", "")
    
    # Groq Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    
    # Supabase Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # Public Base URL for webhooks
    PUBLIC_BASE_URL: str = os.getenv("PUBLIC_BASE_URL", "")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES(self) -> int:
        """Get access token expire minutes, handling string values from env vars"""
        value = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "11520")  # 8 days default
        try:
            # Remove any comments and convert to int
            if "#" in str(value):
                value = str(value).split("#")[0].strip()
            return int(value)
        except (ValueError, TypeError):
            return 11520  # 8 days default
    
    class Config:
        case_sensitive = True

settings = Settings() 