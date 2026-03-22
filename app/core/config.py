"""
Application configuration module using Pydantic settings.
"""
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Configure Pydantic to allow extra fields and case-insensitive env vars
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra environment variables
    )

    # FastAPI Configuration
    app_name: str = "TradeMind — NEPSE Chatbot"
    app_title: str = "TradeMind"
    debug: bool = Field(default=False, env="DEBUG")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="PORT")
    api_reload: bool = Field(default=False, env="API_RELOAD")
    
    # AI/Groq Configuration
    groq_api_key: str = Field(default="", env="GROQ_API_KEY")
    
    # Security
    secret_key: str = Field(default="your-secret-key-change-in-production", env="FLASK_SECRET_KEY")
    
    # Chat Configuration
    max_message_length: int = 500
    max_history_length: int = 20
    
    # Bot Configuration
    bot_name: str = "TradeMind"
    
    # Data Configuration
    data_folder: str = "data"
    documents_folder: str = "data/documents"
    vectorstore_folder: str = "data/vectorstore"


# Global settings instance
settings = Settings()
