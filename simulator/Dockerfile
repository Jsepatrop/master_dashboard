# Simulator Dockerfile for Master Dashboard
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy simulator code
COPY simulator.py .

# Create non-root user
RUN useradd -m -u 1000 simulator && \
    chown -R simulator:simulator /app

USER simulator

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import asyncio; print('Simulator healthy')" || exit 1

# Default command
CMD ["python", "simulator.py", "--verbose"]