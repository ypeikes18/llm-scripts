FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including PostgreSQL client and build tools
RUN apt-get update && \
    apt-get install -y \
    libpq-dev \
    gcc \
    g++ \
    make \
    cmake \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for Chroma DB
RUN mkdir -p /app/chroma_db && chmod 777 /app/chroma_db

# Create directory for environment files
RUN mkdir -p /app/env && chmod 777 /app/env

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Start command
CMD ["python", "-u", "src/agent.py"] 