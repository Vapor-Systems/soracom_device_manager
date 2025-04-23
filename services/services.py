"""
Core services for the Soracom Device Manager.
Provides device management, terminal connections, and update functionality.
Enhanced with caching and improved error handling.
"""
import requests
import time
import logging
from models.device import Device
from core import get_all_devices_paginated
from core.utils import (
    load_devices_from_cache, save_devices_to_cache, 
    clear_cache, is_valid_imsi
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='device_manager.log',
    filemode='a'
)
logger = logging.getLogger('services')

# === DEVICE SERVICE ===

class DeviceService:
    """Service for managing Soracom devices"""
    
    def __init__(self, auth_data):
        """Initialize with authentication data"""
        self.auth_data = auth_data
        self.devices = []
        self.online_devices = []
        self.offline_devices = []
    
    def load_devices(self, retries=3, timeout=30, limit=1000, use_cache=True, force_refresh=False):
        """
        Load all devices from the API and categorize them efficiently
        
        Args:
            retries: Number of retries on connection failure
            timeout: Request timeout in seconds
            limit: Number of devices to fetch per page
            use_cache: Whether to use cached device data if available
            force_refresh: Whether to force a refresh from the API
            
        Returns:
            bool: True if devices were loaded successfully, False otherwise
        """
        # Clear existing lists to ensure fresh data
        self.devices = []
        self.online_devices = []
        self.offline_devices = []
        
        # Try to load from cache first if enabled and not forcing refresh
        raw_devices = None
        if use_cache and not force_refresh:
            try:
                raw_devices = load_devices_from_cache()
                if raw_devices:
                    print(f"✅ Loaded {len(raw_devices)} devices from cache")
                    logger.info(f"Using {len(raw_devices)} devices from cache")
            except Exception as e:
                logger.error(f"Error loading from cache: {e}")
                raw_devices = None
        
        # If no cache or cache disabled, load from API
        if not raw_devices:
            print(f"Loading devices from Soracom API...")
            raw_devices = get_all_devices_paginated(
                self.auth_data, 
                limit=limit,
                timeout=timeout,
                max_retries=retries
            )
            
            # Save to cache if load was successful
            if raw_devices and len(raw_devices) > 0:
                try:
                    save_devices_to_cache(raw_devices)
                except Exception as e:
                    logger.error(f"Failed to save to cache: {e}")
        
        if not raw_devices:
            return False
        
        # Process devices in a single pass, categorizing as we go
        device_count = 0
        
        start_time = time.time()
        for device_data in raw_devices:
            try:
                device = Device(device_data)
                self.devices.append(device)
                
                # Categorize in the same loop to avoid multiple iterations
                if device.is_online():
                    self.online_devices.append(device)
                else:
                    self.offline_devices.append(device)
                    
                device_count += 1
            except Exception as e:
                logger.error(f"Error processing device data: {e}")
                print(f"❌ Error processing device data: {e}")
                # Continue with next device instead of failing entirely
                continue
        
        processing_time = time.time() - start_time
        logger.info(f"Processed {device_count} devices in {processing_time:.2f} seconds")
        
        return len(self.devices) > 0
    
    def get_all_devices(self):
        """Get all devices"""
        return self.devices
    
    def get_online_devices(self):
        """Get only online devices"""
        return self.online_devices
    
    def get_offline_devices(self):
        """Get only offline devices"""
        return self.offline_devices
    
    def get_device_counts(self):
        """Get device counts by category"""
        return {
            'total': len(self.devices),
            'online': len(self.online_devices),
            'offline': len(self.offline_devices)
        }
    
    def search_loaded_devices(self, search_term):
        """
        Search through devices in memory efficiently by name or S/W Version
        Returns exact matches if found, otherwise partial matches
        """
        if not search_term or not self.devices:
            return []
            
        search_term = search_term.lower()
        exact_matches = []
        partial_matches = []
        
        # Single pass through the devices list
        for device in self.devices:
            name = device.get_name().lower()
            sw_version = device.get_software_version().lower()
            
            # Check for exact match in either name or S/W Version
            if name == search_term or sw_version == search_term:
                exact_matches.append(device)
            # Check for partial match in either name or S/W Version
            elif search_term in name or search_term in sw_version:
                partial_matches.append(device)
        
        # Return exact matches if any found, otherwise partial matches
        return exact_matches if exact_matches else partial_matches

# === TERMINAL SERVICE ===

class TerminalService:
    """Service to handle terminal connections to devices via Soracom Napter"""
    
    def __init__(self, auth_data):
        """Initialize with authentication data"""
        self.auth_data = auth_data
        self.api_key = auth_data.get('apiKey', '')
        self.token = auth_data.get('token', '')
        self.base_url = "https://g.api.soracom.io/v1"
        self.napter_session = None
        self.username = 'pi'
        self.password = 'b4ustart'
        self.device_info = None
        self.ssh_process = None
    
    def _api_headers(self):
        """Get headers for API requests"""
        return {
            'Content-Type': 'application/json',
            'X-Soracom-API-Key': self.api_key,
            'X-Soracom-Token': self.token
        }
    
    def start_terminal_session(self, device):
        """
        Start a terminal session with a device using Soracom Napter API.
        
        Args:
            device: The device object to connect to
            
        Returns:
            bool: True if the session was successfully established, False otherwise
        """
        self.device_info = {
            'name': device.get_name(),
            'imei': device.get_imei(),
            'imsi': device.get_imsi(),
            'status': device.get_status_text()
        }
        
        device_imsi = device.get_imsi()
        device_name = device.get_name()
        
        if not device_imsi or device_imsi == "Unknown":
            print(f"ℹ️ Soracom Napter requires IMSI information which couldn't be found for this device.")
            print(f"ℹ️ We'll need to set up the connection manually through the Soracom Console.")
            
            print(f"\n⚠️ Could not automatically create a Napter port mapping.")
            print(f"⚠️ Please use the Soracom Console to create a port mapping manually.")
            print(f"⚠️ Steps: Login to Soracom → SIM Management → Select the device →")
            print(f"⚠️ Actions menu → On-demand remote access")
            return False
            
        print(f"Creating Napter port mapping for {device_name}...")
        
        # Call Soracom API to create a port mapping
        port_mapping_endpoint = f"{self.base_url}/port_mappings"
        
        # Get client IP
        client_ip = self._get_client_ip()
        ip_range = f"{client_ip}/32" if client_ip else "0.0.0.0/0"
        
        port_mapping_data = {
            "destination": {
                "imsi": device_imsi,
                "port": 22  # SSH port
            },
            "duration": 3600,  # 1 hour in seconds
            "ipRanges": [ip_range],
            "tlsRequired": False
        }
        
        try:
            response = requests.post(
                port_mapping_endpoint, 
                json=port_mapping_data,
                headers=self._api_headers()
            )
            
            if response.status_code == 201:
                # Successfully created port mapping
                self.napter_session = response.json()
                print(f"✅ Napter port mapping created successfully")
                print(f"✅ SSH connection available at: {self.napter_session['hostname']}:{self.napter_session['port']}")
                return True
            else:
                print(f"❌ Failed to create port mapping. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                
                # If we get a specific error about IMSI, print more helpful instructions
                if "imsi" in response.text.lower():
                    print(f"\n⚠️ The IMSI information may be incorrect or not recognized by Soracom.")
                    print(f"⚠️ Please use the Soracom Console to create a port mapping manually.")
                
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ API request error: {str(e)}")
            return False
    
    
    def _get_client_ip(self):
        """
        Get the client's public IP address.
        
        Returns:
            str: The client's IP address or None if it cannot be determined
        """
        try:
            # Try to get the public IP using a public API
            response = requests.get('https://api.ipify.org', timeout=3)
            if response.status_code == 200:
                return response.text.strip()
                
            # Fallback to another service if the first one fails
            response = requests.get('https://ifconfig.me', timeout=3)
            if response.status_code == 200:
                return response.text.strip()
                
        except Exception as e:
            print(f"⚠️ Warning: Unable to determine client IP: {str(e)}")
            
        return None
    
    def close_terminal_session(self):
        """
        Close the terminal session by deleting the Napter port mapping.
        
        Returns:
            bool: True if the session was successfully closed, False otherwise
        """
        if not self.napter_session:
            return True
            
        port_mapping_id = self.napter_session.get('id')
        
        if not port_mapping_id:
            return False
            
        print("Closing Napter port mapping...")
        
        delete_endpoint = f"{self.base_url}/port_mappings/{port_mapping_id}"
        
        try:
            response = requests.delete(delete_endpoint, headers=self._api_headers())
            
            if response.status_code in [200, 204]:
                print("✅ Napter port mapping deleted successfully")
                self.napter_session = None
                return True
            else:
                print(f"❌ Failed to delete port mapping. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ API request error: {str(e)}")
            return False
            
    def get_connection_info(self):
        """
        Get the connection information for the Napter session.
        
        Returns:
            tuple: (hostname, port) or (None, None) if no session
        """
        if not self.napter_session:
            return None, None
            
        hostname = self.napter_session.get('hostname')
        port = self.napter_session.get('port')
        
        return hostname, port

# === UPDATE SERVICE ===

class DeviceUpdateService:
    """Service to handle device update operations"""
    
    def __init__(self, auth_data):
        """Initialize with authentication data"""
        self.auth_data = auth_data
        self.api_key = auth_data.get('apiKey', '')
        self.token = auth_data.get('token', '')
        self.base_url = "https://g.api.soracom.io/v1"
    
    def _api_headers(self):
        """Get headers for API requests"""
        return {
            'Content-Type': 'application/json',
            'X-Soracom-API-Key': self.api_key,
            'X-Soracom-Token': self.token
        }
    
    def change_speed_class(self, device, speed_class):
        """
        Change the speed class of a device.
        
        Args:
            device: The device object to update
            speed_class: The new speed class (e.g. 's1.slow', 's1.fast')
            
        Returns:
            bool: True if the speed class was successfully changed, False otherwise
        """
        if not device or not device.get_imsi():
            print(f"Cannot change speed class without valid device IMSI")
            return False
            
        device_imsi = device.get_imsi()
        
        # Soracom API endpoint to update speed class - using the correct update_speed_class endpoint
        url = f"{self.base_url}/subscribers/{device_imsi}/update_speed_class"
        
        # The API expects speedClass in the payload
        payload = {
            "speedClass": speed_class
        }
        
        try:
            print(f"Changing speed class to {speed_class} for device {device.get_name()}...")
            response = requests.post(
                url, 
                json=payload,
                headers=self._api_headers()
            )
            
            if response.status_code in [200, 201, 204]:
                print(f"✅ Speed class changed to {speed_class} successfully")
                return True
            else:
                print(f"❌ Failed to change speed class. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                print(f"URL: {url}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ API request error: {str(e)}")
            return False
    
    def update_device(self, device, new_version):
        """
        Update a device to a new software version.
        This is a placeholder method that will be implemented later.
        """
        print(f"🔄 Simulating update for device: {device.get_name()}")
        print(f"🔄 Current software version: {device.get_software_version()}")
        print(f"🔄 Target software version: {new_version}")
        print("✅ This is a placeholder. The actual update functionality will be implemented later.")
        
        # Return success for now
        return True
