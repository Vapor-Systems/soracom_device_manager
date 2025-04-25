"""
Core functionality for the Soracom Device Manager.
Combines authentication, API interaction, and UI utilities in a single module.
"""
import os
import sys
import time
import json
import shutil
import requests
from config.settings import (
    Colors, UI, 
    AUTH_URL, DEFAULT_EMAIL, DEFAULT_PASSWORD,
    SUBSCRIBERS_URL
)

# === AUTHENTICATION ===

def authenticate(email=None, password=None):
    """Authenticate with Soracom API using email and password"""
    if email is None:
        email = DEFAULT_EMAIL
    if password is None:
        password = DEFAULT_PASSWORD
        
    headers = {
        'Content-Type': 'application/json'
    }
    
    payload = {
        "email": email,
        "password": password
    }
    
    print("Authenticating with Soracom API...", end="", flush=True)
    
    try:
        response = requests.post(AUTH_URL, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            print("\r✅ Authentication successful!              ")
            return response.json()
        else:
            print(f"\r❌ Authentication failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"\r❌ Connection error: {e}")
        return None

def logout(auth_data):
    """Properly logout and release the API token"""
    if not auth_data:
        return True
    
    logout_url = "https://g.api.soracom.io/v1/auth/logout"
    
    headers = {
        'Content-Type': 'application/json',
        'X-Soracom-API-Key': auth_data.get('apiKey', ''),
        'X-Soracom-Token': auth_data.get('token', '')
    }
    
    try:
        print("Logging out and releasing API token...", end="", flush=True)
        response = requests.post(logout_url, headers=headers)
        
        if response.status_code == 200:
            print("\r✅ Successfully logged out and released API token.")
        elif response.status_code == 204:
            print("\r✅ Successfully logged out. (Status: 204)")
        elif response.status_code == 403:
            # Handle 403 Forbidden error gracefully
            print("\r✅ Session ended. (Session may have already expired)")
        else:
            print(f"\r✅ Session ended. (Status: {response.status_code})")
            
        return True
    except requests.exceptions.RequestException as e:
        print(f"\r✅ Session ended. (Connection issue handled)")
        return True  # Continue with exit process even if logout fails

# === API INTERACTION ===

def get_all_devices_paginated(auth_data, status_filter=None, tag_name=None, tag_value=None, limit=1000, timeout=30, max_retries=3):
    """
    Get all devices from Soracom API with pagination support
    
    Args:
        auth_data: Authentication data dictionary with apiKey and token
        status_filter: Optional filter for device status
        tag_name: Optional filter for tag name
        tag_value: Optional filter for tag value
        limit: Maximum number of devices to retrieve per page
        timeout: Request timeout in seconds
        max_retries: Maximum number of retries on failure
    
    Returns:
        list: List of device dictionaries or None on error
    """
    if not auth_data or 'apiKey' not in auth_data or 'token' not in auth_data:
        print("\r❌ Invalid authentication data.")
        return None
        
    headers = {
        'Content-Type': 'application/json',
        'X-Soracom-API-Key': auth_data['apiKey'],
        'X-Soracom-Token': auth_data['token']
    }
    
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
            if tag_name:
                params['tag_name'] = tag_name
            if tag_value:
                params['tag_value'] = tag_value
                
            # Show progress with page number and current count
            device_count = len(all_devices)
            progress_msg = f"Retrieved {device_count} devices so far" if device_count > 0 else "Starting retrieval"
            print(f"\rRetrieving devices (page {page}) - {progress_msg}...", end="", flush=True)
            
            try:
                # Make API request with specified timeout
                response = requests.get(SUBSCRIBERS_URL, headers=headers, params=params, timeout=timeout)
                
                if response.status_code == 200:
                    # Get devices from this page
                    page_devices = response.json()
                    
                    if page_devices:
                        all_devices.extend(page_devices)
                    
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
                    print(f"\r❌ Authentication failed. Please check your API credentials.")
                    return None
                    
                else:
                    # Handle other errors with more detailed message
                    print(f"\r❌ API Error: Status code {response.status_code} - {response.text}")
                    if retry_count < max_retries:
                        retry_count += 1
                        print(f"\rRetrying ({retry_count}/{max_retries})...", end="", flush=True)
                        time.sleep(2)  # Wait before retry
                        continue
                    else:
                        print(f"\r❌ Failed to retrieve devices after {max_retries} retries.")
                        break
                        
            except requests.exceptions.Timeout:
                if retry_count < max_retries:
                    retry_count += 1
                    print(f"\rRequest timed out. Retrying ({retry_count}/{max_retries})...", end="", flush=True)
                    time.sleep(2)  # Wait before retry
                    continue
                else:
                    print(f"\r❌ Request timed out after {max_retries} retries.")
                    break
            except requests.exceptions.ConnectionError:
                if retry_count < max_retries:
                    retry_count += 1
                    print(f"\rConnection error. Retrying ({retry_count}/{max_retries})...", end="", flush=True)
                    time.sleep(3)  # Wait longer for connection issues
                    continue
                else:
                    print(f"\r❌ Connection failed after {max_retries} retries.")
                    break
                    
        # Final status message
        if all_devices:
            print(f"\r✅ Successfully retrieved {len(all_devices)} devices total.       ")
            return all_devices
        else:
            print("\r❌ No devices were retrieved.")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"\r❌ Connection error: {e}")
        return None

# === UI UTILITIES ===

def print_docs_link():
    """
    Print a VERY prominent documentation banner that's impossible to miss
    """
    # Get terminal width
    width, _ = get_terminal_size()
    
    # Create a prominent banner with eye-catching colors and formatting
    print("\n")
    print(f"{Colors.BRIGHT_RED}{'═' * width}{Colors.RESET}")
    print(f"{Colors.BRIGHT_RED}║{' ' * (width - 2)}║{Colors.RESET}")
    
    doc_text = "📚 DOCUMENTATION AVAILABLE AT: http://localhost:8005"
    padding = (width - len(doc_text) - 2) // 2
    print(f"{Colors.BRIGHT_RED}║{' ' * padding}{Colors.BRIGHT_WHITE}{doc_text}{Colors.BRIGHT_RED}{' ' * (width - len(doc_text) - padding - 2)}║{Colors.RESET}")
    
    print(f"{Colors.BRIGHT_RED}║{' ' * (width - 2)}║{Colors.RESET}")
    print(f"{Colors.BRIGHT_RED}{'═' * width}{Colors.RESET}")
    print("\n")

def get_terminal_size():
    """Get the terminal size and handle edge cases"""
    try:
        columns, lines = shutil.get_terminal_size()
        # Set minimum sizes to ensure UI displays properly
        return max(columns, 80), max(lines, 24)
    except:
        # Default fallback values if unable to detect
        return 80, 24

def clear_screen():
    """Clear the terminal screen based on OS"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title, subtitle=None):
    """
    Print a stylish header with optional subtitle
    Uses box-drawing characters and colors for a modern look
    """
    width, _ = get_terminal_size()
    width = min(width, 100)  # Cap at 100 to avoid too wide headers
    
    # Top border with rounded corners
    print(f"\n{UI.HEADER}╭{'─' * (width - 2)}╮{Colors.RESET}")
    
    # Title (centered)
    title_padding = (width - len(title) - 2) // 2
    print(f"{UI.HEADER}│{' ' * title_padding}{UI.TITLE}{title}{Colors.RESET}{UI.HEADER}{' ' * (width - len(title) - title_padding - 2)}│{Colors.RESET}")
    
    # Subtitle if provided
    if subtitle:
        subtitle_padding = (width - len(subtitle) - 2) // 2
        print(f"{UI.HEADER}│{' ' * subtitle_padding}{UI.SUBTITLE}{subtitle}{Colors.RESET}{UI.HEADER}{' ' * (width - len(subtitle) - subtitle_padding - 2)}│{Colors.RESET}")
    
    # Bottom border with rounded corners
    print(f"{UI.HEADER}╰{'─' * (width - 2)}╯{Colors.RESET}")

def print_footer(message="Soracom Device Manager", docs_available=False):
    """Print a stylish footer with optional message"""
    width, _ = get_terminal_size()
    width = min(width, 100)  # Cap at 100 to avoid too wide footers
    
    # Create footer with message
    print(f"\n{UI.SEPARATOR}╰{'─' * (width - 2)}╯{Colors.RESET}")
    
    # Add copyright or message centered
    msg = f"• {message} •"
    padding = (width - len(msg)) // 2
    print(f"{UI.SUBTITLE}{' ' * padding}{msg}{Colors.RESET}")
    
    # Add documentation line at the bottom if available (a simple single line)
    if docs_available:
        doc_msg = "Documentation available at: http://localhost:8005"
        padding = (width - len(doc_msg)) // 2
        print(f"\n{Colors.BRIGHT_CYAN}{' ' * padding}{doc_msg}{Colors.RESET}")

def print_box(title, content, width=None):
    """
    Print a stylish box with title and content
    Used for displaying information sections
    """
    term_width, _ = get_terminal_size()
    if not width:
        width = min(term_width - 4, 90)  # Default to terminal width with margin

    # Top border with title
    print(f"{UI.HEADER}╭─ {UI.TITLE}{title} {UI.HEADER}{'─' * (width - len(title) - 4)}╮{Colors.RESET}")
    
    # Content - handle multiline content
    if isinstance(content, list):
        for line in content:
            # Truncate line if too long
            if len(line) > width - 4:
                line = line[:width - 7] + "..."
            print(f"{UI.HEADER}│ {UI.INFO}{line}{' ' * (width - len(line) - 3)}{UI.HEADER}│{Colors.RESET}")
    else:
        # Handle single string
        print(f"{UI.HEADER}│ {UI.INFO}{content}{' ' * (width - len(content) - 3)}{UI.HEADER}│{Colors.RESET}")
    
    # Bottom border
    print(f"{UI.HEADER}╰{'─' * (width - 2)}╯{Colors.RESET}")

def print_menu_item(number, text, description=None):
    """Print a styled menu item with optional description"""
    print(f"{UI.MENU_NUMBER}  {number}.{Colors.RESET} {UI.MENU_ITEM}{text}{Colors.RESET}")
    if description:
        print(f"     {UI.SUBTITLE}{description}{Colors.RESET}")

def print_status(text, status_type="info"):
    """Print a status message with appropriate icon and color"""
    if status_type == "success":
        print(f"{UI.SUCCESS}{UI.ICON_OK} {text}{Colors.RESET}")
    elif status_type == "error":
        print(f"{UI.ERROR}{UI.ICON_ERROR} {text}{Colors.RESET}")
    elif status_type == "warning":
        print(f"{UI.WARNING}{UI.ICON_WARNING} {text}{Colors.RESET}")
    else:  # info is default
        print(f"{UI.INFO}{UI.ICON_INFO} {text}{Colors.RESET}")

def print_loading(text, end="\r"):
    """Print a loading message with spinner icon"""
    print(f"{UI.LOADING}{UI.ICON_LOADING} {text}...{Colors.RESET}", end=end)

def print_data_row(label, value, icon=None, status=None):
    """Print a data row with label and value, optional icon and status"""
    # Add icon if provided
    icon_str = f"{icon} " if icon else ""
    
    # Apply status color to value if status provided
    if status == "online":
        value_color = UI.DEVICE_ONLINE
    elif status == "offline":
        value_color = UI.DEVICE_OFFLINE
    else:
        value_color = UI.DATA_VALUE
    
    print(f"{icon_str}{UI.DATA_LABEL}{label}:{Colors.RESET} {value_color}{value}{Colors.RESET}")

def print_separator(char="─", color=UI.SEPARATOR):
    """Print a separator line"""
    width, _ = get_terminal_size()
    width = min(width, 100)  # Cap width
    print(f"{color}{char * width}{Colors.RESET}")

def print_device_status(status, text=None):
    """Print device status with appropriate color"""
    if status:
        print(f"{UI.DEVICE_ONLINE}{UI.ICON_ONLINE} {text or 'Online'}{Colors.RESET}")
    else:
        print(f"{UI.DEVICE_OFFLINE}{UI.ICON_OFFLINE} {text or 'Offline'}{Colors.RESET}")

def styled_input(prompt, color=UI.INPUT_PROMPT):
    """Get input with styled prompt"""
    return input(f"{color}{prompt}{Colors.RESET} ")

def cleanup_and_exit(auth_data=None, exit_code=0):
    """Clean up resources and exit properly"""
    clear_screen()
    print_header("EXITING SORACOM DEVICE MANAGER")
    
    print_status("Cleaning up resources...", "info")
    
    # Logout from Soracom API if auth data exists
    if auth_data:
        logout(auth_data)
        print_status("Successfully logged out from Soracom API", "success")
    
    print_separator()
    print(f"\n{UI.INFO}Thank you for using the Soracom Device Manager. Goodbye!{Colors.RESET}\n")
    sys.exit(exit_code)

def draw_ascii_logo():
    """Draw a simple styled title instead of large ASCII art"""
    width, _ = get_terminal_size()
    width = min(width, 100)
    print_header("SORACOM DEVICE MANAGER")
