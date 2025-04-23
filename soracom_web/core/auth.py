"""
Authentication functionality for the Soracom Device Manager Web App.
"""
import json
import requests
from config.settings import AUTH_URL

def authenticate(email, password):
    """
    Authenticate with Soracom API using email and password
    
    Args:
        email (str): Soracom account email
        password (str): Soracom account password
        
    Returns:
        dict: Authentication data dictionary or None on failure
    """
    headers = {
        'Content-Type': 'application/json'
    }
    
    payload = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(AUTH_URL, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.RequestException:
        return None

def logout(auth_data):
    """
    Properly logout and release the API token
    
    Args:
        auth_data (dict): Authentication data including apiKey and token
        
    Returns:
        bool: True if logout was successful or handled gracefully
    """
    if not auth_data:
        return True
    
    logout_url = "https://g.api.soracom.io/v1/auth/logout"
    
    headers = {
        'Content-Type': 'application/json',
        'X-Soracom-API-Key': auth_data.get('apiKey', ''),
        'X-Soracom-Token': auth_data.get('token', '')
    }
    
    try:
        response = requests.post(logout_url, headers=headers)
        return response.status_code in [200, 204, 403]
    except requests.exceptions.RequestException:
        return True  # Continue with exit process even if logout fails
