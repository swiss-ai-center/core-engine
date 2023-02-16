# Base image
FROM ghcr.io/csia-pme/csia-pme-base-image:latest

# Work directory
WORKDIR /app

# Copy requirements file
COPY ./requirements.txt .

# Install dependencies
RUN pip install --requirement requirements.txt

# Copy sources
COPY src src

# Environment variables
ENV ENVIRONMENT=${ENVIRONMENT}
ENV LOG_LEVEL=${LOG_LEVEL}
ENV ENGINE_URL=${ENGINE_URL}
ENV MAX_TASKS=${MAX_TASKS}
ENV ENGINE_ANNOUNCE_RETRIES=${ENGINE_ANNOUNCE_RETRIES}
ENV ENGINE_ANNOUNCE_RETRY_DELAY=${ENGINE_ANNOUNCE_RETRY_DELAY}

# Exposed ports
EXPOSE 80

# Switch to src directory
WORKDIR "/app/src"

# Command to run on start
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--log-config", "logger/log_config.yaml"]
