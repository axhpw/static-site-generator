#!/bin/bash

# Fail immediately if anything fails
set -e

echo "Starting deployment script"

# Change working directory to project directory
cd /home/axhpw/Documents/py-projects/personal-site
echo "Working directory: $PWD"

# Activate the virtual environment
echo "Activating virtual environment..."
source ./.venv/bin/activate

# Run static site generator
echo "Building site..."
python generate.py --force

# Deploy to remote server
echo "Deploying site..."
rsync -avz --delete output/ root@157.230.60.104:/usr/share/nginx/html/

# Deactivate virtual environment
deactivate

echo "Deployment complete!"