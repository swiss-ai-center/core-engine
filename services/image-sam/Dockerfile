# Base image
FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime

# Install all required packages to run the model
RUN apt update && apt install --yes git wget ffmpeg libsm6 libxext6

# Work directory
WORKDIR /app

# Copy requirements file
COPY ./requirements.txt .

# Install dependencies
RUN pip install --requirement requirements.txt

# Copy sources
COPY src src

# Download the weigths
RUN wget https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth -P model/

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
