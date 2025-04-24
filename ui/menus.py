"""
Menu systems for the Soracom Device Manager.
Enhanced with modern UI elements including colors and box drawing.
"""
import time
import os
from config.settings import Colors, UI
from core import (
    clear_screen, print_header, print_box, print_menu_item,
    print_separator, print_status, styled_input,
    get_terminal_size
)
from ui.views import display_device_list, display_device_details, display_json_view
from ui import display_terminal_ui

def device_selection_menu(devices, category_name, update_service=None, docs_available=False):
    """Menu for selecting a device and viewing its details"""
    while True:
        clear_screen()
        
        if not display_device_list(devices, category_name):
            return
        
        width, _ = get_terminal_size()
        box_width = min(width - 4, 90)
        
        # Simple instruction header
        print(f"\n{UI.TITLE}{category_name} DEVICES{Colors.RESET}")
        print(f"{UI.SUBTITLE}Enter a number (1-{len(devices)}) or b to go back{Colors.RESET}")
        print_separator()
        
        choice = styled_input(f"{UI.ICON_DEVICE} Select device:")
        
        if choice.lower() == 'b':
            break
        
        try:
            device_index = int(choice) - 1
            if 0 <= device_index < len(devices):
                selected_device = devices[device_index]
                device_action_menu(selected_device, update_service, docs_available)
            else:
                print_status(f"Invalid selection. Please enter a number between 1 and {len(devices)}.", "error")
                time.sleep(1)
        except ValueError:
            print_status("Invalid input. Please enter a number or 'b' to go back.", "error")
            time.sleep(1)

def device_action_menu(device, update_service, docs_available=False):
    """Menu for actions on a selected device with modern UI"""
    from ui.operations import device_update_menu, manage_device_tags
    from services.services import TerminalService
    from services.tag_service import TagService
    
    # Initialize the services with the same auth data
    terminal_service = TerminalService(update_service.auth_data)
    tag_service = TagService(update_service.auth_data)
    
    # Set default SSH credentials
    terminal_service.username = 'pi'
    terminal_service.password = 'b4ustart'
    
    while True:
        clear_screen()
        
        name = device.get_name()
        print_header(f"DEVICE ACTIONS", name)
        
        width, _ = get_terminal_size()
        box_width = min(width - 4, 90)
        
        # Device info without box
        is_online = device.is_online()
        status_color = UI.DEVICE_ONLINE if is_online else UI.DEVICE_OFFLINE
        status_text = "Online" if is_online else "Offline"
        
        print(f"\n{UI.TITLE}DEVICE INFORMATION{Colors.RESET}")
        print_separator()
        print(f"{UI.DATA_LABEL}Name:{Colors.RESET} {UI.DATA_VALUE}{name}{Colors.RESET}")
        print(f"{UI.DATA_LABEL}Status:{Colors.RESET} {status_color}{status_text}{Colors.RESET}")
        print(f"{UI.DATA_LABEL}S/W Version:{Colors.RESET} {UI.DATA_VALUE}{device.get_software_version()}{Colors.RESET}")
        
        # Simple actions header
        print(f"\n{UI.TITLE}AVAILABLE ACTIONS{Colors.RESET}")
        print_separator()
        
        print_menu_item(1, "View Device Information")
        print_menu_item(2, "Update Device Software")
        print_menu_item(3, "Connect to Device Terminal (SSH)")
        print_menu_item(4, "Manage Device Tags")
        print_menu_item(5, "Back to Device List (b)")
        
        print_separator()
            
        choice = styled_input(f"Your selection (1-5):")
        
        if choice == '1':
            # Show device details
            while True:
                display_device_details(device, False)  # Never show docs link on details screen
                print_separator()
                sub_choice = styled_input("Press Enter to go back or 'j' for JSON view:")
                
                if sub_choice.lower() == 'j':
                    display_json_view(device, False)  # Never show docs link on JSON view
                else:
                    break
        elif choice == '2':
            # Update device software directly
            if update_service:
                clear_screen()
                print_header("UPDATE DEVICE SOFTWARE", device.get_name())
                
                # Ask for confirmation
                print(f"\n{UI.TITLE}UPDATE CONFIRMATION{Colors.RESET}")
                print_separator()
                print(f"{UI.ICON_WARNING} This will update the device software to the latest version.")
                print(f"{UI.ICON_WARNING} The device will be temporarily offline during the update.")
                print(f"{UI.ICON_WARNING} This operation cannot be undone.")
                print_separator()
                confirmation = styled_input(f"{UI.WARNING}Are you sure you want to update {device.get_name()}? (yes/no): ")
                
                if confirmation.lower() == 'yes':
                    print_status("Starting device update process...", "info")
                    
                    # First, change the speed class to s1.fast before establishing connection
                    print_status("Changing speed class to s1.fast for faster updates", "info")
                    speed_class_changed = update_service.change_speed_class(device, "s1.fast")
                    if not speed_class_changed:
                        print_status("Failed to change speed class, proceeding anyway", "warning")
                    else:
                        print_status("Speed class changed to s1.fast", "success")
                        # Give a moment for the speed class change to take effect
                        time.sleep(2)
                    
                    # For the visible interactive session, we'll use a modified approach
                    # Create an expect script that will be run in the terminal
                    import tempfile
                    import os
                    import shutil
                    import platform
                    import subprocess
                    
                    # Start the terminal session
                    print_status(f"Connecting to {device.get_name()} via SSH...", "info")
                    connection_result = terminal_service.start_terminal_session(device)
                    
                    if not connection_result:
                        print_status("Failed to establish SSH connection for update", "error")
                        # Change speed class back to s1.slow
                        update_service.change_speed_class(device, "s1.slow")
                        styled_input("Press Enter to return to the device menu...")
                    else:
                        # Get connection info
                        hostname, port = terminal_service.get_connection_info()
                        if not hostname or not port:
                            print_status("Failed to get SSH connection details", "error")
                            terminal_service.close_terminal_session()
                            update_service.change_speed_class(device, "s1.slow")
                            styled_input("Press Enter to return to the device menu...")
                            continue
                        
                        # Check if expect is available
                        expect_path = shutil.which("expect")
                        if not expect_path:
                            print_status("Expect utility not found. Please install expect to continue.", "error")
                            terminal_service.close_terminal_session()
                            update_service.change_speed_class(device, "s1.slow")
                            styled_input("Press Enter to return to the device menu...")
                            continue
                        
                        # Create a temporary interactive script that will show the user what's happening at every step
                        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                            script_path = temp_file.name
                            temp_file.write(f"""#!/usr/bin/expect -f
# This script runs the update process for devices
spawn ssh -o StrictHostKeyChecking=no -p {port} {terminal_service.username}@{hostname}

# Send password when prompted
expect "password:"
send "{terminal_service.password}\\r"
expect "$"

send "stty -echo\\r"
expect "$"

send "echo 'Proceeding with system update...'\\r"
expect "$"

# Run the update commands sequentially, showing each step
send "echo '\\n\\n*** STEP 1: REMOVING OLD UPDATE FILES ***'\\r"
expect "$"
send "rm -rf full_panel_upgrade\\r"
expect "$"

send "echo '\\n\\n*** STEP 2: DOWNLOADING UPDATE FILES ***'\\r"
expect "$"
send "git clone https://github.com/Vapor-Systems/full_panel_upgrade\\r"
expect "$"

send "echo '\\n\\n*** STEP 3: CHANGING TO UPDATE DIRECTORY ***'\\r"
expect "$"
send "cd full_panel_upgrade\\r"
expect "$"

send "echo '\\n\\n*** STEP 4: RUNNING THE UPDATE SCRIPT ***'\\r"
expect "$"
send "echo 'The system will reboot automatically when the update completes.'\\r"
expect "$"
send "echo 'DO NOT disconnect power during this process!'\\r"
expect "$"
send "python3 updater.py\\r"

# Stay in interact mode so user can see everything happening
interact {{
    timeout 1800 {{
        puts "\\r\\nTimed out waiting for update to complete."
    }}
}}
""")
                        # Make the script executable
                        os.chmod(script_path, 0o700)
                        
                        # Clear screen before starting
                        clear_screen()
                        
                        # Display connection information
                        terminal_width = os.get_terminal_size().columns
                        print("=" * terminal_width)
                        print(f"DEVICE UPDATE: {device.get_name()} - SYSTEM UPDATE")
                        print("=" * terminal_width)
                        time.sleep(1)
                        print(f"Running automated update process on: {device.get_name()}")
                        time.sleep(1)
                        print("This process may take several minutes, especially in poor reception areas.")
                        time.sleep(2)
                        print("The screen may appear unresponsive or paused at times.")
                        time.sleep(2)
                        print("=" * terminal_width)
                        print("⚠️  PLEASE DO NOT INTERACT WITH THE UPCOMING TERMINAL ⚠️")
                        print("=" * terminal_width)
                        time.sleep(3)
                        print("Typing may interrupt the update and cause errors or device failure.")
                        time.sleep(2)
                        print("Thank you for your patience.")
                        time.sleep(1)
                        print("Establishing SSH connection now...")
                        time.sleep(1)
                        
                        try:
                            # Run the expect script
                            subprocess.run([expect_path, script_path])
                            print("\nSSH session ended.")
                        except Exception as e:
                            print(f"\nAn error occurred: {e}")
                        finally:
                            # Clean up
                            try:
                                os.unlink(script_path)
                            except:
                                pass
                            
                            # Close the terminal session
                            terminal_service.close_terminal_session()
                            print("\nTerminal session closed.")
                            
                            # Change speed class back to s1.slow
                            print_status("Changing speed class back to s1.slow", "info")
                            update_service.change_speed_class(device, "s1.slow")
                            
                        print("\nUpdate process completed. Returning to device menu...")
                        styled_input("Press Enter to continue...")
                else:
                    print_status("Update cancelled", "info")
                    time.sleep(1.5)
            else:
                print_status("Update service not available", "error")
                time.sleep(1.5)
        elif choice == '3':
            # Connect to device terminal
            print_status(f"Connecting via SSH (Username: {terminal_service.username})", "info")
            print(f"{UI.LOADING}{UI.ICON_LOADING} Establishing secure connection...{Colors.RESET}")
            
            # Try to display terminal UI directly without waiting for confirmation
            connection_result = display_terminal_ui(device, terminal_service)
            
            # If connection failed, provide manual instructions
            if not connection_result:
                clear_screen()
                print_header("TERMINAL CONNECTION GUIDE", "Manual setup instructions")
                
                width, _ = get_terminal_size()
                box_width = min(width - 4, 90)
                
                connection_steps = [
                    f"{UI.DATA_LABEL}1.{Colors.RESET} Login to the Soracom User Console",
                    f"{UI.DATA_LABEL}2.{Colors.RESET} Go to SIM Management",
                    f"{UI.DATA_LABEL}3.{Colors.RESET} Find and select the device: {UI.DATA_VALUE}{device.get_name()}{Colors.RESET}",
                    f"{UI.DATA_LABEL}4.{Colors.RESET} From the Actions menu, select 'On-demand remote access'",
                    f"{UI.DATA_LABEL}5.{Colors.RESET} Configure the port mapping:",
                    f"   {UI.DATA_LABEL}•{Colors.RESET} Port: {UI.DATA_VALUE}22{Colors.RESET}",
                    f"   {UI.DATA_LABEL}•{Colors.RESET} Duration: As needed (maximum 8 hours)",
                    f"{UI.DATA_LABEL}6.{Colors.RESET} After creating the port mapping, note the hostname and port",
                    f"{UI.DATA_LABEL}7.{Colors.RESET} Connect using your SSH client:",
                    f"   {UI.DATA_LABEL}•{Colors.RESET} SSH command: {UI.DATA_VALUE}ssh {terminal_service.username}@[hostname] -p [port]{Colors.RESET}"
                ]
                
                print_box("MANUAL CONNECTION STEPS", connection_steps, box_width)
                
                print_status("The Soracom Napter service may incur additional charges", "warning")
                
                print_separator()
                styled_input("Press Enter to return to the device menu...")
        elif choice == '4':
            # Manage device tags
            manage_device_tags(device, tag_service)
        elif choice == '5' or choice.lower() == 'b':
            return
        else:
            print_status("Invalid choice. Please enter a number between 1 and 5.", "error")
            time.sleep(1)

def search_loaded_devices_menu(device_service, update_service=None, docs_available=False):
    """Enhanced search interface with styled UI elements"""
    clear_screen()
    
    print_header("DEVICE SEARCH", "Find devices by name or S/W Version")
        
    search_input = styled_input(f"{UI.ICON_SEARCH} Enter search term (leave blank to return to main menu):")
    
    if not search_input:
        return
    
    # Display loading indicator
    print_status("Searching devices...", "info")
    matching_devices = device_service.search_loaded_devices(search_input)
    
    if not matching_devices:
        clear_screen()
        print_header("SEARCH RESULTS", f"Query: '{search_input}'")
        
        print("\nNO MATCHES FOUND")
        print_separator()
        print(f"No devices match '{search_input}'")
        
        print_separator()
            
        styled_input("Press Enter to return to main menu...")
        return
    
    # If only one device found, show its actions menu directly
    if len(matching_devices) == 1:
        device_action_menu(matching_devices[0], update_service, docs_available)
        return
    
    # If multiple devices found, display the results and allow selection
    is_exact_match = matching_devices[0].get_name().lower() == search_input.lower()
    match_type = "EXACT MATCH" if is_exact_match else "SEARCH RESULTS"
    device_selection_menu(matching_devices, f"{match_type}: '{search_input}'", update_service, docs_available)

def main_menu(device_service, update_service=None, docs_available=False):
    """Display enhanced main menu with modern UI elements"""
    # Load all devices initially
    clear_screen()
    print_header("INITIALIZING SORACOM DEVICE MANAGER")
    
    # Display a loading message
    print_status("Loading devices from Soracom API...", "info")
    print(f"{UI.LOADING}{UI.ICON_LOADING} This may take a moment to retrieve all devices...{Colors.RESET}")
    
    # Load all devices with the improved pagination
    success = device_service.load_devices()
    
    if not success:
        print_status("Failed to load devices. Please check your internet connection and API credentials.", "error")
        styled_input("Press Enter to exit...")
        return
    
    while True:
        clear_screen()
        
        width, _ = get_terminal_size()
        
        # Documentation link is now in the dashboard header box
        
        # Get the dashboard stats
        from ui.views import display_dashboard
        display_dashboard(device_service, docs_available)
        
        box_width = min(width - 4, 90)
        
        # Print a simpler main menu title right after the header
        print(f"{UI.TITLE}MAIN MENU{Colors.RESET}")
        
        # Add device counts to the menu labels directly
        print_menu_item(1, f"View All Devices ({len(device_service.get_all_devices())})")
        print_menu_item(2, f"View Online Devices ({len(device_service.get_online_devices())})")
        print_menu_item(3, f"View Offline Devices ({len(device_service.get_offline_devices())})")
        print_menu_item(4, "Search Devices")
        print_menu_item(5, "Refresh Device Data")
        print_menu_item(6, "Exit")
        
        # Documentation link moved to the top
            
        choice = styled_input("Enter your choice (1-6):")
        
        if choice == "1":
            device_selection_menu(device_service.get_all_devices(), "ALL DEVICES", update_service, docs_available)
        elif choice == "2":
            device_selection_menu(device_service.get_online_devices(), "ONLINE DEVICES", update_service, docs_available)
        elif choice == "3":
            device_selection_menu(device_service.get_offline_devices(), "OFFLINE DEVICES", update_service, docs_available)
        elif choice == "4":
            # Search loaded devices
            search_loaded_devices_menu(device_service, update_service, docs_available)
        elif choice == "5":
            # Refresh data with options for cache or force refresh
            clear_screen()
            
            print_header("REFRESH DEVICE DATA", "Choose refresh method")
            
            print(f"\n{UI.TITLE}REFRESH OPTIONS{Colors.RESET}")
                
            print_separator()
            print_menu_item("c", "Use cache if available (faster)")
            print_menu_item("a", "Force refresh from API (slower but up-to-date)")
            print_menu_item("b", "Back to main menu")
                
            refresh_choice = styled_input("Select refresh method:").lower()
            
            if refresh_choice == 'b':
                continue
                
            clear_screen()
            print_header("REFRESHING DEVICE DATA", "Updating devices")
            
            if refresh_choice == 'c':
                print_status("Loading devices with cache if available...", "info")
                success = device_service.load_devices(use_cache=True, force_refresh=False)
            else:
                print_status("Forcing refresh from Soracom API...", "info")
                success = device_service.load_devices(use_cache=False, force_refresh=True)
            
            if success:
                print_status("Device data refreshed successfully!", "success")
                counts = device_service.get_device_counts()
                print(f"📊 {counts['total']} total devices | {counts['online']} online | {counts['offline']} offline")
            else:
                print_status("Failed to refresh device data.", "error")
            
            time.sleep(2)
        elif choice == "6":
            # Add a goodbye message
            clear_screen()
            from core import draw_ascii_logo
            
            draw_ascii_logo()
            print_header("GOODBYE", "Thank you for using Soracom Device Manager")
            
            print_box("SESSION ENDED", [
                f"{UI.ICON_OK} All data has been saved",
                f"{UI.ICON_INFO} Device manager closed successfully",
                f"{UI.ICON_INFO} See you next time!"
            ], box_width)
            return  # Exit the menu loop
        else:
            print_status("Invalid choice. Please try again.", "error")
            time.sleep(1)
