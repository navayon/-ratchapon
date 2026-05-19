# settings_db.py — Module 14 example
# This file shows DATABASES configuration patterns only.
# In a real project these blocks live inside settings.py (or settings/base.py).

from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# ──────────────────────────────────────────────────────────────────────────────
# Pattern 1 — SQLite (development default)
# ──────────────────────────────────────────────────────────────────────────────
DATABASES_SQLITE = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ──────────────────────────────────────────────────────────────────────────────
# Pattern 2 — PostgreSQL with individual environment variables
# Requires: pip install psycopg2-binary
# ──────────────────────────────────────────────────────────────────────────────
DATABASES_POSTGRES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql',
        'NAME':     config('DB_NAME'),
        'USER':     config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST':     config('DB_HOST', default='localhost'),
        'PORT':     config('DB_PORT', default='5432'),
        # Keep a persistent connection for up to 10 minutes
        'CONN_MAX_AGE':       600,
        # Re-validate connection before reuse (Django 4.1+)
        'CONN_HEALTH_CHECKS': True,
        'OPTIONS': {
            'connect_timeout': 10,
            # Enforce TLS in production — remove for local dev
            # 'sslmode': 'require',
        },
        'TEST': {
            'NAME': config('TEST_DB_NAME', default='test_mydb'),
        },
    }
}

# ──────────────────────────────────────────────────────────────────────────────
# Pattern 3 — PostgreSQL via DATABASE_URL (12-factor / Railway / Render / Heroku)
# Requires: pip install dj-database-url psycopg2-binary
# ──────────────────────────────────────────────────────────────────────────────
import dj_database_url  # noqa: E402 — imported here to keep patterns self-contained

DATABASES_URL = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='sqlite:///db.sqlite3'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ──────────────────────────────────────────────────────────────────────────────
# Pattern 4 — MySQL / MariaDB
# Requires: pip install mysqlclient
# ──────────────────────────────────────────────────────────────────────────────
DATABASES_MYSQL = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     config('DB_NAME'),
        'USER':     config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST':     config('DB_HOST', default='127.0.0.1'),
        'PORT':     config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset':       'utf8mb4',
            'init_command':  "SET sql_mode='STRICT_TRANS_TABLES'",
            'connect_timeout': 10,
        },
    }
}

# ──────────────────────────────────────────────────────────────────────────────
# Pattern 5 — Multiple databases (primary + read replica or analytics DB)
# Pair with a database router (see routers.py)
# ──────────────────────────────────────────────────────────────────────────────
DATABASES_MULTI = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql',
        'NAME':     config('PRIMARY_DB_NAME'),
        'USER':     config('PRIMARY_DB_USER'),
        'PASSWORD': config('PRIMARY_DB_PASSWORD'),
        'HOST':     config('PRIMARY_DB_HOST', default='localhost'),
        'PORT':     config('PRIMARY_DB_PORT', default='5432'),
        'CONN_MAX_AGE':       600,
        'CONN_HEALTH_CHECKS': True,
    },
    'analytics': {
        'ENGINE':   'django.db.backends.postgresql',
        'NAME':     config('ANALYTICS_DB_NAME'),
        'USER':     config('ANALYTICS_DB_USER'),
        'PASSWORD': config('ANALYTICS_DB_PASSWORD'),
        'HOST':     config('ANALYTICS_DB_HOST', default='localhost'),
        'PORT':     config('ANALYTICS_DB_PORT', default='5432'),
        'CONN_MAX_AGE':       600,
        'CONN_HEALTH_CHECKS': True,
    },
}

# Tell Django which routers to consult when a database alias is not explicit.
DATABASE_ROUTERS = ['analytics.routers.AnalyticsRouter']

# ──────────────────────────────────────────────────────────────────────────────
# Choosing the active pattern
# ──────────────────────────────────────────────────────────────────────────────
# In a real project you would set exactly one DATABASES dict.
# For example, switch on an environment variable:
#
#   import os
#   _backend = os.getenv('DB_BACKEND', 'sqlite')
#   if _backend == 'postgres':
#       DATABASES = DATABASES_POSTGRES
#   elif _backend == 'mysql':
#       DATABASES = DATABASES_MYSQL
#   else:
#       DATABASES = DATABASES_SQLITE
