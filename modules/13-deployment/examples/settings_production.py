# settings_production.py — Production settings
# ─────────────────────────────────────────────────────────────────────────────
# This file extends base settings with production-specific configuration.
#
# Project structure expected:
#   myproject/
#       settings/
#           __init__.py
#           base.py          ← shared settings (what was your original settings.py)
#           development.py   ← DEBUG=True, SQLite, console email
#           production.py    ← this file
#
# Activate with:
#   export DJANGO_SETTINGS_MODULE=myproject.settings.production
# ─────────────────────────────────────────────────────────────────────────────

from .base import *  # noqa: F401, F403
import os
import dj_database_url

# ── Core ──────────────────────────────────────────────────────────────────────
DEBUG = False

SECRET_KEY = os.environ["SECRET_KEY"]   # crash fast if missing — never use a default

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

# ── Database ──────────────────────────────────────────────────────────────────
DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL"),
        conn_max_age=600,           # persistent connections (seconds)
        conn_health_checks=True,    # validate connections before reuse
    )
}

# ── Static files (WhiteNoise serves them directly from Gunicorn) ──────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",   # must be second
    *MIDDLEWARE[2:],  # type: ignore[name-defined]  # rest of your base middleware
]

STATIC_ROOT = BASE_DIR / "staticfiles"  # type: ignore[name-defined]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ── Cache (Redis) ─────────────────────────────────────────────────────────────
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0"),
    }
}

# ── Session ───────────────────────────────────────────────────────────────────
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# ── Security headers ──────────────────────────────────────────────────────────
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")  # needed behind reverse proxy
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000          # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"

# ── Email ─────────────────────────────────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ── Logging ───────────────────────────────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "ERROR"),
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
