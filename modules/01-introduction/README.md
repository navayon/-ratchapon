ยั# Module 01 — Introduction to Django

## Learning Objectives
- Understand what Django is and where it fits in web development
- Understand the MTV (Model-Template-View) architecture
- Create your very first Django project and run the development server

---

## 1.1 What Is Django?

Django is a **high-level Python web framework** that encourages rapid development and clean, pragmatic design. It follows the "batteries-included" philosophy — authentication, ORM, admin interface, forms, and more are all built in.

**Key characteristics:**
- Open source, maintained since 2005
- "Don't Repeat Yourself" (DRY) principle
- Convention over configuration
- Used by Instagram, Pinterest, Mozilla, Disqus

---

## 1.2 MTV Architecture

Django uses **Model-Template-View** (MTV), which maps closely to the classic MVC pattern:

```
Browser Request
      │
      ▼
  URL Router  ──►  View (views.py)
                       │
              ┌────────┴────────┐
              ▼                 ▼
           Model            Template
         (models.py)       (.html files)
              │
              ▼
          Database
```

| Layer | File | Responsibility |
|-------|------|---------------|
| **Model** | `models.py` | Data structure & database interaction |
| **Template** | `templates/*.html` | Presentation / HTML rendering |
| **View** | `views.py` | Business logic, connects Model ↔ Template |

---

## 1.3 Creating Your First Project

```bash
# 1. Activate your virtual environment first
source .venv/bin/activate          # macOS/Linux
.venv\Scripts\Activate.ps1         # Windows

# 2. Create a new Django project
django-admin startproject mysite

# 3. Enter the project directory
cd mysite

# 4. Start the development server
python manage.py runserver
```

Open your browser at **http://127.0.0.1:8000/** — you should see the Django welcome page.

---

## 1.4 Project File Overview

```
mysite/
├── manage.py               ← command-line utility (don't edit)
└── mysite/
    ├── __init__.py
    ├── settings.py         ← all configuration lives here
    ├── urls.py             ← root URL dispatcher
    ├── asgi.py             ← ASGI entry point (async)
    └── wsgi.py             ← WSGI entry point (production)
```

---

## 1.5 Creating Your First App

A **project** is the whole website. An **app** is one piece of functionality (blog, store, accounts…).

```bash
python manage.py startapp hello
```

This creates:
```
hello/
├── admin.py
├── apps.py
├── migrations/
│   └── __init__.py
├── models.py
├── tests.py
└── views.py
```

**Register the app** in `mysite/settings.py`:
```python
INSTALLED_APPS = [
    # ... default apps ...
    'hello',          # add your app here
]
```

---

## 1.6 Hello, World!

### `hello/views.py`
```python
from django.http import HttpResponse


def index(request):
    return HttpResponse("<h1>Hello, Django World!</h1>")
```

### `hello/urls.py` (create this file)
```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]
```

### `mysite/urls.py` (add include)
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hello/', include('hello.urls')),
]
```

Visit **http://127.0.0.1:8000/hello/** to see your first page.

---

## Exercises

1. Create a new project called `learningdjango` and run the dev server.
2. Create an app called `pages` with a view that returns `<h1>Welcome to Django 101</h1>`.
3. Map it to the root URL `/` so it appears on the home page.
4. **Bonus:** Return the current date/time in the response using Python's `datetime` module.

---

## Key Takeaways

- `django-admin startproject` creates a new project skeleton
- `python manage.py startapp` creates a new application
- Apps must be added to `INSTALLED_APPS` in `settings.py`
- URL routing: root `urls.py` → app `urls.py` → view function

**Next:** [Module 02 — Project Structure →](../02-project-structure/README.md)
