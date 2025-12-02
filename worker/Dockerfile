FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared library
COPY shared /app/shared

# Copy worker code
COPY worker /app/worker

# Set python path to include /app so we can import shared
ENV PYTHONPATH=/app

# Expose port (Cloud Run expects 8080 by default)
ENV PORT=8080

# Command to run the worker
CMD ["uvicorn", "worker.main:app", "--host", "0.0.0.0", "--port", "8080"]
