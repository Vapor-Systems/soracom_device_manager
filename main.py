#!/usr/bin/env python3
"""
Soracom Device Manager - Main Entry Point
"""
import signal
import sys
import subprocess
import atexit
import shutil
import time
import argparse
from config.settings import APP_VERSION
from core import clear_screen, cleanup_and_exit, authenticate
from services import DeviceService, DeviceUpdateService
from ui.menus import main_menu

# Global variables for signal handlers
auth_data = None
mkdocs_process = None

def launch_docs_server():
    """Launch the mkdocs documentation server in the background"""
    global mkdocs_process
    try:
        # Check if mkdocs is installed using subprocess.run with a timeout
        try:
            result = subprocess.run(
                ["which", "mkdocs"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                timeout=2
            )
            if result.returncode != 0:
                print("mkdocs not found. Documentation server will not be started.")
                return False
        except (subprocess.SubprocessError, FileNotFoundError):
            print("Could not verify mkdocs installation. Documentation server will not be started.")
            return False
            
        # Start mkdocs server in background (non-blocking) with a short timeout
        print("Starting documentation server...")
        try:
            mkdocs_process = subprocess.Popen(
                ["mkdocs", "serve", "--dev-addr=127.0.0.1:8005"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Give it a second to see if it crashes immediately
            time.sleep(1)
            if mkdocs_process.poll() is not None:
                print(f"Documentation server failed to start (exit code: {mkdocs_process.returncode})")
                return False
            
            print("Documentation server started. Available at http://localhost:8005")
            
            # Register a function to kill the process on exit
            atexit.register(lambda: mkdocs_process.terminate() if mkdocs_process else None)
            return True
        except Exception as e:
            print(f"Failed to start documentation server: {e}")
            return False
    except Exception as e:
        print(f"Documentation server error: {e}")
        return False

def signal_handler(sig, frame):
    """Handle Ctrl+C and other termination signals"""
    print("\n\n📣 Detected program termination signal.")
    cleanup_and_exit(auth_data)

def main():
    """Main entry point for the application"""
    global auth_data, mkdocs_process
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Soracom Device Manager")
    parser.add_argument('--version', '-v', action='store_true', help='Display version information')
    args = parser.parse_args()
    
    # Display version and exit if requested
    if args.version:
        print(f"VST Soracom Device Manager v{APP_VERSION}")
        sys.exit(0)
    
    # Register signal handlers for graceful termination
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Try to launch documentation server, but don't let it block the app if it fails
    docs_available = False
    try:
        docs_available = launch_docs_server()
        print(f"Documentation server status: {'Running' if docs_available else 'Not available'}")
    except Exception as e:
        print(f"Documentation server error (non-critical): {e}")
        docs_available = False
    
    # Clear screen and show welcome
    clear_screen()
    
    try:
        # Get credentials from environment or prompt user
        from config.settings import DEFAULT_EMAIL, DEFAULT_PASSWORD
        from getpass import getpass
        
        email = DEFAULT_EMAIL
        password = DEFAULT_PASSWORD
        
        # If credentials not provided via environment variables, prompt the user
        if not email or not password:
            print("\n🔐 Soracom Authentication Required")
            print("─" * 40)
            
            if not email:
                email = input("Email: ").strip()
            else:
                print(f"Email: {email} (from environment)")
                
            if not password:
                password = getpass("Password: ")
            else:
                print("Password: (using password from environment)")
        
        # Authenticate with Soracom
        auth_data = authenticate(email, password)
        
        if not auth_data:
            print("❌ Authentication failed. Exiting program.")
            input("\nPress Enter to exit...")
            sys.exit(1)
    except Exception as e:
        print(f"❌ An error occurred during authentication: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Initialize device service
    device_service = DeviceService(auth_data)
    
    # Initialize update service
    update_service = DeviceUpdateService(auth_data)
    
    # Show main menu - the new main menu handles loading devices
    # docs_available is already set above
    try:
        main_menu(device_service, update_service, docs_available=docs_available)
        # Clean exit if menu returns
        cleanup_and_exit(auth_data)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        cleanup_and_exit(auth_data, 1)

if __name__ == "__main__":
    main()
