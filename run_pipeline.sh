#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting ML Pipeline...${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Install/upgrade pip
echo -e "${BLUE}Upgrading pip...${NC}"
pip install --upgrade pip

# Install project dependencies
echo -e "${BLUE}Installing project dependencies...${NC}"
pip install -e .

# Create necessary directories
echo -e "${BLUE}Creating project directories...${NC}"
mkdir -p data models logs

# Run the main pipeline
echo -e "${BLUE}Running main pipeline...${NC}"
python src/main.py

# Run tests
echo -e "${BLUE}Running tests...${NC}"
python -m pytest tests/ -v

# Check if everything completed successfully
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Pipeline completed successfully!${NC}"
    echo -e "${GREEN}Results can be found in:${NC}"
    echo -e "  - Models: models/"
    echo -e "  - Data: data/"
    echo -e "  - Logs: logs/"
else
    echo -e "${RED}Pipeline failed! Check the logs for details.${NC}"
    exit 1
fi

# Optionally launch MLflow UI
read -p "Do you want to launch the MLflow UI? (y/n): " launch_mlflow
if [ "$launch_mlflow" == "y" ]; then
    echo -e "${BLUE}Launching MLflow UI at http://localhost:5000 ...${NC}"
    mlflow ui --port 5000 &
    echo -e "${GREEN}Open your browser and go to http://localhost:5000 to view experiment results.${NC}"
fi

# Deactivate virtual environment
deactivate 