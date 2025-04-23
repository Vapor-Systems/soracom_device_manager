"""
Tag management for Soracom devices.
"""
import requests

class TagService:
    """Service for managing tags on Soracom devices"""
    
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
    
    def get_tags(self, device):
        """
        Get all tags for a device.
        
        Args:
            device: The device object to get tags for
            
        Returns:
            dict: The tags for the device or empty dict if failed
        """
        if not device or not device.get_imsi():
            print(f"Cannot get tags without valid device IMSI")
            return {}
            
        device_imsi = device.get_imsi()
        
        # Soracom API endpoint to get subscriber info which includes tags
        url = f"{self.base_url}/subscribers/{device_imsi}"
        
        try:
            response = requests.get(
                url, 
                headers=self._api_headers()
            )
            
            if response.status_code == 200:
                # The response is a subscriber object that contains tags
                subscriber = response.json()
                # Extract tags from the subscriber data
                tags = subscriber.get('tags', {})
                return tags
            else:
                print(f"❌ Failed to get subscriber info. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return {}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ API request error: {str(e)}")
            return {}
    
    def put_tag(self, device, tag_name, tag_value):
        """
        Create or update a tag for a device.
        
        Args:
            device: The device object to create/update a tag for
            tag_name: The name of the tag to create/update
            tag_value: The value of the tag to create/update
            
        Returns:
            bool: True if the tag was successfully created/updated, False otherwise
        """
        if not device:
            print(f"Cannot create/update tag: Device object is missing")
            return False
            
        # Get IMSI and verify it exists and has proper format
        device_imsi = device.get_imsi()
        if not device_imsi or len(device_imsi) < 10:
            print(f"Cannot create/update tag: Invalid IMSI format")
            return False
            
        # Soracom API endpoint to create/update tags
        url = f"{self.base_url}/subscribers/{device_imsi}/tags"
        
        # The API expects a JSON array of tag objects
        payload = [
            {
                "tagName": tag_name.strip("'"),
                "tagValue": tag_value.strip("'")
            }
        ]
        
        try:
            response = requests.put(
                url, 
                json=payload,
                headers=self._api_headers()
            )
            
            if response.status_code in [200, 201, 204]:
                print(f"✅ Tag '{tag_name}' created/updated successfully")
                return True
            else:
                print(f"❌ Failed to create/update tag. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ API request error: {str(e)}")
            return False
    
    def delete_tag(self, device, tag_name):
        """
        Delete a tag from a device.
        
        Args:
            device: The device object to delete a tag from
            tag_name: The name of the tag to delete
            
        Returns:
            bool: True if the tag was successfully deleted, False otherwise
        """
        if not device or not device.get_imsi():
            print(f"Cannot delete tag without valid device IMSI")
            return False
            
        device_imsi = device.get_imsi()
        
        # Soracom API endpoint to delete tags
        url = f"{self.base_url}/subscribers/{device_imsi}/tags"
        
        # The API expects a list of tag names to delete
        payload = {
            "tagNames": [tag_name]
        }
        
        try:
            response = requests.delete(
                url, 
                json=payload,
                headers=self._api_headers()
            )
            
            if response.status_code in [200, 204]:
                print(f"✅ Tag '{tag_name}' deleted successfully")
                return True
            else:
                print(f"❌ Failed to delete tag. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ API request error: {str(e)}")
            return False
