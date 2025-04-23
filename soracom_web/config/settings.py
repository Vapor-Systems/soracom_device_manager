"""
Configuration settings for the Soracom Device Manager Web App.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Authentication settings
AUTH_URL = "https://g.api.soracom.io/v1/auth"
SUBSCRIBERS_URL = "https://g.api.soracom.io/v1/subscribers"

# Get credentials from environment variables
DEFAULT_EMAIL = os.getenv("SORACOM_EMAIL", "")
DEFAULT_PASSWORD = os.getenv("SORACOM_PASSWORD", "")

# UI Settings for Streamlit
APP_TITLE = "SORACOM Device Manager"
APP_ICON = "🛰️"

# Device status colors
COLOR_ONLINE = "#28a745"   # Green
COLOR_OFFLINE = "#dc3545"  # Red
