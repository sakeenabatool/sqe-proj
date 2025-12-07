#!/bin/sh

# Run database migrations
poetry run alembic upgrade head

# Start API on Railway's dynamic port
poetry run uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}
