"""
Configuration settings for the Soracom Device Manager.
"""

# Application Version
APP_VERSION = "1.0.0"

# API Configuration
API_BASE_URL = "https://g.api.soracom.io/v1"
AUTH_URL = f"{API_BASE_URL}/auth"
SUBSCRIBERS_URL = f"{API_BASE_URL}/subscribers"

import os

# Get credentials from environment variables with fallbacks for development
DEFAULT_EMAIL = os.environ.get("SORACOM_EMAIL", "")
DEFAULT_PASSWORD = os.environ.get("SORACOM_PASSWORD", "")

# UI Settings
TERMINAL_DELIMITER = "▁"  # Bottom line unicode character

# ANSI Color Codes
class Colors:
    # Basic colors
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[0;33m"
    BLUE = "\033[0;34m"
    MAGENTA = "\033[0;35m"
    CYAN = "\033[0;36m"
    WHITE = "\033[0;37m"
    
    # Bright colors
    BRIGHT_BLACK = "\033[0;90m"
    BRIGHT_RED = "\033[0;91m"
    BRIGHT_GREEN = "\033[0;92m"
    BRIGHT_YELLOW = "\033[0;93m"
    BRIGHT_BLUE = "\033[0;94m"
    BRIGHT_MAGENTA = "\033[0;95m"
    BRIGHT_CYAN = "\033[0;96m"
    BRIGHT_WHITE = "\033[0;97m"
    
    # Bold colors
    BOLD_RED = "\033[1;31m"
    BOLD_GREEN = "\033[1;32m"
    BOLD_YELLOW = "\033[1;33m"
    BOLD_BLUE = "\033[1;34m"
    BOLD_MAGENTA = "\033[1;35m"
    BOLD_CYAN = "\033[1;36m"
    BOLD_WHITE = "\033[1;37m"
    
    # Text styles
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    ITALIC = "\033[3m"
    
    # Reset
    RESET = "\033[0m"

# UI Component Colors
class UI:
    HEADER = Colors.BOLD_BLUE
    TITLE = Colors.BOLD_CYAN
    SUBTITLE = Colors.CYAN
    SUCCESS = Colors.BOLD_GREEN
    ERROR = Colors.BOLD_RED
    WARNING = Colors.BOLD_YELLOW
    INFO = Colors.BOLD_WHITE
    MENU_ITEM = Colors.BRIGHT_WHITE
    MENU_NUMBER = Colors.BRIGHT_CYAN
    INPUT_PROMPT = Colors.BRIGHT_GREEN
    DEVICE_ONLINE = Colors.BOLD_GREEN
    DEVICE_OFFLINE = Colors.BOLD_RED
    SEPARATOR = Colors.BRIGHT_BLACK
    DATA_LABEL = Colors.BRIGHT_YELLOW
    DATA_VALUE = Colors.BRIGHT_WHITE
    LOADING = Colors.BRIGHT_MAGENTA
    
    # Status Icons
    ICON_OK = "✓"
    ICON_ERROR = "✗"
    ICON_WARNING = "⚠"
    ICON_INFO = "ℹ"
    ICON_LOADING = "⟳"
    ICON_DEVICE = "📱"
    ICON_ONLINE = "🟢"
    ICON_OFFLINE = "🔴"
    ICON_SEARCH = "🔍"
    ICON_UPDATE = "↻"
    ICON_TERMINAL = "💻"
    ICON_BACK = "←"
    ICON_EXIT = "✕"
    ICON_TAG = "🏷️"
