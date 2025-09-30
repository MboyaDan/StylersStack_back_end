# Use a secure base image (Debian Bookworm)
FROM python:3.10-slim-bookworm

# Environment variables for better Python behavior
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Update OS packages to patch vulnerabilities
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Install build dependencies (needed for some Python packages like psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for Docker cache efficiency
COPY requirements.txt .

# Upgrade pip and install dependencies with extended timeout & retries
RUN pip install --upgrade pip \
    && pip install --default-timeout=100 --retries=5 --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI with hot reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
