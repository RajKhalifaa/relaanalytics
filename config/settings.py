# Environment Configuration for RELA Analytics Dashboard

# Application Settings
APP_NAME = "RELA Analytics Dashboard"
APP_VERSION = "1.0.0"
DEBUG = False

# Streamlit Configuration
STREAMLIT_CONFIG = {
    "server_address": "0.0.0.0",
    "server_port": 8501,
    "browser_gather_usage_stats": False,
    "server_headless": True,
}

# Data Settings
DATA_DIR = "data"
MODELS_DIR = "models"
ASSETS_DIR = "assets"

# Default Language
DEFAULT_LANGUAGE = "en"

# Performance Settings
CACHE_TTL = 3600  # 1 hour in seconds
MAX_DATA_ROWS = 100000
