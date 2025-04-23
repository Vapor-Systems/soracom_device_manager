"""
Device model for representing Soracom devices in the web application.
"""
from datetime import datetime

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
        
        # Check if online info is in sessionStatus
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
        """Get device status as icon only"""
        if self.is_online():
            return "🟢"
        else:
            return "🔴"
    
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
        
        return "Unknown"
        
    def get_software_version(self):
        """Get the software version from device tags"""
        if 'tags' in self.data and self.data['tags']:
            tags = self.data['tags']
            if isinstance(tags, dict) and 'S/W Version' in tags:
                return tags['S/W Version']
        return "Unknown"
    
    def to_dict(self):
        """Convert device to dictionary for display in streamlit"""
        return {
            "Name": self.get_name(),
            "Status": self.get_status_text(),
            "Software Version": self.get_software_version(),
            "Last Seen": self.get_last_seen()
        }
        
    def to_detail_dict(self):
        """Create a detailed dictionary with all device information for the details page"""
        return {
            "Name": self.get_name(),
            "Status": self.get_status_text(),
            "Software Version": self.get_software_version(),
            "IMSI": self.get_imsi(),
            "IMEI": self.get_imei(),
            "Last Seen": self.get_last_seen(),
            "Raw Data": self.get_raw_data()
        }
