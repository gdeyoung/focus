FROM python:3.11-slim

LABEL maintainer="Focus"
LABEL description="Self-hosted start page with tab groups, folders, and wallpapers"
LABEL version="2.1.0"

WORKDIR /app

# Install dependencies first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application code
COPY app.py .
COPY templates/ templates/

# Create data directory with proper permissions
RUN mkdir -p /app/data/wallpaper_cache

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" || exit 1

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "30", "app:app"]
