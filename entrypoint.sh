#!/bin/sh
set -e

echo "Waiting for database..."
until python -c "import psycopg2; psycopg2.connect(host='${DB_HOST}', port='${DB_PORT}', user='${DB_USER}', password='${DB_PASSWORD}', dbname='${DB_NAME}')" 2>/dev/null; do
  sleep 1
done

echo "Waiting for Redis..."
until python -c "import redis; redis.Redis(host='${REDIS_HOST}', port='${REDIS_PORT:-6379}', db='${REDIS_DB:-0}').ping()" 2>/dev/null; do
  sleep 1
done

echo "Running migrations..."
alembic upgrade head

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${WEB_PORT:-8000}
