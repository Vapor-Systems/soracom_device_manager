"""
Utility functions for the Soracom Device Manager.
Provides caching, data processing, and other helper functions.
"""
import os
import json
import time
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='device_manager.log',
    filemode='a'
)
logger = logging.getLogger('utils')

# Cache directory path
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")
DEVICE_CACHE_FILE = os.path.join(CACHE_DIR, "devices_cache.json")
CACHE_TTL = 60 * 10  # 10 minutes in seconds

def ensure_cache_dir():
    """Ensure the cache directory exists"""
    if not os.path.exists(CACHE_DIR):
        try:
            os.makedirs(CACHE_DIR)
            return True
        except Exception as e:
            logger.error(f"Failed to create cache directory: {e}")
            return False
    return True

def save_devices_to_cache(devices_data):
    """
    Save devices data to cache file
    
    Args:
        devices_data: List of device dictionaries to cache
        
    Returns:
        bool: True if cache was successfully saved, False otherwise
    """
    if not ensure_cache_dir():
        return False
        
    try:
        cache_data = {
            "timestamp": time.time(),
            "devices": devices_data
        }
        
        with open(DEVICE_CACHE_FILE, 'w') as f:
            json.dump(cache_data, f)
            
        logger.info(f"Cached {len(devices_data)} devices")
        return True
    except Exception as e:
        logger.error(f"Failed to save devices to cache: {e}")
        return False

def load_devices_from_cache():
    """
    Load devices data from cache if available and not expired
    
    Returns:
        list: List of device dictionaries or None if cache is invalid/expired
    """
    if not os.path.exists(DEVICE_CACHE_FILE):
        return None
        
    try:
        with open(DEVICE_CACHE_FILE, 'r') as f:
            cache_data = json.load(f)
            
        # Check if cache is expired
        timestamp = cache_data.get("timestamp", 0)
        current_time = time.time()
        
        if current_time - timestamp > CACHE_TTL:
            logger.info("Cache expired, will refresh from API")
            return None
            
        devices = cache_data.get("devices", [])
        if not devices:
            return None
            
        logger.info(f"Loaded {len(devices)} devices from cache (cached at {datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')})")
        return devices
    except Exception as e:
        logger.error(f"Failed to load devices from cache: {e}")
        return None

def clear_cache():
    """
    Clear the device cache file
    
    Returns:
        bool: True if cache was successfully cleared, False otherwise
    """
    if not os.path.exists(DEVICE_CACHE_FILE):
        return True
        
    try:
        os.remove(DEVICE_CACHE_FILE)
        logger.info("Device cache cleared")
        return True
    except Exception as e:
        logger.error(f"Failed to clear device cache: {e}")
        return False

def is_valid_imsi(imsi):
    """
    Check if a string is a valid IMSI (International Mobile Subscriber Identity)
    IMSI is typically a 15-digit number
    
    Args:
        imsi: The IMSI string to validate
        
    Returns:
        bool: True if IMSI is valid, False otherwise
    """
    if not imsi:
        return False
        
    # IMSI should be a string of 15 digits
    return isinstance(imsi, str) and imsi.isdigit() and len(imsi) == 15

def format_timestamp(timestamp_ms):
    """
    Format a Unix timestamp from milliseconds to a human-readable format
    
    Args:
        timestamp_ms: Timestamp in milliseconds
        
    Returns:
        str: Formatted datetime string
    """
    if not timestamp_ms:
        return "Unknown"
        
    try:
        timestamp_sec = int(timestamp_ms) / 1000  # Convert ms to seconds
        return datetime.fromtimestamp(timestamp_sec).strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError) as e:
        logger.error(f"Failed to format timestamp {timestamp_ms}: {e}")
        return "Invalid Timestamp"
