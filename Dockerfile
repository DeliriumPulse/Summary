# Multi-stage Dockerfile for Telegram Chat Summarizer Bot
FROM python:3.11-slim AS base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Create data directory for database
RUN mkdir -p /app/data

# Create non-root user for security
RUN useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app

USER botuser

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

# Health check (not applicable for long-polling bot, but kept for reference)
# HEALTHCHECK --interval=60s --timeout=5s --start-period=10s --retries=3 \
#   CMD python -c "import sys; sys.exit(0)"

# Run the bot
CMD ["python", "src/main.py"]
