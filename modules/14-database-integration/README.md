# Module 14 — Database Integration

## Learning Objectives
- Configure Django to connect to different database backends (SQLite, PostgreSQL, MySQL)
- Use environment variables to keep credentials out of source code
- Understand Django's database connection options and connection pooling
- Route models to multiple databases using database routers
- Load initial data with fixtures and data migrations
- Execute raw SQL when the ORM is not sufficient

---

## 14.1 Django's DATABASES Setting

All database configuration lives in the `DATABASES` dictionary inside `settings.py`.

```python
# settings.py — default SQLite (development)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### Supported built-in backends

| Backend string | Database |
|---|---|
| `django.db.backends.sqlite3` | SQLite (file-based, no server needed) |
| `django.db.backends.postgresql` | PostgreSQL |
| `django.db.backends.mysql` | MySQL / MariaDB |
| `django.db.backends.oracle` | Oracle |

---

## 14.2 Connecting to PostgreSQL

### Install the driver
```bash
pip install psycopg2-binary   # development
pip install psycopg2          # production (compiled, faster)
```

### Minimal settings
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'USER': 'myuser',
        'PASSWORD': 'secret',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

> **Never hard-code credentials.** Use environment variables or a secrets manager instead (see §14.3).

---

## 14.3 Using Environment Variables for Credentials

### Option A — python-decouple (already in requirements.txt)
```python
# settings.py
from decouple import config

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':     config('DB_NAME'),
        'USER':     config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST':     config('DB_HOST', default='localhost'),
        'PORT':     config('DB_PORT', default='5432'),
    }
}
```

### .env file (never commit to git)
```
DB_NAME=mydb
DB_USER=myuser
DB_PASSWORD=secret
DB_HOST=localhost
DB_PORT=5432
```

### Option B — dj-database-url (single DATABASE_URL string)
```bash
pip install dj-database-url
```

```python
import dj_database_url
from decouple import config

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='sqlite:///db.sqlite3'),
        conn_max_age=600,   # keep connection open for 600 s (connection pooling)
    )
}
```

```
# .env
DATABASE_URL=postgresql://myuser:secret@localhost:5432/mydb
```

---

## 14.4 Connection Options

These keys can be added inside any database dictionary to tune behaviour:

```python
DATABASES = {
    'default': {
        'ENGINE':       'django.db.backends.postgresql',
        'NAME':         config('DB_NAME'),
        'USER':         config('DB_USER'),
        'PASSWORD':     config('DB_PASSWORD'),
        'HOST':         config('DB_HOST', default='localhost'),
        'PORT':         config('DB_PORT', default='5432'),
        # ── Tuning ──────────────────────────────────────────────
        'CONN_MAX_AGE':         600,        # seconds; 0 = close after each request
        'CONN_HEALTH_CHECKS':   True,       # validate connection before reuse (Django 4.1+)
        'OPTIONS': {
            'connect_timeout': 10,          # seconds before giving up on connection
            'sslmode': 'require',           # enforce TLS in production
        },
        'TEST': {
            'NAME': 'test_mydb',            # custom name for the test database
        },
    }
}
```

---

## 14.5 Connecting to MySQL / MariaDB

```bash
pip install mysqlclient
```

```python
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     config('DB_NAME'),
        'USER':     config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST':     config('DB_HOST', default='127.0.0.1'),
        'PORT':     config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

---

## 14.6 Multiple Databases

Django can connect to several databases simultaneously.

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('PRIMARY_DB_NAME'),
        'USER': config('PRIMARY_DB_USER'),
        'PASSWORD': config('PRIMARY_DB_PASSWORD'),
        'HOST': config('PRIMARY_DB_HOST', default='localhost'),
        'PORT': '5432',
    },
    'analytics': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('ANALYTICS_DB_NAME'),
        'USER': config('ANALYTICS_DB_USER'),
        'PASSWORD': config('ANALYTICS_DB_PASSWORD'),
        'HOST': config('ANALYTICS_DB_HOST', default='localhost'),
        'PORT': '5432',
    },
}
```

### Querying a specific database
```python
# Use the `using()` queryset method
from blog.models import Post

posts = Post.objects.using('analytics').all()
```

### Database routers
Routers automatically direct models to the correct database without manually calling `.using()`. See `examples/routers.py` for a full implementation.

```python
# settings.py
DATABASE_ROUTERS = ['blog.routers.AnalyticsRouter']
```

---

## 14.7 Migrations with Multiple Databases

```bash
# Apply to the default database
python manage.py migrate

# Apply to a specific database
python manage.py migrate --database=analytics

# Create migrations as usual — routers control which DB they target
python manage.py makemigrations
```

---

## 14.8 Fixtures — Loading Initial Data

Fixtures are JSON (or YAML/XML) dumps of model data useful for seeding a database.

### Create a fixture from existing data
```bash
python manage.py dumpdata blog.Category --indent 2 > blog/fixtures/categories.json
```

### Load a fixture
```bash
python manage.py loaddata categories.json
```

### Example fixture file
```json
[
  {
    "model": "blog.category",
    "pk": 1,
    "fields": {
      "name": "Django",
      "slug": "django"
    }
  },
  {
    "model": "blog.category",
    "pk": 2,
    "fields": {
      "name": "Python",
      "slug": "python"
    }
  }
]
```

Django looks for fixture files in:
1. Each app's `fixtures/` directory
2. Paths listed in `FIXTURE_DIRS` in settings

---

## 14.9 Data Migrations

Use data migrations to programmatically seed or transform data as part of the migration history.

```bash
python manage.py makemigrations --empty blog --name seed_categories
```

```python
# blog/migrations/0005_seed_categories.py
from django.db import migrations


def seed_categories(apps, schema_editor):
    Category = apps.get_model('blog', 'Category')
    db_alias = schema_editor.connection.alias
    Category.objects.using(db_alias).bulk_create([
        Category(name='Django', slug='django'),
        Category(name='Python', slug='python'),
    ])


def unseed_categories(apps, schema_editor):
    Category = apps.get_model('blog', 'Category')
    db_alias = schema_editor.connection.alias
    Category.objects.using(db_alias).filter(
        slug__in=['django', 'python']
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_previous_migration'),
    ]

    operations = [
        migrations.RunPython(seed_categories, reverse_code=unseed_categories),
    ]
```

---

## 14.10 Raw SQL

Use raw SQL only when the ORM cannot express the query efficiently.

```python
from django.db import connection

# Raw query returning model instances
posts = Post.objects.raw('SELECT * FROM blog_post WHERE status = %s', ['published'])
for post in posts:
    print(post.title)

# Arbitrary SQL with a cursor
def get_published_count():
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM blog_post WHERE status = %s",
            ['published']
        )
        row = cursor.fetchone()
    return row[0]
```

> **Security:** Always pass values as query parameters (`%s`), never via string formatting. This prevents SQL injection.

---

## 14.11 Quick-Reference Checklist

| Step | Command / Action |
|---|---|
| Install driver | `pip install psycopg2-binary` |
| Add `.env` entries | `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` |
| Update `DATABASES` in `settings.py` | Use `config()` or `dj_database_url` |
| Add `.env` to `.gitignore` | `echo ".env" >> .gitignore` |
| Run migrations | `python manage.py migrate` |
| Verify connection | `python manage.py dbshell` |
| Seed data | `python manage.py loaddata <fixture>` |

---

## Example Files

| File | Description |
|---|---|
| `examples/settings_db.py` | Full `DATABASES` configuration examples for SQLite, PostgreSQL, MySQL, and multiple databases |
| `examples/routers.py` | Database router that directs `analytics` app models to a secondary database |
| `examples/initial_data.json` | Sample fixture file for the `blog.Category` model |
