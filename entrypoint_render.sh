#!/bin/sh
echo "🚀 Starting Flask with SQLite..."
exec gunicorn --bind 0.0.0.0:8000 "app:create_app()"
