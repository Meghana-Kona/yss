# Dockerfile for Railway deployment
# Base image
FROM python:3.12-slim AS base

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build dependencies (if any) and clean up
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a non‑root user for security
RUN adduser --disabled-password --gecos "" appuser
WORKDIR /app

# Copy requirements first for layer caching
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app

# Adjust ownership and switch to non‑root user
RUN chown -R appuser:appuser /app
USER appuser

# Expose the default port (Railway provides $PORT at runtime)
EXPOSE 8080

# Set the entrypoint to Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT:-8080}", "--workers", "2", "--threads", "4", "app:app"]
