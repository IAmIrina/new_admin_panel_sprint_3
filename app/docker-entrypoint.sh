#!/bin/bash

# Wait when DB Ready for connection
echo "Wait db ready to connect"
python wait_for_db.py

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Create a Superuser if it doesn't exist 
echo "Create Superuser"
python manage.py ensure_adminuser

# Collect static
echo "Collect static"
python3 manage.py collectstatic --noinput

# Start server
echo "Starting server"
uwsgi --strict --ini uwsgi.ini