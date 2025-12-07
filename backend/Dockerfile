FROM python:3.12-slim

ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /rental-crud

# Copy project metadata
COPY alembic.ini pyproject.toml poetry.lock ./

# Install poetry
RUN pip install poetry

# Install backend dependencies
RUN poetry config installer.max-workers 10
RUN poetry install --only backend --no-root --no-interaction --no-ansi

# Copy backend source code
COPY backend/ backend/

# Fix line endings
RUN sed -i 's/\r$//' backend/entrypoint.sh

# Railway sets $PORT dynamically — do NOT hardcode
EXPOSE $PORT

# Start FastAPI using Railway's port
ENTRYPOINT ["sh", "/rental-crud/backend/entrypoint.sh"]
