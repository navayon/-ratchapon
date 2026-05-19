# Module 02 — Project Structure & Django Settings

## Learning Objectives
- Understand every file Django generates and its role
- Configure `settings.py` for development and production
- Use environment variables with `python-decouple`
- Understand Django apps and the INSTALLED_APPS concept

---

## 2.1 Full Project Anatomy

```
myproject/
│
├── manage.py                   ← CLI tool for admin tasks
├── requirements.txt            ← project dependencies
├── .env                        ← secret config (never commit!)
├── .gitignore
│
├── myproject/                  ← project package (same name as project)
│   ├── __init__.py
│   ├── settings.py             ← central configuration
│   ├── urls.py                 ← root URL configuration
│   ├── asgi.py
│   └── wsgi.py
│
├── myapp/                      ← an application
│   ├── migrations/             ← auto-generated DB migration files
│   │   └── __init__.py
│   ├── templates/              ← HTML templates (optional per-app)
│   │   └── myapp/
│   │       └── index.html
│   ├── static/                 ← CSS, JS, images (optional per-app)
│   ├── __init__.py
│   ├── admin.py                ← admin site registration
│   ├── apps.py                 ← app configuration class
│   ├── forms.py                ← form classes (you create this)
│   ├── models.py               ← database models
│   ├── tests.py                ← unit tests
│   ├── urls.py                 ← app-level URL patterns (you create)
│   └── views.py                ← view functions / classes
│
└── templates/                  ← global templates directory
    └── base.html
```

---

## 2.2 settings.py Deep Dive

Key settings every Django developer must know:

```python
# myproject/settings.py

from decouple import config   # pip install python-decouple

# ── Security ──────────────────────────────────────────────────
SECRET_KEY = config('SECRET_KEY')          # loaded from .env
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost',
                        cast=lambda v: [s.strip() for s in v.split(',')])

# ── Application definition ─────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party apps
    'rest_framework',
    # Your apps
    'myapp',
]

# ── Database ───────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',   # SQLite for development
    }
}

# ── Internationalization ───────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ── Static files ───────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'   # for collectstatic

# ── Media files ────────────────────────────────────────────────
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── Templates ─────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],   # global templates folder
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ── Login / Logout redirects ───────────────────────────────────
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
```

---

## 2.3 Using .env for Secrets

**Never** hardcode `SECRET_KEY`, database passwords, or API keys.

### `.env` file (in project root)
```
SECRET_KEY=your-very-long-random-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=sqlite:///db.sqlite3
```

### `.gitignore`
```
.env
.venv/
__pycache__/
*.pyc
db.sqlite3
media/
staticfiles/
```

### Generate a new SECRET_KEY
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 2.4 manage.py Commands Reference

```bash
# Development
python manage.py runserver            # start dev server on port 8000
python manage.py runserver 0.0.0.0:8080  # custom host:port

# Database
python manage.py makemigrations       # detect model changes → create migration
python manage.py migrate              # run pending migrations
python manage.py showmigrations       # list all migrations and status
python manage.py dbshell              # interactive database shell

# Apps & Code
python manage.py startapp <name>      # create a new Django app
python manage.py shell                # interactive Python + Django shell
python manage.py check                # verify project has no errors

# Users
python manage.py createsuperuser      # create admin user

# Static Files
python manage.py collectstatic        # gather all static files

# Tests
python manage.py test                 # run all tests
python manage.py test myapp           # run tests for a specific app
```

---

## 2.5 Multiple Settings Files (Best Practice)

For larger projects split settings by environment:

```
myproject/
└── settings/
    ├── __init__.py
    ├── base.py        ← shared settings
    ├── development.py ← extends base, DEBUG=True
    └── production.py  ← extends base, DEBUG=False, security hardened
```

```python
# settings/development.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

```bash
# Use a specific settings file
python manage.py runserver --settings=myproject.settings.development
```

---

## Exercises

1. Create a new project with `python-decouple` and move `SECRET_KEY` to a `.env` file.
2. Add a `.gitignore` that excludes `.env`, `.venv/`, and `db.sqlite3`.
3. Run `python manage.py check` — understand each line of output.
4. **Bonus:** Split settings into `base.py` and `development.py`.

---

**Next:** [Module 03 — Models & ORM →](../03-models-orm/README.md)
