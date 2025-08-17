FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY flask-app/pyproject.toml flask-app/uv.lock* ./

# Install uv for fast dependency management
RUN pip install uv

# Install dependencies
RUN uv pip install --system -e .

# Copy application code
COPY flask-app/ ./

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Expose port (Render will inject the PORT environment variable)
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Run the application
# Note: Render provides PORT environment variable, but we'll default to 5000
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=${PORT:-5000}"]
