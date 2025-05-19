#!/bin/bash
# This script sets up a development environment for AVIS Engine Python API

# Ensure python3 and pip are available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3 first."
    exit 1
fi

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip and install development dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install package in development mode
pip install -e .

# Run tests to verify setup
pytest tests/ -v

echo "Development environment setup complete!"
echo "To activate the virtual environment in the future, run: source venv/bin/activate"
