# Module 13 — Deployment Basics

## Learning Objectives
- Understand the difference between development and production settings
- Configure Django for production (security, static files, database)
- Serve Django with Gunicorn
- Deploy to a free cloud platform (Railway or Render)
- Set up a basic CI/CD mindset

---

## 13.1 Development vs Production

| Setting | Development | Production |
|---------|------------|-----------|
| `DEBUG` | `True` | `False` — MUST be False |
| `SECRET_KEY` | Any value | Long, random, secret |
| `ALLOWED_HOSTS` | `localhost`, `127.0.0.1` | Your domain name |
| Database | SQLite | PostgreSQL (recommended) |
| Static files | Served by Django | Served by Nginx / WhiteNoise / CDN |
| HTTPS | Not required | Required |

---

## 13.2 Production Settings

```python
# myproject/settings/production.py
from .base import *
import os

DEBUG = False

SECRET_KEY = os.environ['SECRET_KEY']   # never hardcode in production

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# ── Database: PostgreSQL ───────────────────────────────
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
    )
}

# ── Static files with WhiteNoise ───────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # add after SecurityMiddleware
    *MIDDLEWARE[1:],
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ── Security headers ───────────────────────────────────
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### Required packages for production
```bash
pip install gunicorn whitenoise dj-database-url psycopg2-binary
pip freeze > requirements.txt
```

---

## 13.3 Gunicorn

Gunicorn is the production WSGI server (replaces Django's built-in `runserver`).

```bash
# Basic usage
gunicorn myproject.wsgi:application

# With workers and port
gunicorn myproject.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --log-level info
```

**Rule of thumb for workers:** `(2 × CPU cores) + 1`

---

## 13.4 Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --no-input

EXPOSE 8000

CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
```

### `.dockerignore`
```
.venv/
.env
__pycache__/
*.pyc
db.sqlite3
media/
staticfiles/
.git/
```

---

## 13.5 Deploying to Render (Free Tier)

1. Push your project to GitHub.

2. Create a `render.yaml` in the project root:

```yaml
# render.yaml
services:
  - type: web
    name: django-101-blog
    env: python
    buildCommand: "pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate"
    startCommand: "gunicorn myproject.wsgi:application"
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: "False"
      - key: ALLOWED_HOSTS
        value: ".onrender.com"
      - key: DATABASE_URL
        fromDatabase:
          name: django-101-db
          property: connectionString

databases:
  - name: django-101-db
    databaseName: django101
    user: django101
```

3. Go to [render.com](https://render.com) → New Web Service → connect your GitHub repo.

---

## 13.6 Deploying to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and init
railway login
railway init
railway up

# Set environment variables
railway variables set SECRET_KEY="your-secret-key"
railway variables set DEBUG=False
railway variables set ALLOWED_HOSTS=".railway.app"
```

---

## 13.7 Pre-deployment Checklist

```bash
# Run Django's deployment checklist
python manage.py check --deploy

# Expected output should be all clear, or show only non-critical warnings
```

| Item | Command / Action |
|------|-----------------|
| Migrate database | `python manage.py migrate` |
| Collect static files | `python manage.py collectstatic` |
| Create superuser | `python manage.py createsuperuser` |
| Set `DEBUG=False` | In production env vars |
| Set `SECRET_KEY` | Strong random key in env vars |
| Set `ALLOWED_HOSTS` | Your production domain |
| Enable HTTPS | Via platform or Nginx |
| Run `check --deploy` | Should pass all checks |

---

## 13.8 Logging in Production

```python
# settings/production.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'ERROR'),
            'propagate': False,
        },
    },
}
```

---

## Exercises

1. Create a `settings/production.py` that sets `DEBUG=False` and reads `SECRET_KEY` from an env var.
2. Install `gunicorn` and `whitenoise`. Run `gunicorn myproject.wsgi:application` locally.
3. Run `python manage.py check --deploy` and fix all warnings.
4. Write a `Dockerfile` for your project.
5. **Bonus:** Deploy to Render or Railway and access your live app!

---

**Congratulations! You've completed the Django 101 course.**

[← Back to Course Overview](../../README.md) | [Capstone Project →](../../capstone-blog-project/README.md)
