"""
Configuration management for Niniko
Loads environment variables and provides configuration access
"""

import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Config:
    """Application configuration"""
    
    # Redis Configuration
    UPSTASH_REDIS_REST_URL: str = os.getenv("UPSTASH_REDIS_REST_URL", "")
    UPSTASH_REDIS_REST_TOKEN: str = os.getenv("UPSTASH_REDIS_REST_TOKEN", "")
    
    # Soniox STT
    SONIOX_API_KEY: str = os.getenv("SONIOX_API_KEY", "")
    
    # Azure OpenAI
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5-mini")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
    
    # ElevenLabs TTS
    ELEVEN_API_KEY: str = os.getenv("ELEVEN_API_KEY", "")
    ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "")
    ELEVENLABS_MODEL: str = os.getenv("ELEVENLABS_MODEL", "eleven_turbo_v2_5")
    
    # Application Settings
    DEFAULT_TIMEZONE: str = "Europe/Athens"
    DEFAULT_LANGUAGE: str = "el-GR"  # Greek
    
    # Agent Type Selection
    AGENT_TYPE: str = os.getenv("AGENT_TYPE", "dental")  # dental, hotel, elder
    
    # Hotel Configuration (for hotel agent)
    HOTEL_CONFIG_PATH: str = os.getenv("HOTEL_CONFIG_PATH", "data/hotel_config.yaml")
    HOTEL_ID: str = os.getenv("HOTEL_ID", "hotel_001")
    
    # Feature Flags
    ENABLE_HOTEL_INFO: bool = os.getenv("ENABLE_HOTEL_INFO", "true").lower() == "true"
    ENABLE_BOOKING_MANAGEMENT: bool = os.getenv("ENABLE_BOOKING_MANAGEMENT", "false").lower() == "true"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configuration is present"""
        required_fields = [
            ("UPSTASH_REDIS_REST_URL", cls.UPSTASH_REDIS_REST_URL),
            ("UPSTASH_REDIS_REST_TOKEN", cls.UPSTASH_REDIS_REST_TOKEN),
            ("SONIOX_API_KEY", cls.SONIOX_API_KEY),
            ("AZURE_OPENAI_API_KEY", cls.AZURE_OPENAI_API_KEY),
            ("AZURE_OPENAI_ENDPOINT", cls.AZURE_OPENAI_ENDPOINT),
            ("ELEVEN_API_KEY", cls.ELEVEN_API_KEY),
            ("ELEVENLABS_VOICE_ID", cls.ELEVENLABS_VOICE_ID),
        ]
        
        missing = [name for name, value in required_fields if not value]
        
        if missing:
            print(f"⚠️  Missing required configuration: {', '.join(missing)}")
            return False
        
        return True
    
    @classmethod
    def print_status(cls):
        """Print configuration status"""
        print("Configuration Status:")
        print(f"  Redis URL: {'✓' if cls.UPSTASH_REDIS_REST_URL else '✗'}")
        print(f"  Redis Token: {'✓' if cls.UPSTASH_REDIS_REST_TOKEN else '✗'}")
        print(f"  Soniox API: {'✓' if cls.SONIOX_API_KEY else '✗'}")
        print(f"  Azure OpenAI: {'✓' if cls.AZURE_OPENAI_API_KEY else '✗'}")
        print(f"  ElevenLabs: {'✓' if cls.ELEVEN_API_KEY else '✗'}")


# Create global config instance
config = Config()
