# Base image
FROM python:3.10

# Install all required packages to run the model
RUN apt update && apt install --yes ffmpeg libsm6 libxext6

RUN mkdir -p /root/.deepface/weights
WORKDIR /root/.deepface/weights
RUN wget https://github.com/serengil/deepface_models/releases/download/v1.0/age_model_weights.h5
RUN wget https://github.com/serengil/deepface_models/releases/download/v1.0/facial_expression_model_weights.h5
RUN wget https://github.com/serengil/deepface_models/releases/download/v1.0/gender_model_weights.h5
RUN wget https://github.com/serengil/deepface_models/releases/download/v1.0/race_model_single_batch.h5
RUN wget https://github.com/serengil/deepface_models/releases/download/v1.0/retinaface.h5

# Work directory
WORKDIR /app

# Copy requirements file
COPY ./requirements.txt .
COPY ./requirements-all.txt .

# Install dependencies
RUN pip install --requirement requirements.txt --requirement requirements-all.txt

# Copy sources
COPY src src

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
