#!/bin/bash
#==============================================================================
#  SORACOM DEVICE MANAGER
#  Setup and Execution Script
#==============================================================================

# Color definitions
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'  # No Color

# Set the environment name
VENV_NAME="venv"

# Check if the virtual environment already exists
if [ ! -d "$VENV_NAME" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv "$VENV_NAME"

    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: Failed to create virtual environment. Is 'python3-venv' installed?${NC}"
        exit 1
    fi
        echo -e "${GREEN}Virtual environment '${VENV_NAME}' created successfully.${NC}"
else
    echo -e "${GREEN}Using existing virtual environment.${NC}"
fi

# Activate the virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
source "$VENV_NAME/bin/activate"

if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to activate virtual environment.${NC}"
    exit 1
fi

# Install dependencies
echo -e "\n${YELLOW}Installing dependencies...${NC}"
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to install dependencies.${NC}"
    exit 1
fi

# Skip the mkdocs installation - it seems to be causing problems
echo -e "\n${YELLOW}Skipping mkdocs installation (documentation may not be available)${NC}"
# Just continue with the program execution even without mkdocs

# Create or check .env file
if [ ! -f ".env" ]; then
    echo -e "\n${YELLOW}Creating .env file from .env.example...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}Created .env file. Please edit with your Soracom credentials.${NC}"
    else
        echo -e "${YELLOW}Creating empty .env file...${NC}"
        echo "# Soracom Device Manager Environment Configuration

# Soracom API credentials
SORACOM_EMAIL=
SORACOM_PASSWORD=" > .env
        echo -e "${GREEN}Created empty .env file. Please edit with your Soracom credentials.${NC}"
    fi
else
    echo -e "\n${GREEN}Using existing .env file.${NC}"
fi

# Run the app
echo -e "\n${YELLOW}Starting Soracom Device Manager...${NC}"
python3 main.py
