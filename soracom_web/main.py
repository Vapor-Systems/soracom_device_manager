"""
Soracom Device Manager Web App - Main Entry Point
"""
import streamlit as st
import pandas as pd
from config.settings import APP_TITLE, APP_ICON, COLOR_ONLINE, COLOR_OFFLINE
from core.auth import authenticate, logout
from services.device_service import DeviceService

# Page configuration and styling
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'auth_data' not in st.session_state:
    st.session_state['auth_data'] = None

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def login():
    """Handle the login form and authentication"""
    st.markdown("# 🛰️ SORACOM Device Manager")
    st.markdown("### Login")
    
    with st.form("login_form"):
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if not email or not password:
                st.error("Please enter both email and password")
            else:
                with st.spinner("Authenticating..."):
                    auth_data = authenticate(email, password)
                    
                    if auth_data:
                        st.session_state['auth_data'] = auth_data
                        st.session_state['logged_in'] = True
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Authentication failed. Please check your credentials.")

def show_devices():
    """Display the device listing screen"""
    # Create device service
    device_service = DeviceService(st.session_state['auth_data'])
    
    # Header
    st.markdown("# 🛰️ SORACOM Device Manager")
    
    # Sidebar
    st.sidebar.markdown("### Search")
    search_query = st.sidebar.text_input("Search devices:", placeholder="Enter name, IMSI, etc.")
    
    st.sidebar.markdown("### Filters")
    filter_option = st.sidebar.radio(
        "Device Status:",
        ["All Devices", "Online Devices", "Offline Devices"]
    )
    
    # Refresh button
    if st.sidebar.button("Refresh Data"):
        st.rerun()
    
    # Logout button
    if st.sidebar.button("Logout"):
        logout(st.session_state['auth_data'])
        st.session_state['auth_data'] = None
        st.session_state['logged_in'] = False
        st.rerun()
    
    # Get devices based on filter
    with st.spinner("Loading devices..."):
        if filter_option == "Online Devices":
            devices = device_service.get_online_devices()
            header_text = "Online Devices"
        elif filter_option == "Offline Devices":
            devices = device_service.get_offline_devices()
            header_text = "Offline Devices"
        else:
            devices = device_service.get_all_devices()
            header_text = "All Devices"
        
        # Apply search filter if query exists
        if search_query:
            search_query = search_query.lower()
            filtered_devices = []
            for device in devices:
                # Search in name, IMSI, and software version
                if (search_query in device.get_name().lower() or
                    search_query in device.get_imsi().lower() or
                    search_query in device.get_software_version().lower()):
                    filtered_devices.append(device)
            devices = filtered_devices
            header_text = f"Search Results: {header_text}"
        
        st.markdown(f"## {header_text}")
    
    # Convert to dataframe
    if devices:
        df = pd.DataFrame([device.to_dict() for device in devices])
        
        # Display devices
        st.markdown(f"Found {len(devices)} devices")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No devices found")

# Main application flow
def main():
    """Main entry point for the web application"""
    if not st.session_state['logged_in']:
        login()
    else:
        show_devices()

if __name__ == "__main__":
    main()
