"""
Device service for Soracom Device Manager Web App.
"""
import time
import requests
from config.settings import SUBSCRIBERS_URL
from models.device import Device

class DeviceService:
    """Service for retrieving and managing device data from Soracom API"""
    
    def __init__(self, auth_data):
        """
        Initialize with authentication data
        
        Args:
            auth_data (dict): Authentication data containing apiKey and token
        """
        self.auth_data = auth_data
        self.headers = {
            'Content-Type': 'application/json',
            'X-Soracom-API-Key': auth_data.get('apiKey', ''),
            'X-Soracom-Token': auth_data.get('token', '')
        }
    
    def get_all_devices(self, status_filter=None, limit=1000, max_retries=3):
        """
        Get all devices from Soracom API with pagination support
        
        Args:
            status_filter (str, optional): Filter for device status
            limit (int, optional): Maximum number of devices per page
            max_retries (int, optional): Maximum number of retries on failure
            
        Returns:
            list: List of Device objects or empty list on error
        """
        if not self.auth_data:
            return []
            
        # Start with empty list and first page
        all_devices = []
        last_evaluated_key = None
        page = 1
        retry_count = 0
        
        try:
            while True:
                # Prepare query parameters
                params = {'limit': limit}
                
                # Add pagination token if not the first page
                if last_evaluated_key:
                    params['last_evaluated_key'] = last_evaluated_key
                    
                # Add filters if provided
                if status_filter:
                    params['status_filter'] = status_filter
                    
                try:
                    # Make API request with a 30-second timeout
                    response = requests.get(
                        SUBSCRIBERS_URL, 
                        headers=self.headers, 
                        params=params, 
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        # Get devices from this page
                        page_devices = response.json()
                        
                        if page_devices:
                            for device_data in page_devices:
                                all_devices.append(Device(device_data))
                        
                        # Check if we received a pagination token for the next page
                        last_evaluated_key = response.headers.get('x-soracom-next-key')
                        
                        # If no token or empty page, we're done
                        if not last_evaluated_key or not page_devices:
                            break
                            
                        # Reset retry counter on success
                        retry_count = 0
                        
                        # Move to next page
                        page += 1
                        
                    elif response.status_code in [401, 403]:
                        # Authentication or authorization error
                        return []
                        
                    else:
                        # Handle other errors
                        if retry_count < max_retries:
                            retry_count += 1
                            time.sleep(2)  # Wait before retry
                            continue
                        else:
                            break
                            
                except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                    if retry_count < max_retries:
                        retry_count += 1
                        time.sleep(2)  # Wait before retry
                        continue
                    else:
                        break
                        
            return all_devices
                
        except requests.exceptions.RequestException:
            return []
    
    def get_online_devices(self):
        """Get only online devices"""
        all_devices = self.get_all_devices()
        return [device for device in all_devices if device.is_online()]
    
    def get_offline_devices(self):
        """Get only offline devices"""
        all_devices = self.get_all_devices()
        return [device for device in all_devices if not device.is_online()]
