# Installation Guide

This guide will help you install and set up the VST Soracom Device Manager on your system.

## Prerequisites

Before installing the VST Soracom Device Manager, ensure you have the following:

- Python 3.7 or higher
- pip (Python package installer)
- Git (optional, for cloning the repository)
- Network access to the Soracom API endpoints

## Installation Options

### Option 1: Using the run.sh Script (Recommended)

The easiest way to install and run the VST Soracom Device Manager is using the provided `run.sh` script, which automates the entire setup process:

```bash
# Make the script executable (first time only)
chmod +x run.sh

# Run the setup script
./run.sh
```

The script will automatically:
- Create a Python virtual environment if it doesn't exist
- Activate the virtual environment
- Install all required dependencies
- Start the Soracom Device Manager application

This is the recommended method for most users as it simplifies the installation and setup process.

### Option 2: Manual Installation

If you prefer to perform the installation steps manually:

1. Clone the repository or download the latest release:

```bash
# Clone the repository
git clone https://github.com/Vapor-Systems/soracom_device_manager.git

# Navigate to the project directory
cd soracom_device_manager
```

2. Create and activate a virtual environment:

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

3. Install dependencies:

```bash
pip3 install -r requirements.txt
```

4. Create a `.env` file for your Soracom credentials:

```bash
# Create an empty .env file
touch .env

# Edit the file and add your credentials
echo "# VST Soracom Device Manager Environment Configuration

# Soracom API credentials
SORACOM_EMAIL=your-email@example.com
SORACOM_PASSWORD=your-password" > .env
```

5. Start the application:

```bash
python3 main.py
```

## Verify Installation

To verify that the installation was successful:

```bash
python3 main.py --version
```

This should display the version of the VST Soracom Device Manager.

## Next Steps

After successful installation:

1. Learn about [authentication](authentication.md) with the Soracom API
2. Go through the [first steps guide](first-steps.md) to learn basic usage
