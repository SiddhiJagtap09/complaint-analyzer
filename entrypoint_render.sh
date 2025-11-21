#!/bin/sh

echo "📌 Running migrations on startup..."
flask db upgrade || echo "⚠️ Migration failed (maybe already applied)"

echo "🚀 Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 "app:create_app()"
