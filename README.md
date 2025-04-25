# SORACOM Device Manager

A terminal based application for managing Soracom devices.

## Installation & Usage

### 1. Ensure you have the required prerequisites:
- Python 3 installed
- python3-venv package installed (can be installed via `apt install python3-venv` on Debian/Ubuntu systems)

### 2. Clone the repository:
```bash
git clone https://github.com/Vapor-Systems/soracom_device_manager.git
```

### 3. Switch to new Soracom Device Manager directory:
```bash
cd soracom_device_manager
```

### 4. Run the application:
```bash
./run.sh
```

This script automatically handles:
- Creating a virtual environment *if needed*
- Installing all required dependencies *if they haven't already been installed*
- Launching the application
- Starting the documentation server (available at http://localhost:8005)

## Documentation

The application includes built-in documentation that is automatically served when you run the application:

- Documentation is available at http://localhost:8005 while the application is running
- A link to the documentation is prominently displayed in the main menu header
- The documentation server runs in the background and is automatically stopped when you exit the application

The documentation provides comprehensive information about using the VST Soracom Device Manager

## Project Structure

```
soracom_device_manager/
│
├── config/                  # Configuration settings
│   └── settings.py          # Application settings and constants
│
├── core/                    # Core functionality
│   ├── __init__.py
│   ├── core.py              # Authentication and API interaction
│   └── utils.py             # Utility functions including caching
│
├── models/                  # Data models
│   ├── __init__.py
│   └── device.py            # Device model with helper methods
│
├── services/                # Service layers
│   ├── __init__.py
│   ├── services.py          # Device and terminal services
│   └── tag_service.py       # Tag management service
│
├── ui/                      # User interface components
│   ├── __init__.py
│   ├── except_handler.py    # Exception handling
│   ├── menus.py             # Menu systems
│   ├── operations.py        # Device operations
│   └── views.py             # Visual components
│
├── cache/                   # Cache directory (auto-created)
├── .gitignore               # Git ignore file
├── main.py                  # Main entry point
├── README.md                # This file
└── requirements.txt         # Dependencies
```

## Logging

The application now logs information to `device_manager.log` for easier troubleshooting.

