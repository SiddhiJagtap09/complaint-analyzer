#!/bin/sh
# Wait for DB to be ready
echo "⏳ Waiting for Postgres..."
while ! nc -z db 5432; do
  sleep 1
done
echo "✅ Postgres is up!"

# Run migrations
echo "⚡ Running migrations..."
flask db upgrade

# Start Gunicorn
echo "🚀 Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 "app:create_app()"
