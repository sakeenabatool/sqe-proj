FROM python:3.12-slim

ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /rental-crud

# Copy project metadata
COPY pyproject.toml poetry.lock alembic.ini ./

RUN pip install poetry
RUN poetry install --only backend --no-root --no-interaction --no-ansi

# Copy backend code
COPY backend/ backend/

RUN sed -i 's/\r$//' backend/entrypoint.sh

EXPOSE $PORT

CMD ["sh", "backend/entrypoint.sh"]
