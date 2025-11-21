#!/bin/sh

echo "📌 Applying database migrations..."
flask db upgrade || echo "⚠️ Migrations already applied or failed"

echo "🚀 Starting App..."
exec gunicorn --bind 0.0.0.0:8000 "app:create_app()"
