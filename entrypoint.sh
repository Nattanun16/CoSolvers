#!/bin/bash

# Wait for database
while ! nc -z dbs 5432; do
  sleep 0.1
done

# Run migrations from repository root
python viable_graph_project/manage.py migrate

# Collect static files
python viable_graph_project/manage.py collectstatic --noinput

# Start server
python viable_graph_project/manage.py runserver 0.0.0.0:8000
