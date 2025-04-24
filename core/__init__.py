"""Core functionality for the Soracom Device Manager."""

from core.core import (
    # Authentication
    authenticate, logout,
    
    # API interaction
    get_all_devices_paginated,
    
    # UI utilities
    get_terminal_size, clear_screen, print_header, print_footer, 
    print_box, print_menu_item, print_status, print_loading,
    print_data_row, print_separator, print_device_status,
    styled_input, cleanup_and_exit, draw_ascii_logo, print_docs_link
)
