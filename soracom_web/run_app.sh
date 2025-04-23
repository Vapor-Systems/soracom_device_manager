#!/bin/bash

# Soracom Device Manager Web App Runner Script
# This script sets up a virtual environment, installs dependencies, and runs the app

# Set the environment name
VENV_NAME="venv"

# Check if the virtual environment already exists
if [ ! -d "$VENV_NAME" ]; then
    echo "Creating virtual environment..."
    python3 -m venv $VENV_NAME
    
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment. Make sure python3-venv is installed."
        exit 1
    fi
    
    echo "Virtual environment created successfully."
else
    echo "Using existing virtual environment."
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source $VENV_NAME/bin/activate

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your Soracom credentials before running the app again."
fi

# Run the Streamlit app
echo "Starting Soracom Device Manager Web App..."
streamlit run main.py
