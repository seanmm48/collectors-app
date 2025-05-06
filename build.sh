#!/usr/bin/env bash
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files for production
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate