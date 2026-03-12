# Base image
FROM ghcr.io/astral-sh/uv:0.8.15 AS uv
FROM python:3.11

# Install uv
COPY --from=uv /uv /uvx /bin/

# Keep the virtual environment outside bind-mounted project files
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:${PATH}"
