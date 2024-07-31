#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

source ../venv/bin/activate

echo "Activated virtual environment"

# Update Poetry dependencies
echo "Updating Poetry dependencies..."
poetry update

# Export Poetry dependencies to requirements.txt
echo "Exporting Poetry dependencies to requirements.txt..."
poetry export -f requirements.txt --output requirements.txt --without-hashes

# Update pip dependencies
echo "Updating pip dependencies..."
pip install -r requirements.txt --upgrade

# Show installed packages
echo "Currently installed packages:"
pip list

echo "Dependencies synced successfully!"