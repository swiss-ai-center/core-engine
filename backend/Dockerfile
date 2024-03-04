# Base image
FROM python:3.11

# Work directory
WORKDIR /app

# Copy requirements files
COPY ./requirements.txt .
COPY ./requirements-all.txt .

# Install dependencies
RUN pip install --requirement requirements.txt --requirement requirements-all.txt

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
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
