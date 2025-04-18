#!/bin/bash

# Script to start the development environment
# This will activate the virtual environment and start the FastAPI server

set -e  # Exit on any error

# Determine the project root directory (parent of this script's directory)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_DIR="${PROJECT_DIR}/env"

# Check if virtual environment exists
if [ ! -d "${ENV_DIR}" ]; then
    echo "Virtual environment not found at ${ENV_DIR}"
    echo "Creating virtual environment..."
    python -m venv "${ENV_DIR}"
fi

# Activate virtual environment (with appropriate detection for OS)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows using Git Bash or similar
    source "${ENV_DIR}/Scripts/activate"
else
    # Linux, macOS, etc.
    source "${ENV_DIR}/bin/activate"
fi

# Install dependencies if needed
if [ ! -f "${ENV_DIR}/.dependencies_installed" ]; then
    echo "Installing dependencies..."
    pip install -r "${PROJECT_DIR}/requirements.txt"
    touch "${ENV_DIR}/.dependencies_installed"
fi

# Navigate to project directory
cd "${PROJECT_DIR}"

# Run database migrations
echo "Running database migrations..."
# Check if alembic is installed and available
if command -v alembic &> /dev/null; then
    alembic upgrade head
else
    echo "Warning: Alembic not found in PATH, skipping migrations"
fi

# Start the development server with hot reload
echo "Starting development server..."
python -m app.main

echo "Development server stopped." 