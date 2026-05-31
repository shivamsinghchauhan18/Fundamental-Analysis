#!/bin/bash

# Exit on error
set -e

# Terminal colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0;37m' # No Color

echo -e "${BLUE}======================================================"
echo -e "   LOCAL PIPELINE & DASHBOARD RUNNER (ZERO DOCKER)"
echo -e "======================================================${NC}"

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] Python3 is not installed or not in your PATH.${NC}"
    exit 1
fi

# 1. Virtual environment setup
if [ ! -d ".venv" ]; then
    echo -e "\n${CYAN}[1/4] Creating virtual environment (.venv)...${NC}"
    python3 -m venv .venv
else
    echo -e "\n${GREEN}[✓] Virtual environment (.venv) already exists.${NC}"
fi

# Activate virtual environment
echo -e "${CYAN}Activating virtual environment...${NC}"
source .venv/bin/activate

# 2. Dependency installation
echo -e "\n${CYAN}[2/4] Installing dependencies from root requirements.txt...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# 3. Running multi-agent pipeline
echo -e "\n${CYAN}[3/4] Triggering Sequential Multi-Agent Pipeline...${NC}"
python orchestrator/orchestrator.py

echo -e "\n${GREEN}[✓] Pipeline completed successfully! Database (shared.db) populated.${NC}"

# 4. Starting visualization dashboard
echo -e "\n${CYAN}[4/4] Starting Educational FastAPI Dashboard Server on http://localhost:8000 ...${NC}"
echo -e "${GREEN}Open http://localhost:8000 in your browser to view the premium dashboard.${NC}"
echo -e "${BLUE}Press Ctrl+C to stop the dashboard server.${NC}\n"

# Run FastAPI app
python visualization-dashboard/app.py
