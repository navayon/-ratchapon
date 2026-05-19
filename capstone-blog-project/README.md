# Capstone Project — Django Blog Platform

## Project Overview

Build a fully functional **Blog Platform** that incorporates everything learned in the course.  
This is an open-ended project — implement features progressively and use it as your portfolio piece.

---

## Features to Build

### Core (Required)
- [ ] User registration, login, and logout
- [ ] Create, edit, and delete blog posts (author-only)
- [ ] Post categories and tags
- [ ] Comment system (with moderation)
- [ ] Django admin for all models
- [ ] Paginated post list

### Intermediate
- [ ] User profile page with bio and avatar upload
- [ ] Search posts by title or content
- [ ] Filter posts by category
- [ ] Post detail shows related posts
- [ ] REST API (`/api/posts/`) using Django REST Framework

### Bonus / Advanced
- [ ] Rich text editor (e.g. `django-ckeditor` or `django-summernote`)
- [ ] Email notification when a comment is approved
- [ ] RSS feed (`django.contrib.syndication`)
- [ ] Social share buttons
- [ ] Deploy to Railway or Render

---

## Suggested Project Structure

```
capstone-blog-project/
├── manage.py
├── requirements.txt
├── .env
├── .gitignore
├── Dockerfile
├── render.yaml
│
├── config/                    ← project package (renamed from default)
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── apps/
│   ├── blog/                  ← posts, categories, tags, comments
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │   ├── admin.py
│   │   ├── serializers.py
│   │   ├── api_views.py
│   │   └── tests.py
│   └── accounts/              ← registration, profile
│       ├── models.py
│       ├── views.py
│       ├── urls.py
│       ├── forms.py
│       └── tests.py
│
├── templates/
│   ├── base.html
│   ├── registration/
│   │   └── login.html
│   ├── blog/
│   │   ├── post_list.html
│   │   ├── post_detail.html
│   │   ├── post_form.html
│   │   └── post_confirm_delete.html
│   └── accounts/
│       ├── signup.html
│       └── profile.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
│
└── media/                     ← user uploads (git-ignored)
```

---

## Getting Started

```bash
# 1. Set up environment
cd capstone-blog-project
python3 -m venv .venv
source .venv/bin/activate        # macOS
# .venv\Scripts\Activate.ps1    # Windows

pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your SECRET_KEY

# 3. Database
python manage.py migrate
python manage.py createsuperuser

# 4. Run
python manage.py runserver
```

---

## Data Models

```
User (Django built-in)
  └─ Profile (OneToOne)
       - bio
       - avatar

Category
  - name
  - slug

Tag
  - name
  - slug

Post
  - title
  - slug
  - author (FK → User)
  - category (FK → Category)
  - tags (M2M → Tag)
  - body
  - featured_image
  - status (draft|published)
  - created_at
  - updated_at
  - published_at

Comment
  - post (FK → Post)
  - author (FK → User)
  - body
  - is_approved
  - created_at
```

---

## API Endpoints

| Method | URL | Description | Auth |
|--------|-----|-------------|------|
| GET | `/api/posts/` | List all published posts | No |
| POST | `/api/posts/` | Create a post | Yes |
| GET | `/api/posts/{id}/` | Get a single post | No |
| PUT/PATCH | `/api/posts/{id}/` | Update a post | Owner |
| DELETE | `/api/posts/{id}/` | Delete a post | Owner |
| GET | `/api/posts/{id}/comments/` | List comments for a post | No |
| POST | `/api/posts/{id}/comments/` | Add a comment | Yes |

---

## Milestones

| Milestone | Modules Applied | Target |
|-----------|----------------|--------|
| 1 — Models & DB | 01–03 | Create all models and run migrations |
| 2 — Views & Templates | 04–05 | Post list and detail pages |
| 3 — Forms | 06 | Create, edit, delete posts |
| 4 — Admin & Media | 07–08 | Admin site + avatar upload |
| 5 — Auth | 09 | Sign up, login, profile |
| 6 — CBVs | 10 | Refactor views to CBVs |
| 7 — REST API | 11 | API endpoints + REST Client test |
| 8 — Tests | 12 | 80%+ test coverage |
| 9 — Deploy | 13 | Live on Railway or Render |

---

*Good luck! Refer back to the module READMEs whenever you need a refresher.*
