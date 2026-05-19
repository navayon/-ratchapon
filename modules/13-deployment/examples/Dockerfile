# ── Stage 1: Builder ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies into a separate layer for caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── Stage 2: Runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Install only runtime system dependencies (no build tools)
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy project source
COPY . .

# Collect static files (requires SECRET_KEY to be set, even as a dummy)
RUN SECRET_KEY=dummy-build-key python manage.py collectstatic --no-input

# Create a non-root user for security
RUN addgroup --system django && adduser --system --ingroup django django
USER django

EXPOSE 8000

# Use gunicorn.conf.py for configuration (see examples/gunicorn.conf.py)
CMD ["gunicorn", "myproject.wsgi:application", "--config", "gunicorn.conf.py"]
