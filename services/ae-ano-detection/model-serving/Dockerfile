# Base image
FROM python:3.10

# Work directory
WORKDIR /app

# Install and configure Poetry
RUN pip install poetry==1.5.1
RUN poetry config virtualenvs.create false

# Copy Python project file
COPY ./pyproject.toml .
COPY ./poetry.lock .

# Install dependencies
RUN poetry install --no-dev

# Copy sources
COPY src src

# Copy model
COPY ae_model.h5 .

# Environment variables
ENV ENVIRONMENT=${ENVIRONMENT}
ENV LOG_LEVEL=${LOG_LEVEL}
ENV ENGINE_URLS=${ENGINE_URLS}
ENV MAX_TASKS=${MAX_TASKS}
ENV ENGINE_ANNOUNCE_RETRIES=${ENGINE_ANNOUNCE_RETRIES}
ENV ENGINE_ANNOUNCE_RETRY_DELAY=${ENGINE_ANNOUNCE_RETRY_DELAY}

# Exposed ports
EXPOSE 80

# Switch to src directory
WORKDIR "/app/src"

# Command to run on start
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
