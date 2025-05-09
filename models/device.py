"""
Device model for representing Soracom devices.
"""
from datetime import datetime
import re

class Device:
    """Class representing a Soracom device with helper methods"""
    
    def __init__(self, device_data):
        """Initialize with device data from Soracom API"""
        self.data = device_data
    
    def is_online(self):
        """Check if a device is online based on sessionStatus"""
        # Check if 'online' field exists directly in the device dictionary
        if 'online' in self.data and self.data['online'] is True:
            return True
        
        # Check if online info is in sessionStatus (as a string in a dictionary)
        if 'sessionStatus' in self.data:
            session_status = self.data['sessionStatus']
            if isinstance(session_status, dict) and 'online' in session_status:
                return session_status['online'] is True
            # Sometimes sessionStatus contains a string representation of a dictionary
            elif isinstance(session_status, str) and "'online': True" in session_status:
                return True
        
        return False
    
    def get_name(self):
        """Extract the device name from the device data"""
        # Check if name exists directly
        if 'name' in self.data and self.data['name']:
            return self.data['name']
        
        # Check for tagName or similar fields
        if 'tagName' in self.data and self.data['tagName']:
            return self.data['tagName']
        
        # Check for tags that might contain name
        if 'tags' in self.data and self.data['tags']:
            tags = self.data['tags']
            if isinstance(tags, dict):
                if 'name' in tags:
                    return tags['name']
        
        return "Unnamed Device"
    
    def get_last_seen(self):
        """Get the last time a device was seen online"""
        if 'lastModifiedAt' in self.data:
            # Convert timestamp to readable format
            timestamp = int(self.data['lastModifiedAt']) / 1000  # Convert ms to seconds
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        return "Unknown"
    
    def get_imei(self):
        """Get device IMEI if available"""
        if 'imei' in self.data:
            return self.data['imei']
        return "Unknown"
    
    def get_status_text(self):
        """Get device status with colored indicators"""
        if self.is_online():
            return "🟢 Online "
        else:
            return "🔴 Offline"
    
    def get_raw_data(self):
        """Return the raw device data"""
        return self.data
        
    def get_imsi(self):
        """Get the device IMSI if available"""
        # Try direct IMSI fields
        if 'imsi' in self.data:
            return self.data['imsi']
        elif 'subscriberId' in self.data:
            return self.data['subscriberId']
        elif 'simId' in self.data:
            return self.data['simId']
            
        # Check in tags
        if 'tags' in self.data and isinstance(self.data['tags'], dict):
            tags = self.data['tags']
            if 'imsi' in tags:
                return tags['imsi']
            elif 'IMSI' in tags:
                return tags['IMSI']
            
        # Try to extract IMSI from name or other fields if it follows a pattern (15 digits)"""
"""
Device model for representing Soracom devices.
Enhanced with improved error handling and data validation.
"""
from datetime import datetime
import logging
import re

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='device_manager.log',
    filemode='a'
)
logger = logging.getLogger('device_model')

class Device:
    """Class representing a Soracom device with helper methods and improved error handling"""
    
    def __init__(self, device_data):
        """Initialize with device data from Soracom API"""
        self.data = device_data
    
    def is_online(self):
        """Check if a device is online based on sessionStatus"""
        # Check if 'online' field exists directly in the device dictionary
        if 'online' in self.data and self.data['online'] is True:
            return True
        
        # Check if online info is in sessionStatus (as a string in a dictionary)
        if 'sessionStatus' in self.data:
            session_status = self.data['sessionStatus']
            if isinstance(session_status, dict) and 'online' in session_status:
                return session_status['online'] is True
            # Sometimes sessionStatus contains a string representation of a dictionary
            elif isinstance(session_status, str) and "'online': True" in session_status:
                return True
        
        return False
    
    def get_name(self):
        """Extract the device name from the device data"""
        # Check if name exists directly
        if 'name' in self.data and self.data['name']:
            return self.data['name']
        
        # Check for tagName or similar fields
        if 'tagName' in self.data and self.data['tagName']:
            return self.data['tagName']
        
        # Check for tags that might contain name
        if 'tags' in self.data and self.data['tags']:
            tags = self.data['tags']
            if isinstance(tags, dict):
                if 'name' in tags:
                    return tags['name']
        
        return "Unnamed Device"
    
    def get_last_seen(self):
        """Get the last time a device was seen online"""
        if 'lastModifiedAt' in self.data:
            # Convert timestamp to readable format
            timestamp = int(self.data['lastModifiedAt']) / 1000  # Convert ms to seconds
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        return "Unknown"
    
    def get_imei(self):
        """Get device IMEI if available"""
        if 'imei' in self.data:
            return self.data['imei']
        return "Unknown"
    
    def get_status_text(self):
        """Get device status with colored indicators"""
        if self.is_online():
            return "🟢 Online"
        else:
            return "🔴 Offline"
    
    def get_raw_data(self):
        """Return the raw device data"""
        return self.data
        
    def get_imsi(self):
        """Get the device IMSI if available"""
        # Try direct IMSI fields in different possible formats
        if 'imsi' in self.data:
            return self.data['imsi']
        elif 'IMSI' in self.data:
            return self.data['IMSI']  
        elif 'subscriberId' in self.data:
            return self.data['subscriberId']
        elif 'simId' in self.data:
            return self.data['simId']
        
        # Check in tags
        if 'tags' in self.data and isinstance(self.data['tags'], dict):
            tags = self.data['tags']
            if 'imsi' in tags:
                return tags['imsi']
            elif 'IMSI' in tags:
                return tags['IMSI']
            elif 'subscriberId' in tags:
                return tags['subscriberId']
            elif 'simId' in tags:
                return tags['simId']
        
        # Try to extract IMSI from other fields that might contain it
        # IMSI is typically a 15-digit number
        for key, value in self.data.items():
            if isinstance(value, str) and value.isdigit() and len(value) == 15:
                return value
        
        # If no IMSI found, return None to indicate it needs to be provided manually
        return None
        
    def get_software_version(self):
        """Get the software version from device tags"""
        if 'tags' in self.data and self.data['tags']:
            tags = self.data['tags']
            if isinstance(tags, dict) and 'S/W Version' in tags:
                return tags['S/W Version']
        return "Unknown"
