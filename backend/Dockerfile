# Base image
FROM ghcr.io/astral-sh/uv:0.8.15 AS uv
FROM python:3.11

# Work directory
WORKDIR /app

# Install uv
COPY --from=uv /uv /uvx /bin/

# Keep the virtual environment outside the project tree
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

# Copy dependency definition and lockfile
COPY ./pyproject.toml .
COPY ./uv.lock .

# Install dependencies in a local virtual environment
RUN uv sync --frozen --no-dev --no-install-project

# Copy sources
COPY src src

# Environment variables
ENV ENVIRONMENT=${ENVIRONMENT}
ENV LOG_LEVEL=${LOG_LEVEL}
ENV DATABASE_URL=${DATABASE_URL}
ENV DATABASE_CONNECT_ARGS=${DATABASE_CONNECT_ARGS}
ENV S3_ACCESS_KEY_ID=${S3_ACCESS_KEY_ID}
ENV S3_SECRET_ACCESS_KEY=${S3_SECRET_ACCESS_KEY}
ENV S3_REGION=${S3_REGION}
ENV S3_HOST=${S3_HOST}
ENV S3_BUCKET=${S3_BUCKET}
ENV CHECK_SERVICES_AVAILABILITY_INTERVAL=${CHECK_SERVICES_AVAILABILITY_INTERVAL}

# Exposed ports
EXPOSE 80

# Switch to src directory
WORKDIR "/app/src"

# Command to run on start
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
