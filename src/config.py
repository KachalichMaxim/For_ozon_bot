"""Configuration module for loading and validating environment variables."""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # Google Sheets Configuration
    GOOGLE_SHEETS_ID: str = os.getenv("GOOGLE_SHEETS_ID", "")
    GOOGLE_SERVICE_ACCOUNT_JSON: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "bot.log")
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate that all required configuration values are present.
        
        Returns:
            bool: True if all required configs are present, False otherwise
        """
        required_configs = {
            "TELEGRAM_BOT_TOKEN": cls.TELEGRAM_BOT_TOKEN,
            "GOOGLE_SHEETS_ID": cls.GOOGLE_SHEETS_ID,
            "GOOGLE_SERVICE_ACCOUNT_JSON": cls.GOOGLE_SERVICE_ACCOUNT_JSON,
        }
        
        missing = [key for key, value in required_configs.items() if not value]
        
        if missing:
            logging.error(f"Missing required configuration: {', '.join(missing)}")
            return False
        
        # Validate service account JSON file exists
        json_path = Path(cls.GOOGLE_SERVICE_ACCOUNT_JSON)
        if not json_path.exists():
            logging.error(f"Service account JSON file not found: {json_path}")
            return False
        
        return True
    
    @classmethod
    def get_service_account_path(cls) -> Path:
        """Get absolute path to service account JSON file."""
        return Path(cls.GOOGLE_SERVICE_ACCOUNT_JSON).resolve()


