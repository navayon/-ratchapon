# Django 101 — From Basics to Intermediate

> A structured, hands-on course covering Django fundamentals through intermediate concepts.  
> Each module includes explanations, code examples, and exercises.

---

## Table of Contents

1. [About This Course](#about-this-course)
2. [Prerequisites](#prerequisites)
3. [IDE & Extension Setup](#ide--extension-setup)
4. [Environment Setup — macOS](#environment-setup--macos)
5. [Environment Setup — Windows](#environment-setup--windows)
6. [Course Modules](#course-modules)
7. [Capstone Project](#capstone-project)

---

## About This Course

This course teaches Django from the ground up, progressing into intermediate patterns used in real-world projects. By the end you will be able to:

- Build multi-page Django web applications
- Work with databases using Django's ORM
- Create forms, handle user authentication, and manage static/media files
- Write class-based views and REST APIs with Django REST Framework
- Write basic tests and deploy a Django application

**Level:** Basic → Intermediate  
**Language:** Python 3.11+  
**Framework:** Django 5.x

---

## Prerequisites

### Knowledge
- Basic Python (variables, functions, loops, classes)
- Basic understanding of HTML & CSS
- Familiarity with the command line / terminal

### Software
| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.11 or higher | [python.org/downloads](https://www.python.org/downloads/) |
| pip | bundled with Python | package installer |
| Git | any recent | [git-scm.com](https://git-scm.com/) |
| VS Code | latest | recommended IDE |

---

## IDE & Extension Setup

### Visual Studio Code (Recommended)

Install VS Code from [code.visualstudio.com](https://code.visualstudio.com/).

#### Essential Extensions

| Extension | Publisher | Purpose |
|-----------|-----------|---------|
| **Python** | Microsoft | Python language support, IntelliSense, linting |
| **Pylance** | Microsoft | Fast type checking & auto-complete |
| **Django** | Baptiste Darthenay | Django template syntax highlighting & snippets |
| **Ruff** | Astral Software | Fast Python linter & formatter |
| **SQLite Viewer** | Florian Klampfer | Browse SQLite `.db` files visually |
| **DotENV** | mikestead | Syntax highlighting for `.env` files |
| **GitLens** | GitKraken | Enhanced Git integration |
| **REST Client** | Huachao Mao | Test API endpoints directly in VS Code |

#### Installing Extensions via Command Line
```bash
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension batisteo.vscode-django
code --install-extension charliermarsh.ruff
code --install-extension qwtel.sqlite-viewer
code --install-extension mikestead.dotenv
code --install-extension eamodio.gitlens
code --install-extension humao.rest-client
```

#### Recommended VS Code Settings (`.vscode/settings.json`)
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff"
  },
  "files.associations": {
    "**/*.html": "django-html"
  },
  "emmet.includeLanguages": {
    "django-html": "html"
  }
}
```

---

## Environment Setup — macOS

### Step 1 — Install Python

```bash
# Check if Python is already installed
python3 --version

# Recommended: install via Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.11
```

### Step 2 — Create a Virtual Environment

```bash
# Navigate to your project folder
cd ~/Documents/django-101

# Create a virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Your prompt should now show (.venv)
```

### Step 3 — Install Django

```bash
# With the virtual environment active:
pip install django

# Verify installation
python -m django --version
```

### Step 4 — Install Course Dependencies

```bash
pip install -r requirements.txt
```

### Step 5 — Open in VS Code

```bash
code .
# Press Cmd+Shift+P → "Python: Select Interpreter" → choose .venv
```

### Deactivate the Virtual Environment

```bash
deactivate
```

---

## Environment Setup — Windows

### Step 1 — Install Python

1. Download Python 3.11+ from [python.org/downloads](https://www.python.org/downloads/)
2. Run the installer — **check "Add Python to PATH"** before clicking Install
3. Verify installation:

```powershell
python --version
pip --version
```

> **Tip:** Use **PowerShell** or **Windows Terminal** for all commands below.

### Step 2 — Create a Virtual Environment

```powershell
# Navigate to your project folder
cd C:\Users\YourName\Documents\django-101

# Create a virtual environment
python -m venv .venv

# Activate it (PowerShell)
.venv\Scripts\Activate.ps1

# If you get an execution policy error, run first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3 — Install Django

```powershell
# With the virtual environment active:
pip install django

# Verify
python -m django --version
```

### Step 4 — Install Course Dependencies

```powershell
pip install -r requirements.txt
```

### Step 5 — Open in VS Code

```powershell
code .
# Press Ctrl+Shift+P → "Python: Select Interpreter" → choose .venv
```

### Deactivate the Virtual Environment

```powershell
deactivate
```

---

## Course Modules

| # | Module | Topics Covered | Difficulty |
|---|--------|---------------|------------|
| 01 | [Introduction to Django](./modules/01-introduction/README.md) | What is Django, MTV pattern, first project | ⭐ |
| 02 | [Project Structure](./modules/02-project-structure/README.md) | Files & folders, apps, settings, manage.py | ⭐ |
| 03 | [Models & ORM](./modules/03-models-orm/README.md) | Models, migrations, QuerySet API | ⭐⭐ |
| 04 | [Views & URLs](./modules/04-views-urls/README.md) | Function-based views, URL routing, path converters | ⭐⭐ |
| 05 | [Templates](./modules/05-templates/README.md) | DTL syntax, inheritance, filters, tags | ⭐⭐ |
| 06 | [Forms](./modules/06-forms/README.md) | Django forms, ModelForms, validation | ⭐⭐ |
| 07 | [Admin Interface](./modules/07-admin-interface/README.md) | Registering models, customising admin | ⭐ |
| 08 | [Static & Media Files](./modules/08-static-media/README.md) | Static files, file uploads, MEDIA settings | ⭐⭐ |
| 09 | [Authentication](./modules/09-authentication/README.md) | Login, logout, signup, permissions | ⭐⭐⭐ |
| 10 | [Class-Based Views](./modules/10-class-based-views/README.md) | ListView, DetailView, CreateView, mixins | ⭐⭐⭐ |
| 11 | [REST API with DRF](./modules/11-rest-api/README.md) | Serializers, APIView, ViewSets, routers | ⭐⭐⭐ |
| 12 | [Testing](./modules/12-testing/README.md) | Unit tests, TestCase, Client, mocking | ⭐⭐⭐ |
| 13 | [Deployment](./modules/13-deployment/README.md) | Production settings, Gunicorn, Nginx basics, Railway/Render | ⭐⭐⭐ |

---

## Capstone Project

[Blog Platform](./capstone-blog-project/README.md) — Build a fully functional blog with:
- User registration and login
- Create / edit / delete posts (with rich text)
- Categories and tags
- Comment system
- REST API endpoint
- Deployed to a free cloud platform

---

## Quick Reference

```bash
# Most-used Django commands
python manage.py startproject <name>   # create a new project
python manage.py startapp <name>       # create a new app
python manage.py runserver             # start dev server (localhost:8000)
python manage.py makemigrations        # generate migration files
python manage.py migrate               # apply migrations to the database
python manage.py createsuperuser       # create an admin user
python manage.py shell                 # open interactive Django shell
python manage.py collectstatic         # gather static files for production
python manage.py test                  # run test suite
```

---

## requirements.txt

```
django>=5.0
djangorestframework>=3.15
pillow>=10.0          # image handling
python-decouple>=3.8  # .env management
gunicorn>=21.0        # production WSGI server
```

---

*Happy coding! Work through the modules in order for the best learning experience.*
