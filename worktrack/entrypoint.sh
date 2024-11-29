#!/bin/sh

PG_HOST="postgresql"  # Changed from localhost to service name
PG_PORT="5432"

MAX_RETRIES=30
RETRY_INTERVAL=1

i=0
while [ $i -lt $MAX_RETRIES ]; do
    if nc -z -v -w 1 $PG_HOST $PG_PORT 2>/dev/null; then
        echo "PostgreSQL is ready to accept connections"
        break
    else
        i=$((i + 1))  # Fixed increment
        sleep $RETRY_INTERVAL
    fi
done

# Create necessary directories
mkdir -p /app/static /app/media /app/logs
chmod -R 777 /app/logs /app/static /app/media

# Create log file
touch /app/logs/django.log
chmod 666 /app/logs/django.log

# Apply migrations
python manage.py makemigrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Create initial data
python manage.py create_admin
python manage.py create_company_information
python manage.py create_test_staff 10

exec "$@"