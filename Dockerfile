# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port (default to 5000, but Railway will override with PORT env var)
EXPOSE 5000

# Run the application
# Use shell form to allow PORT environment variable expansion
CMD gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 4 --timeout 120 --access-logfile - --error-logfile - wsgi:app
