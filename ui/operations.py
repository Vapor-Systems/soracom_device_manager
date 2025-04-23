"""
Device operations for the Soracom Device Manager.
Provides terminal connections and update functionality.
"""
import os
import sys
import time
import platform
import subprocess
import threading
import shutil
import tempfile
import getpass
from config.settings import Colors, UI
from core import (
    clear_screen, print_header, print_footer, print_box, 
    print_data_row, print_separator, get_terminal_size,
    print_status, styled_input
)

# === TERMINAL OPERATIONS ===

def display_terminal_ui(device, terminal_service):
    """
    Display interactive terminal UI for device using Soracom Napter
    
    Args:
        device: The device object to connect to
        terminal_service: The terminal service to use
        
    Returns:
        bool: True if the connection was successful, False otherwise
    """
    # Start the terminal session (creates Napter port mapping)
    connection_result = terminal_service.start_terminal_session(device)
    
    # If automatic connection failed, offer manual IMSI input option
    if not connection_result:
        clear_screen()
        print_header("MANUAL IMSI CONFIGURATION")
        
        print(f"ℹ️ Connection to {device.get_name()} requires a valid IMSI.")
        print(f"ℹ️ This information may not be available from the API.")
        print(f"\nWould you like to:")
        print(f"  1. Enter IMSI manually and try again")
        print(f"  2. Return to the device menu")
        
        manual_choice = input("\nYour choice (1-2): ")
        
        if manual_choice == "1":
            # Get manual IMSI input
            print("\nEnter the IMSI for this device (15-16 digits):")
            manual_imsi = input("IMSI: ").strip()
            
            if manual_imsi and len(manual_imsi) >= 10:  # Basic validation for IMSI
                # Create a temporary device info dictionary with the manual IMSI
                device_data = device.get_raw_data()
                device_data['imsi'] = manual_imsi
                
                # Create a new device object with the updated data
                from models.device import Device
                temp_device = Device(device_data)
                
                # Try connecting again with the updated device information
                print(f"\n🔌 Attempting connection with manual IMSI: {manual_imsi}...")
                connection_result = terminal_service.start_terminal_session(temp_device)
                
                if not connection_result:
                    print("\n❌ Connection failed even with manual IMSI.")
                    print("   Returning to device menu...")
                    time.sleep(2)
                    return False
            else:
                print("\n❌ Invalid IMSI format. IMSI should be 15-16 digits.")
                print("   Returning to device menu...")
                time.sleep(2)
                return False
        else:
            # User chose to return to device menu
            return False
    
    try:
        # Get the connection information
        hostname, port = terminal_service.get_connection_info()
        
        if not hostname or not port:
            # If automatic connection created but details are missing,
            # offer manual connection option
            clear_screen()
            print_header("MANUAL CONNECTION DETAILS")
            
            print("The Napter port mapping requires manual configuration.")
            print("If you've already created a port mapping via the Soracom Console, you can enter the details below.")
            
            print("\nEnter connection details (or press Enter to cancel):")
            hostname_input = input("Hostname: ").strip()
            
            if not hostname_input:
                print("\nManual connection cancelled.")
                time.sleep(1)
                return False
                
            port_input = input("Port: ").strip()
            
            try:
                port = int(port_input)
                hostname = hostname_input
            except ValueError:
                print("\nInvalid port number.")
                time.sleep(1)
                return False
        
        # Clear screen before starting SSH session
        clear_screen()
        
        # Display connection information
        terminal_width = os.get_terminal_size().columns
        print("=" * terminal_width)
        print(f"DEVICE TERMINAL: {device.get_name()} - {device.get_imei()}")
        print("=" * terminal_width)
        print(f"Connected to: {device.get_name()} ({device.get_status_text()})")
        print(f"Type 'exit', 'quit', or 'logout' to end the session")
        print(f"Type 'help' for a list of available commands")
        print("\nEstablishing SSH connection, please wait...")
        print(f"\n🔑 Username: {terminal_service.username}")
        print(f"🔑 Hostname: {hostname}")
        print(f"🔑 Port: {port}")
        # No longer displaying password or waiting for Enter press
        time.sleep(1)  # Short pause to let user read info before connection
        
        # SSH connection approach depends on the platform
        system = platform.system()
        ssh_success = False
        
        if system == "Windows":
            # Use PuTTY on Windows if available
            putty_path = shutil.which("putty")
            if putty_path:
                cmd = [
                    putty_path, 
                    "-ssh", 
                    f"{terminal_service.username}@{hostname}",
                    "-P", str(port)
                ]
                subprocess.run(cmd)
                ssh_success = True
            else:
                # Use built-in SSH on newer Windows
                ssh_path = shutil.which("ssh")
                if ssh_path:
                    # Use standard SSH command (will prompt for password)
                    print("\n⚠️  SSH will prompt for password, please enter it when requested")
                    time.sleep(1)
                    os.system(f"ssh -o StrictHostKeyChecking=no -p {port} {terminal_service.username}@{hostname}")
                    ssh_success = True
                else:
                    print("❌ No SSH client found. Please install OpenSSH or PuTTY.")
                    time.sleep(2)
                    ssh_success = False
        else:
            # For MacOS/Linux - use expect script if available
            expect_path = shutil.which("expect")
            if expect_path:
                # Create temporary expect script
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                    script_path = temp_file.name
                    temp_file.write(f"""#!/usr/bin/expect -f
spawn ssh -o StrictHostKeyChecking=no -p {port} {terminal_service.username}@{hostname}
expect "password:"
send "{terminal_service.password}\\r"
interact
""")
                
                # Make the script executable
                os.chmod(script_path, 0o700)
                
                # Run the expect script
                try:
                    subprocess.run([expect_path, script_path])
                    ssh_success = True
                finally:
                    # Clean up the temporary file
                    os.unlink(script_path)
            else:
                # Fall back to standard SSH (will prompt for password)
                print("\n⚠️  SSH will prompt for password, please enter it when requested")
                time.sleep(1)
                os.system(f"ssh -o StrictHostKeyChecking=no -p {port} {terminal_service.username}@{hostname}")
                ssh_success = True
        
        print("\nSSH session ended.")
        
    except KeyboardInterrupt:
        print("\n⚠️  Terminal session interrupted.")
        ssh_success = False
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        ssh_success = False
    finally:
        # Clean up and close the terminal session
        terminal_service.close_terminal_session()
        print("\n✅ Terminal session ended.")
        print("   Returning to device menu...")
        time.sleep(2)
        
    return ssh_success

# === UPDATE OPERATIONS ===

def display_update_info(device):
    """Display device update information with modern UI"""
    clear_screen()
    name = device.get_name()
    print_header("UPDATE DEVICE", name)
    
    width, _ = get_terminal_size()
    box_width = min(width - 4, 90)
    
    # Device information section
    is_online = device.is_online()
    status_icon = UI.ICON_ONLINE if is_online else UI.ICON_OFFLINE
    status_color = UI.DEVICE_ONLINE if is_online else UI.DEVICE_OFFLINE
    status_text = "Online" if is_online else "Offline"
    
    print(f"\n{UI.TITLE}DEVICE INFORMATION{Colors.RESET}")
    print_separator()
    print(f"{UI.ICON_DEVICE} {UI.DATA_LABEL}Name:{Colors.RESET} {UI.DATA_VALUE}{name}{Colors.RESET}")
    print(f"{UI.ICON_INFO} {UI.DATA_LABEL}S/W Version:{Colors.RESET} {UI.DATA_VALUE}{device.get_software_version()}{Colors.RESET}")
    print(f"{UI.ICON_STATUS} {UI.DATA_LABEL}Status:{Colors.RESET} {status_color}{status_text}{Colors.RESET}")
    
    # Software information section
    print(f"\n{UI.TITLE}SOFTWARE INFORMATION{Colors.RESET}")
    print_separator()
    print(f"{UI.ICON_UPDATE} {UI.DATA_LABEL}Current Version:{Colors.RESET} {UI.DATA_VALUE}{device.get_software_version()}{Colors.RESET}")
    
    # Important notes section
    print(f"\n{UI.TITLE}IMPORTANT NOTES{Colors.RESET}")
    print_separator()
    print(f"{UI.ICON_WARNING} Updating device software may cause temporary service interruption.")
    print(f"{UI.ICON_WARNING} Make sure the device is online and has a stable connection.")
    print(f"{UI.ICON_WARNING} The update process cannot be canceled once started.")
    
    # Options section
    print(f"\n{UI.TITLE}OPTIONS{Colors.RESET}")
    print_separator()
    print(f"Enter {UI.MENU_NUMBER}u{Colors.RESET} to update the device")
    print(f"Enter {UI.MENU_NUMBER}b{Colors.RESET} to go back to device menu")
    
    print_footer()

def update_confirmation(device):
    """Display update confirmation screen with styled UI"""
    clear_screen()
    name = device.get_name()
    print_header("CONFIRM UPDATE", name)
    
    width, _ = get_terminal_size()
    
    # Device target section
    is_online = device.is_online()
    status_color = UI.DEVICE_ONLINE if is_online else UI.DEVICE_OFFLINE
    status_text = "Online" if is_online else "Offline"
    
    print(f"\n{UI.TITLE}UPDATE TARGET{Colors.RESET}")
    print_separator()
    print(f"{UI.ICON_DEVICE} {UI.DATA_LABEL}Name:{Colors.RESET} {UI.DATA_VALUE}{name}{Colors.RESET}")
    print(f"{UI.ICON_UPDATE} {UI.DATA_LABEL}S/W Version:{Colors.RESET} {UI.DATA_VALUE}{device.get_software_version()}{Colors.RESET}")
    print(f"{UI.DATA_LABEL}Status:{Colors.RESET} {status_color}{status_text}{Colors.RESET}")
    
    # Update information section
    print(f"\n{UI.TITLE}UPDATE INFORMATION{Colors.RESET}")
    print_separator()
    print(f"{UI.ICON_UPDATE} {UI.DATA_LABEL}Target Version:{Colors.RESET} {UI.DATA_VALUE}Next available version{Colors.RESET}")
    
    # Warning section
    print(f"\n{UI.TITLE}WARNING{Colors.RESET}")
    print_separator()
    print(f"{UI.ICON_WARNING} The device will be temporarily offline during the update.")
    print(f"{UI.ICON_WARNING} This operation cannot be undone.")
    print(f"{UI.ICON_WARNING} Make sure the device has sufficient battery and connectivity.")
    
    # Confirmation section
    print(f"\n{UI.TITLE}CONFIRMATION{Colors.RESET}")
    print_separator()
    print(f"Enter {UI.MENU_NUMBER}confirm{Colors.RESET} to proceed with the update")
    print(f"Enter anything else to cancel")
    
    print_footer()
    
    confirmation = styled_input(f"{UI.WARNING}Confirm update:")
    return confirmation.lower() == 'confirm'

from ui.except_handler import handle_update_exception

@handle_update_exception
def run_ssh_update_commands(terminal_service, device, update_service, skip_speed_change=False):
    """
    Connect to device via SSH and run update commands.
    Uses the same connection approach as option 3 (which works reliably).
    
    Args:
        terminal_service: The terminal service to use for SSH connection
        device: The device object to update
        update_service: The update service to use for speed class changes
        skip_speed_change: If True, skips the speed class change (assumes already done)
        
    Returns:
        bool: True if update was successful, False otherwise
    """
    from services.services import TerminalService
    import subprocess
    import tempfile
    import threading
    
    # Get connection info from the terminal service
    hostname, port = terminal_service.get_connection_info()
    if not hostname or not port:
        print_status("Failed to get SSH connection details", "error")
        return False
    
    try:
        # Change the speed class to s1.fast if not already done
        if not skip_speed_change:
            print_status("Changing speed class to s1.fast for faster updates", "info")
            speed_class_changed = update_service.change_speed_class(device, "s1.fast")
            if not speed_class_changed:
                print_status("Failed to change speed class, proceeding anyway", "warning")
            else:
                print_status("Speed class changed to s1.fast", "success")
                # Give a moment for the speed class change to take effect
                time.sleep(2)
        
        print_status("Connecting via SSH to run updates", "info")
        
        # Check for expect utility
        expect_path = shutil.which("expect")
        if not expect_path:
            print_status("Expect utility not found. Please install expect to continue.", "error")
            return False
        
        # Run the update commands
        print_status("Starting update process...", "info")
        
        # Create temporary expect script for update commands - with improved reboot detection
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as update_script:
            script_path = update_script.name
            update_script.write(f"""#!/usr/bin/expect -f
# Set longer timeout for git clone but not forever
set timeout 300

# Function to report progress
proc report_progress {{message}} {{
    puts "PROGRESS: $message"
    flush stdout
}}

# Begin connection
report_progress "Establishing SSH connection"
spawn ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 -p {port} {terminal_service.username}@{hostname}
expect {{
    timeout {{
        report_progress "Timed out waiting for password prompt"
        exit 1
    }}
    "password:" {{
        report_progress "Connected, sending password"
    }}
}}

send "{terminal_service.password}\\r"
expect {{
    timeout {{
        report_progress "Timed out waiting for shell prompt"
        exit 1
    }}
    "$" {{
        report_progress "Successfully logged in"
    }}
}}

# Clear the terminal first
report_progress "Clearing terminal display"
send "clear\\r"
expect "$"

# Remove existing upgrade directory if it exists
report_progress "Cleaning up any previous update files"
send "rm -rf full_panel_upgrade\\r"
expect {{
    timeout {{
        report_progress "Timed out waiting for rm command to complete"
        exit 1
    }}
    "$" {{
        report_progress "Cleanup complete"
    }}
}}

# Clone the repository
report_progress "Downloading update repository (this may take a few minutes)"
send "git clone https://github.com/Vapor-Systems/full_panel_upgrade\\r"
expect {{
    timeout {{
        report_progress "Git clone timed out - may still be in progress"
        exit 1
    }}
    "fatal:" {{
        report_progress "Git clone failed"
        exit 1
    }}
    "$" {{
        report_progress "Repository download complete"
    }}
}}

# Change directory
report_progress "Changing to update directory"
send "cd full_panel_upgrade\\r"
expect {{
    timeout {{
        report_progress "Timed out changing directory"
        exit 1
    }}
    "$" {{
        report_progress "Changed to update directory"
    }}
}}

# Run the update script
report_progress "Starting update script (device will reboot when complete)"
send "python3 updater.py\\r"

# Watch for device reboot or completion with expanded patterns
expect {{
    -re "([Cc]onnection closed|broken pipe|reset by peer)" {{
        report_progress "Connection closed - device is rebooting"
        puts "SYSTEM_REBOOT_DETECTED"
        exit 0
    }}
    -re "([Rr]eboot|[Ss]hutdown|[Ss]ystem is rebooting)" {{
        report_progress "Device is rebooting"
        puts "SYSTEM_REBOOT_DETECTED"
        exit 0
    }}
    eof {{
        report_progress "SSH connection closed, device is likely rebooting"
        puts "SYSTEM_REBOOT_DETECTED"
        exit 0
    }}
    timeout {{
        report_progress "Update script timed out - closing connection"
        puts "SCRIPT_TIMED_OUT"
        # Force close the connection as it might be hanging
        close
        exit 0
    }}
    "$" {{
        report_progress "Update script completed"
        puts "UPDATE_COMPLETE"
        send "exit\\r"
        expect eof
        exit 0
    }}
}}
""")
        
        # Make script executable
        os.chmod(script_path, 0o700)
        
        # Run the update script and display progress
        print(f"{UI.LOADING}{UI.ICON_LOADING} Running update commands on device...{Colors.RESET}")
        
        try:
            update_success = False
            current_progress = ""
            
            # Run the expect script and process its output
            result = subprocess.run([expect_path, script_path], capture_output=True, text=True, timeout=300)
            
            # Process the output for progress updates and success detection
            for line in result.stdout.split('\n'):
                if line.startswith("PROGRESS:"):
                    progress_msg = line.replace("PROGRESS:", "").strip()
                    print_status(progress_msg, "info")
                    current_progress = progress_msg
                    
            # Check for success or reboot indicators
            if "SYSTEM_REBOOT_DETECTED" in result.stdout:
                print_status("Update successful! System is rebooting", "success")
                update_success = True
            elif "UPDATE_COMPLETE" in result.stdout:
                print_status("Update completed successfully", "success")
                update_success = True
            elif "SCRIPT_TIMED_OUT" in result.stdout:
                print_status("Update script timed out, but may still be running on device", "warning")
                # Consider this a potential success since the device might still reboot
                update_success = True
            elif result.returncode == 0:
                print_status("Update process completed normally", "success")
                update_success = True
            else:
                print_status(f"Update process failed: {current_progress}", "error")
                update_success = False
                
        except subprocess.TimeoutExpired:
            print_status("Update process timed out. Device may still be updating.", "warning")
            # The timeout doesn't necessarily mean failure - the device might still be updating
            update_success = True
        finally:
            # Clean up temporary update script
            try:
                os.unlink(script_path)
            except:
                pass
            
            # For successful updates, we want to set the speed class back to s1.slow after a delay
            # to give the device time to reboot
            if update_success:
                print_status("Waiting for device to complete reboot...", "info")
                time.sleep(5)  # Wait a bit before changing speed class back
                print_status("Setting speed class back to s1.slow after update", "info")
                update_service.change_speed_class(device, "s1.slow")
                print_status("Update completed successfully. Connection terminated.", "success")
            else:
                # Change speed class back to s1.slow if update failed
                print_status("Changing speed class back to s1.slow", "info")
                update_service.change_speed_class(device, "s1.slow")
            
            # Close the terminal session to remove mapping (always do this regardless of success/failure)
            terminal_service.close_terminal_session()
            
        return update_success
            
    except Exception as e:
        print_status(f"Error during update process: {str(e)}", "error")
        # Change speed class back to s1.slow on error
        try:
            update_service.change_speed_class(device, "s1.slow")
        except:
            pass
        
        # Make sure to close the terminal session to remove mapping
        terminal_service.close_terminal_session()
        
        return False

def manage_device_tags(device, tag_service):
    """Display and manage tags for a device"""
    while True:
        clear_screen()
        print_header("MANAGE DEVICE TAGS", device.get_name())
        
        # Get current tags
        current_tags = tag_service.get_tags(device)
        
        print(f"\n{UI.TITLE}CURRENT TAGS{Colors.RESET}")
        print_separator()
        
        if not current_tags:
            print(f"{UI.ICON_INFO} No tags found for this device.")
        else:
            for tag_name, tag_value in current_tags.items():
                print(f"{UI.ICON_TAG} {UI.DATA_LABEL}{tag_name}:{Colors.RESET} {UI.DATA_VALUE}{tag_value}{Colors.RESET}")
        
        print(f"\n{UI.TITLE}OPTIONS{Colors.RESET}")
        print_separator()
        print(f"Enter {UI.MENU_NUMBER}a{Colors.RESET} to add a new tag")
        print(f"Enter {UI.MENU_NUMBER}u{Colors.RESET} to update an existing tag")
        print(f"Enter {UI.MENU_NUMBER}d{Colors.RESET} to delete a tag")
        print(f"Enter {UI.MENU_NUMBER}b{Colors.RESET} to go back to device menu")
        
        print_footer()
        
        choice = styled_input("Your choice:").lower()
        
        if choice == 'b':
            return
        
        elif choice == 'a':
            # Add a new tag
            clear_screen()
            print_header("ADD NEW TAG", device.get_name())
            
            try:
                tag_name = styled_input("Enter tag name (e.g., 'Note', 'Location'):").strip().strip('"')
                if not tag_name:
                    print_status("Tag name cannot be empty", "error")
                    styled_input("Press Enter to continue...")
                    continue
                    
                tag_value = styled_input("Enter tag value:").strip().strip('"')
                if not tag_value:
                    print_status("Tag value cannot be empty", "error")
                    styled_input("Press Enter to continue...")
                    continue
                
                # Call API to create/update the tag
                print_status(f"Creating tag '{tag_name}'...", "info")
                success = tag_service.put_tag(device, tag_name, tag_value)
            except Exception as e:
                print_status(f"Error creating tag: {str(e)}", "error")
                styled_input("Press Enter to continue...")
                continue
            
            if success:
                print_status(f"Tag '{tag_name}' created successfully", "success")
            else:
                print_status(f"Failed to create tag '{tag_name}'", "error")
                
            styled_input("Press Enter to continue...")
            
        elif choice == 'u':
            if not current_tags:
                print_status("No tags to update", "error")
                styled_input("Press Enter to continue...")
                continue
                
            # Update existing tag
            clear_screen()
            print_header("UPDATE TAG", device.get_name())
            
            print(f"\n{UI.TITLE}CURRENT TAGS{Colors.RESET}")
            print_separator()
            
            # Display tags with numbers for selection
            tags_list = list(current_tags.items())
            for i, (tag_name, tag_value) in enumerate(tags_list, 1):
                print(f"{i}. {UI.DATA_LABEL}{tag_name}:{Colors.RESET} {UI.DATA_VALUE}{tag_value}{Colors.RESET}")
            
            # Get tag selection
            tag_choice = styled_input(f"\nEnter tag number to update (1-{len(tags_list)}):").strip()
            try:
                tag_index = int(tag_choice) - 1
                if tag_index < 0 or tag_index >= len(tags_list):
                    raise ValueError("Invalid tag number")
                    
                selected_tag_name = tags_list[tag_index][0]
                current_value = tags_list[tag_index][1]
                
                print(f"\n{UI.DATA_LABEL}Selected Tag:{Colors.RESET} {selected_tag_name}")
                print(f"{UI.DATA_LABEL}Current Value:{Colors.RESET} {current_value}")
                
                new_value = styled_input(f"\nEnter new value for '{selected_tag_name}':").strip()
                if not new_value:
                    print_status("Tag value cannot be empty", "error")
                    styled_input("Press Enter to continue...")
                    continue
                
                # Call API to update the tag
                success = tag_service.put_tag(device, selected_tag_name, new_value)
                
                if success:
                    print_status(f"Tag '{selected_tag_name}' updated successfully", "success")
                else:
                    print_status(f"Failed to update tag '{selected_tag_name}'", "error")
                
            except (ValueError, IndexError) as e:
                print_status(f"Invalid selection: {str(e)}", "error")
            
            styled_input("Press Enter to continue...")
            
        elif choice == 'd':
            if not current_tags:
                print_status("No tags to delete", "error")
                styled_input("Press Enter to continue...")
                continue
                
            # Delete a tag
            clear_screen()
            print_header("DELETE TAG", device.get_name())
            
            print(f"\n{UI.TITLE}CURRENT TAGS{Colors.RESET}")
            print_separator()
            
            # Display tags with numbers for selection
            tags_list = list(current_tags.keys())
            for i, tag_name in enumerate(tags_list, 1):
                print(f"{i}. {UI.DATA_LABEL}{tag_name}:{Colors.RESET} {UI.DATA_VALUE}{current_tags[tag_name]}{Colors.RESET}")
            
            # Get tag selection
            tag_choice = styled_input(f"\nEnter tag number to delete (1-{len(tags_list)}):").strip()
            try:
                tag_index = int(tag_choice) - 1
                if tag_index < 0 or tag_index >= len(tags_list):
                    raise ValueError("Invalid tag number")
                    
                selected_tag_name = tags_list[tag_index]
                
                # Confirm deletion
                confirm = styled_input(f"\n{UI.WARNING}Are you sure you want to delete the tag '{selected_tag_name}'? (y/n):").lower()
                
                if confirm == 'y':
                    # Call API to delete the tag
                    success = tag_service.delete_tag(device, selected_tag_name)
                    
                    if success:
                        print_status(f"Tag '{selected_tag_name}' deleted successfully", "success")
                    else:
                        print_status(f"Failed to delete tag '{selected_tag_name}'", "error")
                else:
                    print_status("Deletion cancelled", "info")
                
            except (ValueError, IndexError) as e:
                print_status(f"Invalid selection: {str(e)}", "error")
            
            styled_input("Press Enter to continue...")
        
        else:
            print_status("Invalid option", "error")
            styled_input("Press Enter to continue...")

@handle_update_exception
def device_update_menu(device, update_service, terminal_service=None):
    """Menu for updating a device with modern UI"""
    while True:
        display_update_info(device)
        choice = styled_input("Your choice:")
        
        if choice.lower() == 'b':
            return
        
        if choice.lower() == 'u':
            if update_confirmation(device):
                # Perform the update
                clear_screen()
                print_header("INTERACTIVE UPDATE MODE", device.get_name())
                
                width, _ = get_terminal_size()
                box_width = min(width - 4, 90)
                
                # Update details section
                print(f"\n{UI.TITLE}UPDATE DETAILS{Colors.RESET}")
                print_separator()
                print(f"{UI.ICON_DEVICE} {UI.DATA_LABEL}Device:{Colors.RESET} {UI.DATA_VALUE}{device.get_name()}{Colors.RESET}")
                print(f"{UI.ICON_UPDATE} {UI.DATA_LABEL}Current Version:{Colors.RESET} {UI.DATA_VALUE}{device.get_software_version()}{Colors.RESET}")
                
                # First, change the speed class to s1.fast before establishing connection
                print_status("Changing speed class to s1.fast for faster updates", "info")
                speed_class_changed = update_service.change_speed_class(device, "s1.fast")
                if not speed_class_changed:
                    print_status("Failed to change speed class, proceeding anyway", "warning")
                else:
                    print_status("Speed class changed to s1.fast", "success")
                    # Give a moment for the speed class change to take effect
                    time.sleep(2)
                
                try:
                    # Force clear the screen again to remove any unwanted headers
                    os.system('clear' if platform.system() != 'Windows' else 'cls')
                    
                    # Use existing terminal service or create a new one
                    local_terminal_service = terminal_service
                    if not local_terminal_service:
                        from services.services import TerminalService
                        local_terminal_service = TerminalService(update_service.auth_data)
                        local_terminal_service.username = 'pi'
                        local_terminal_service.password = 'b4ustart'
                        
                    try:
                        # Start terminal session
                        connection_result = local_terminal_service.start_terminal_session(device)
                        if not connection_result:
                            print_status("Failed to establish SSH connection", "error")
                            raise Exception("Failed to establish SSH connection")
                        
                        # Let run_ssh_update_commands handle the update process
                        print_status("Executing update commands automatically...", "info")
                        
                        update_success = run_ssh_update_commands(
                            terminal_service=local_terminal_service,
                            device=device,
                            update_service=update_service,
                            skip_speed_change=True  # Speed class already changed above
                        )
                    finally:
                        # Ensure terminal service is properly cleaned up
                        if local_terminal_service and local_terminal_service.napter_session:
                            local_terminal_service.close_terminal_session()
                    
                    if update_success:
                        print(f"\n{UI.TITLE}UPDATE COMPLETED{Colors.RESET}")
                        print_separator()
                        print(f"{UI.ICON_SUCCESS} Device update completed successfully.")
                        print(f"{UI.ICON_INFO} The device will reboot to apply changes.")
                        print_separator()
                        styled_input("Press Enter to continue...")
                    else:
                        print(f"\n{UI.TITLE}UPDATE FAILED{Colors.RESET}")
                        print_separator()
                        print(f"{UI.ICON_ERROR} Device update failed.")
                        print(f"{UI.ICON_WARNING} Please check device connection and try again.")
                        print_separator()
                        styled_input("Press Enter to continue...")
                        
                except Exception as e:
                    print_status(f"Error during update: {str(e)}", "error")
                    print(f"\n{UI.TITLE}UPDATE ERROR{Colors.RESET}")
                    print_separator()
                    print(f"{UI.ICON_ERROR} An error occurred during the update process:")
                    print(f"{str(e)}")
                    print_separator()
                    styled_input("Press Enter to continue...")
                
                finally:
                    # Change speed class back to s1.slow when done
                    print_status("Changing speed class back to s1.slow", "info")
                    try:
                        update_service.change_speed_class(device, "s1.slow")
                    except Exception as e:
                        print_status(f"Failed to reset speed class: {str(e)}", "warning")
