import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL") or "postgresql+psycopg://ecommerce_user:ecommerce_pass@postgres:5432/ecommerce"
    REDIS_URL: str = os.getenv("REDIS_URL") or "redis://redis:6379/0"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
