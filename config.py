#I will provide the complete application structure across successive replies. Here is the first part, setting up your configuration and database connection.
#First, create config.py.
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Dubbing App"
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "outputs"
    DATABASE_URL: str = "sqlite:///./app.db"
    SECRET_KEY: str = "YOUR_SECRET_KEY"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "your_openai_key")
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "your_elevenlabs_key")

    class Config:
        env_file = ".env"

settings = Settings()

