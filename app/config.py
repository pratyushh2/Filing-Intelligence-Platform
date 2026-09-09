import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GROQ_API_KEY: str
    FRONTEND_URL: str = "http://localhost:3000"
    CHROMA_PATH: str = "./chroma_db"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    GROQ_MODEL: str = "openai/gpt-oss-20b"
    SEC_USER_AGENT: str = "Pratyush pratyushh0212@gmail.com"

    model_config = {"env_file": ".env", "extra": "ignore"}

settings = Settings()
