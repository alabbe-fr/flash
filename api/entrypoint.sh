#!/bin/sh
set -e

# Run migrations
flask db upgrade

# Replace shell with the app process
exec python app.py
