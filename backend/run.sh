#!/bin/bash

# SIEM Backend Development Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}SIEM Security Tool - Backend${NC}"
echo "================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
    cp .env.example .env
    echo -e "${RED}IMPORTANT: Update SECRET_KEY in .env before running in production!${NC}"
fi

# Function to initialize database
init_db() {
    echo -e "${GREEN}Initializing database...${NC}"
    python init_db.py
    echo -e "${GREEN}✓ Database initialized with sample data${NC}"
}

# Function to run the server
run_server() {
    echo -e "${GREEN}Starting FastAPI server...${NC}"
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

# Function to run tests
run_tests() {
    echo -e "${GREEN}Running tests...${NC}"
    pytest tests/ -v
}

# Function to run with Docker
run_docker() {
    echo -e "${GREEN}Starting with Docker Compose...${NC}"
    docker-compose up --build
}

# Parse command line arguments
case "${1}" in
    init)
        init_db
        ;;
    run)
        run_server
        ;;
    test)
        run_tests
        ;;
    docker)
        run_docker
        ;;
    *)
        echo "Usage: $0 {init|run|test|docker}"
        echo ""
        echo "Commands:"
        echo "  init   - Initialize database with sample data"
        echo "  run    - Run the FastAPI development server"
        echo "  test   - Run tests"
        echo "  docker - Run with Docker Compose"
        exit 1
        ;;
esac
