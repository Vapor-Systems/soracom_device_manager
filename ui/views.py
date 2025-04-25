"""
Visual components for the Soracom Device Manager.
Provides styled display of dashboards, device information, and data views.
"""
import os
import json
from datetime import datetime
from tabulate import tabulate
from config.settings import Colors, UI
from core import (
    clear_screen, print_header, print_footer, print_box, 
    print_data_row, print_separator, get_terminal_size,
    print_status, styled_input
)

# === DASHBOARD COMPONENTS ===

def display_dashboard(device_service, docs_available=False):
    """Display a minimal dashboard with device statistics"""
    clear_screen()
    
    # Get counts
    counts = device_service.get_device_counts()
    total_count = counts['total']
    online_count = counts['online']
    
    # Get terminal dimensions for box width
    width, _ = get_terminal_size()
    box_width = min(width - 4, 90)
    
    # Draw the header box
    _draw_header_box(box_width, total_count, online_count, docs_available)
    
    # Documentation is shown in the header box

def _draw_header_box(width, total_count, online_count, docs_available=False):
    """Helper function to draw the header box with device information"""
    # Draw top border
    print(f"\n{UI.HEADER}╭{'─' * (width - 2)}╮{Colors.RESET}")
    
    # Draw title
    title = "SORACOM DEVICE MANAGER"
    print(f"{UI.HEADER}│{UI.TITLE}{title.center(width - 2)}{Colors.RESET}{UI.HEADER}│{Colors.RESET}")
    
    # Draw device count info with colored numbers (lighter font using SUBTITLE)
    count_text = f"{total_count} devices • {online_count} online"
    count_display = f"{UI.DATA_VALUE}{total_count}{Colors.RESET}{UI.SUBTITLE} devices • " \
                    f"{UI.DEVICE_ONLINE}{online_count}{Colors.RESET}{UI.SUBTITLE} online{Colors.RESET}"
    
    # Calculate padding for centered text with color codes
    padding = (width - 2 - len(count_text)) // 2
    print(f"{UI.HEADER}│{' ' * padding}{count_display}{' ' * (width - 2 - len(count_text) - padding)}{UI.HEADER}│{Colors.RESET}")
    
    # Only add documentation link in the header box when docs_available is True (main menu only)
    if docs_available:
        doc_text = "📚 DOCUMENTATION: http://localhost:8005"
        
        # Calculate padding for centered text (accounting for the emoji and color codes)
        visible_len = len(doc_text)
        doc_padding = (width - 2 - visible_len) // 2
        
        # Ensure right padding accounts for potential rounding issues
        right_padding = width - 2 - visible_len - doc_padding
        
        # Create doc display with BRIGHT_YELLOW for DOCUMENTATION to make it stand out
        doc_display = f"📚 {Colors.BRIGHT_YELLOW}DOCUMENTATION{Colors.RESET}: http://localhost:8005"
        
        print(f"{UI.HEADER}│{' ' * doc_padding}{doc_display}{' ' * right_padding}{UI.HEADER}│{Colors.RESET}")
    
    # Draw bottom border
    print(f"{UI.HEADER}╰{'─' * (width - 2)}╯{Colors.RESET}")

# === DEVICE DISPLAY COMPONENTS ===

def display_device_list(devices, category_name):
    """Display a stylish table of devices with key information and color coding"""
    if not devices:
        clear_screen()
        
        width, _ = get_terminal_size()
        box_width = min(width - 4, 90)
        
        print_header("DEVICE LIST", category_name)
        print_box("NO DEVICES", [
            f"No devices found matching the criteria.",
            f"Try refreshing the device data from the main menu."
        ], box_width)
        
        styled_input("Press Enter to continue...")
        return False
    
    # Don't clear screen here since it's already cleared in the device_selection_menu function
    # And the documentation link is added there
    print_header("DEVICE LIST", category_name)
    
    # Prepare table data with more information
    table_data = []
    for i, device in enumerate(devices, 1):
        name = device.get_name()
        is_online = device.is_online()
        status_color = UI.DEVICE_ONLINE if is_online else UI.DEVICE_OFFLINE
        status_text = "Online" if is_online else "Offline"
        
        last_seen = device.get_last_seen()
        sw_version = device.get_software_version()
        
        # Truncate long names for better display
        if len(name) > 25:
            name = name[:22] + "..."
        
        # Format the status with color (no icon)
        colored_status = f"{status_color}{status_text}{Colors.RESET}"
        
        # Format row number with color
        colored_num = f"{UI.MENU_NUMBER}{i}{Colors.RESET}"
        
        table_data.append([colored_num, name, colored_status, sw_version, last_seen])
    
    # Print table with a nice format and colored headers
    headers = [
        f"{UI.TITLE}#{Colors.RESET}", 
        f"{UI.TITLE}Device Name{Colors.RESET}", 
        f"{UI.TITLE}Status{Colors.RESET}", 
        f"{UI.TITLE}S/W Version{Colors.RESET}", 
        f"{UI.TITLE}Last Seen{Colors.RESET}"
    ]
    
    # Use a more visually appealing table format
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
    
    # Show count information with color
    print(f"\n{UI.INFO}{UI.ICON_INFO} Found {UI.DATA_VALUE}{len(devices)}{Colors.RESET}{UI.INFO} device(s){Colors.RESET}")
    
    print_separator()
    return True

def display_device_details(device, docs_available=False):
    """Display formatted device information with styled UI components"""
    clear_screen()
    
    name = device.get_name()
    print_header(f"DEVICE DETAILS", name)
    
    raw_data = device.get_raw_data()
    width, _ = get_terminal_size()
    box_width = min(width - 4, 90)
    
    # Basic information section
    is_online = device.is_online()
    status_color = UI.DEVICE_ONLINE if is_online else UI.DEVICE_OFFLINE
    status_text = "Online" if is_online else "Offline"
    
    print(f"\n{UI.TITLE}BASIC INFORMATION{Colors.RESET}")
    print_separator()
    print(f"{UI.DATA_LABEL}Status:{Colors.RESET} {status_color}{status_text}{Colors.RESET}")
    print(f"{UI.ICON_INFO} {UI.DATA_LABEL}S/W Version:{Colors.RESET} {UI.DATA_VALUE}{device.get_software_version()}{Colors.RESET}")
    print(f"{UI.ICON_INFO} {UI.DATA_LABEL}Last Seen:{Colors.RESET} {UI.DATA_VALUE}{device.get_last_seen()}{Colors.RESET}")
    
    # Network information section
    if 'ipAddress' in raw_data:
        print(f"\n{UI.TITLE}NETWORK INFORMATION{Colors.RESET}")
        print_separator()
        print(f"{UI.ICON_INFO} {UI.DATA_LABEL}IP Address:{Colors.RESET} {UI.DATA_VALUE}{raw_data.get('ipAddress', 'Unknown')}{Colors.RESET}")
        print(f"{UI.ICON_INFO} {UI.DATA_LABEL}ICCID:{Colors.RESET} {UI.DATA_VALUE}{raw_data.get('iccid', 'Unknown')}{Colors.RESET}")
        print(f"{UI.ICON_INFO} {UI.DATA_LABEL}IMSI:{Colors.RESET} {UI.DATA_VALUE}{raw_data.get('imsi', 'Unknown')}{Colors.RESET}")
        print(f"{UI.ICON_INFO} {UI.DATA_LABEL}APN:{Colors.RESET} {UI.DATA_VALUE}{raw_data.get('apn', 'Unknown')}{Colors.RESET}")
    
    # Tags section
    if 'tags' in raw_data and raw_data['tags']:
        print(f"\n{UI.TITLE}TAGS{Colors.RESET}")
        print_separator()
        for key, value in raw_data['tags'].items():
            print(f"{UI.ICON_INFO} {UI.DATA_LABEL}{key}:{Colors.RESET} {UI.DATA_VALUE}{value}{Colors.RESET}")
    
    # Timestamps section
    if 'createdAt' in raw_data or 'lastModifiedAt' in raw_data:
        print(f"\n{UI.TITLE}TIMESTAMPS{Colors.RESET}")
        print_separator()
        if 'createdAt' in raw_data:
            created_time = datetime.fromtimestamp(int(raw_data['createdAt']) / 1000).strftime('%Y-%m-%d %H:%M:%S')
            print(f"{UI.ICON_INFO} {UI.DATA_LABEL}Created:{Colors.RESET} {UI.DATA_VALUE}{created_time}{Colors.RESET}")
        if 'lastModifiedAt' in raw_data:
            modified_time = datetime.fromtimestamp(int(raw_data['lastModifiedAt']) / 1000).strftime('%Y-%m-%d %H:%M:%S')
            print(f"{UI.ICON_INFO} {UI.DATA_LABEL}Last Modified:{Colors.RESET} {UI.DATA_VALUE}{modified_time}{Colors.RESET}")
    
    # Other information section
    covered_keys = {'name', 'imei', 'ipAddress', 'iccid', 'imsi', 'apn', 'tags', 'createdAt', 'lastModifiedAt', 'tagName', 'sessionStatus', 'online'}
    remaining_keys = set(raw_data.keys()) - covered_keys
    
    if remaining_keys:
        print(f"\n{UI.TITLE}OTHER INFORMATION{Colors.RESET}")
        print_separator()
        for key in remaining_keys:
            value = raw_data[key]
            # Format different types of values
            if isinstance(value, dict):
                print(f"{UI.ICON_INFO} {UI.DATA_LABEL}{key}:{Colors.RESET} {UI.DATA_VALUE}{len(value)} items (object){Colors.RESET}")
            elif isinstance(value, list):
                print(f"{UI.ICON_INFO} {UI.DATA_LABEL}{key}:{Colors.RESET} {UI.DATA_VALUE}{len(value)} items (list){Colors.RESET}")
            else:
                # Truncate long values
                str_value = str(value)
                if len(str_value) > 50:
                    str_value = str_value[:47] + "..."
                print(f"{UI.ICON_INFO} {UI.DATA_LABEL}{key}:{Colors.RESET} {UI.DATA_VALUE}{str_value}{Colors.RESET}")
    
    # JSON view option
    print(f"\n{UI.TITLE}JSON VIEW OPTION{Colors.RESET}")
    print_separator()
    print(f"Enter {UI.MENU_NUMBER}j{Colors.RESET} to view the complete JSON data")
    
    print_footer(docs_available=docs_available)

def display_json_view(device, docs_available=False):
    """Display the raw JSON data for a device with syntax highlighting"""
    clear_screen()
    
    name = device.get_name()
    print_header(f"JSON DATA", name)
    
    # Pretty print the JSON data with some basic syntax highlighting
    raw_data = device.get_raw_data()
    formatted_json = json.dumps(raw_data, indent=2)
    
    # Simple syntax highlighting
    lines = formatted_json.split("\n")
    highlighted_lines = []
    
    for line in lines:
        # Highlight keys (before colon)
        if ":" in line:
            key_part, value_part = line.split(":", 1)
            # Add color to the key
            line = f"{UI.DATA_LABEL}{key_part}{Colors.RESET}:{value_part}"
        
        # Highlight string values (in quotes)
        if '"' in line:
            parts = line.split('"')
            for i in range(1, len(parts), 2):  # Only odd indices will be inside quotes
                if i < len(parts):
                    parts[i] = f"{UI.DATA_VALUE}{parts[i]}{Colors.RESET}"
            line = '"'.join(parts)
        
        # Highlight numbers and booleans
        for value in ["true", "false", "null"]:
            if value in line.lower():
                line = line.replace(value, f"{Colors.BRIGHT_MAGENTA}{value}{Colors.RESET}")
                line = line.replace(value.capitalize(), f"{Colors.BRIGHT_MAGENTA}{value.capitalize()}{Colors.RESET}")
        
        # Add the line with highlighting
        highlighted_lines.append(line)
    
    # Print the highlighted JSON
    print("\n".join(highlighted_lines))
    
    print_footer("Press Enter to go back", docs_available)
    styled_input("")
