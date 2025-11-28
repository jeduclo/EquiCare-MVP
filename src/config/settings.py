"""
Configuration management module
Loads settings from config.yaml and environment variables
"""

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

import streamlit as st

# Try to load from Streamlit secrets first (for cloud deployment)
try:
    if hasattr(st, 'secrets'):
        OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")
        SECRET_KEY = st.secrets.get("SECRET_KEY", "")
    else:
        OPENAI_API_KEY = ""
        SECRET_KEY = ""
except:
    OPENAI_API_KEY = ""
    SECRET_KEY = ""
    
# Load environment variables
load_dotenv()

# Get project root directory
ROOT_DIR = Path(__file__).parent.parent.parent

# Load config.yaml
CONFIG_PATH = ROOT_DIR / "config.yaml"
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)


class Settings:
    """Application settings"""
    
    # Paths
    ROOT_DIR = ROOT_DIR
    DATA_DIR = ROOT_DIR / "data"
    AUDIO_DIR = DATA_DIR / "audio"
    UPLOADS_DIR = DATA_DIR / "uploads"
    ASSETS_DIR = ROOT_DIR / "assets"
    
    # Create directories if they don't exist
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Environment variables (from .env)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/equicare.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
    DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"
    SESSION_TIMEOUT_HOURS = int(os.getenv("SESSION_TIMEOUT_HOURS", "8"))
    
    # App settings (from config.yaml)
    APP_NAME = config['app']['name']
    APP_VERSION = config['app']['version']
    PAGE_TITLE = config['app']['page_title']
    PAGE_ICON = config['app']['page_icon']
    MAX_RECORDING_DURATION = config['app']['max_recording_duration']
    WARNING_DURATION = config['app']['warning_duration']
    
    # AI settings
    AI_TRANSCRIPTION_SERVICE = config['ai']['transcription']['service']
    AI_TRANSCRIPTION_MODEL = config['ai']['transcription']['model']
    AI_TRANSCRIPTION_LANGUAGE = config['ai']['transcription']['language']
    
    AI_SUMMARIZATION_SERVICE = config['ai']['summarization']['service']
    AI_SUMMARIZATION_MODEL = config['ai']['summarization']['model']
    AI_SUMMARIZATION_MAX_TOKENS = config['ai']['summarization']['max_tokens']
    AI_SUMMARIZATION_TEMPERATURE = config['ai']['summarization']['temperature']
    
    # Audio settings
    AUDIO_SAMPLE_RATE = config['audio']['sample_rate']
    AUDIO_CHANNELS = config['audio']['channels']
    AUDIO_FORMAT = config['audio']['format']
    MAX_FILE_SIZE_MB = config['audio']['max_file_size_mb']
    
    # Security settings
    MAX_LOGIN_ATTEMPTS = config['security']['max_login_attempts']
    LOCKOUT_DURATION_MINUTES = config['security']['lockout_duration_minutes']
    PASSWORD_MIN_LENGTH = config['security']['password_min_length']
    
    # UI Theme
    THEME = config['ui']['theme']
    RECORDING_BUTTON_COLOR = config['ui']['recording_button_color']
    SUCCESS_COLOR = config['ui']['success_color']
    
    @classmethod
    def validate(cls):
        """Validate that required settings are present"""
        if not cls.OPENAI_API_KEY or cls.OPENAI_API_KEY == "your-openai-api-key-here":
            raise ValueError(
                "OpenAI API key not configured. "
                "Please set OPENAI_API_KEY in .env file"
            )
        return True


# Validate settings on import
Settings.validate()