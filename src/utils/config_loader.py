"""Configuration management for the bot"""
import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class BotSettings(BaseModel):
    """Bot-specific settings"""
    telegram_token: str
    default_summary_count: int = 20
    max_summary_count: int = 100
    default_style: str = "Professional"


class StorageSettings(BaseModel):
    """Storage-specific settings"""
    message_retention_days: int = 30
    cleanup_interval_hours: int = 24
    database_path: str = "data/messages.db"


class APIKeys(BaseModel):
    """API keys for LLM providers"""
    openai: Optional[str] = None
    anthropic: Optional[str] = None
    gemini: Optional[str] = None


class ConfigFromFile(BaseModel):
    """Configuration loaded from config.json (BYOK mode)"""
    mode: str
    llm_provider: str
    api_keys: APIKeys
    bot: BotSettings
    storage: StorageSettings


class ConfigFromEnv(BaseSettings):
    """Configuration loaded from environment variables (hosted mode)"""
    telegram_bot_token: str
    mode: str = "hosted"
    llm_provider: str = "gemini"
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    default_summary_count: int = 20
    max_summary_count: int = 100
    default_style: str = "Professional"
    message_retention_days: int = 30
    cleanup_interval_hours: int = 24
    database_path: str = "data/messages.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class Config:
    """Unified configuration manager"""
    
    def __init__(self):
        self.mode: str = "hosted"
        self.llm_provider: str = "gemini"
        self.telegram_token: str = ""
        self.api_keys: Dict[str, Optional[str]] = {
            "openai": None,
            "anthropic": None,
            "gemini": None
        }
        self.bot_settings: BotSettings
        self.storage_settings: StorageSettings
        self._load_config()
    
    def _load_config(self):
        """Load configuration from either .env or config.json"""
        # First, check if we're in BYOK mode by looking for config.json
        config_path = Path("config/config.json")
        
        if config_path.exists():
            # BYOK mode: Load from config.json
            self._load_from_file(config_path)
        else:
            # Hosted mode: Load from .env
            self._load_from_env()
    
    def _load_from_file(self, config_path: Path):
        """Load configuration from config.json"""
        with open(config_path, "r") as f:
            data = json.load(f)
        
        config = ConfigFromFile(**data)
        self.mode = config.mode
        self.llm_provider = config.llm_provider
        self.telegram_token = config.bot.telegram_token
        self.api_keys = {
            "openai": config.api_keys.openai,
            "anthropic": config.api_keys.anthropic,
            "gemini": config.api_keys.gemini
        }
        self.bot_settings = config.bot
        self.storage_settings = config.storage
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        load_dotenv()
        env_config = ConfigFromEnv()
        
        self.mode = env_config.mode
        self.llm_provider = env_config.llm_provider
        self.telegram_token = env_config.telegram_bot_token
        self.api_keys = {
            "openai": env_config.openai_api_key,
            "anthropic": env_config.anthropic_api_key,
            "gemini": env_config.gemini_api_key
        }
        self.bot_settings = BotSettings(
            telegram_token=env_config.telegram_bot_token,
            default_summary_count=env_config.default_summary_count,
            max_summary_count=env_config.max_summary_count,
            default_style=env_config.default_style
        )
        self.storage_settings = StorageSettings(
            message_retention_days=env_config.message_retention_days,
            cleanup_interval_hours=env_config.cleanup_interval_hours,
            database_path=env_config.database_path
        )
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a specific provider"""
        return self.api_keys.get(provider)
    
    def validate(self) -> bool:
        """Validate that required configuration is present"""
        if not self.telegram_token:
            raise ValueError("Telegram bot token is required")
        
        if not self.get_api_key(self.llm_provider):
            raise ValueError(f"API key for {self.llm_provider} is required")
        
        return True


# Global config instance
config = Config()
