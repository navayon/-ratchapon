# Module 05 — Templates & the Django Template Language (DTL)

## Learning Objectives
- Understand how Django renders templates
- Use template variables, tags, and filters
- Build reusable layouts with template inheritance
- Include partial templates
- Use `{% static %}` and `{% url %}` tags

---

## 5.1 Template Configuration

In `settings.py`, tell Django where to find templates:

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],   # global templates directory
        'APP_DIRS': True,                   # also look in <app>/templates/
        ...
    },
]
```

### Recommended directory structure
```
templates/
├── base.html              ← site-wide base layout
├── partials/
│   ├── _navbar.html
│   └── _footer.html
blog/
└── templates/
    └── blog/              ← namespaced under app name
        ├── post_list.html
        ├── post_detail.html
        └── post_form.html
```

---

## 5.2 Rendering a Template from a View

```python
# views.py
def post_list(request):
    posts = Post.objects.filter(status='published')
    # The dict is the "context" — available as variables in the template
    return render(request, 'blog/post_list.html', {'posts': posts})
```

---

## 5.3 Template Syntax

### Variables — `{{ }}`
```html
<h1>{{ post.title }}</h1>
<p>Author: {{ post.author.get_full_name }}</p>
<p>{{ user.username|upper }}</p>
```

### Tags — `{% %}`
Tags control logic — they do NOT output text themselves.

```html
<!-- if / elif / else -->
{% if user.is_authenticated %}
  <p>Welcome, {{ user.username }}!</p>
{% elif user.is_staff %}
  <p>Welcome, staff member!</p>
{% else %}
  <p><a href="{% url 'login' %}">Please log in</a></p>
{% endif %}

<!-- for loop -->
{% for post in posts %}
  <article>
    <h2>{{ post.title }}</h2>
    <p>{{ post.summary }}</p>
  </article>
{% empty %}
  <p>No posts found.</p>
{% endfor %}

<!-- with — alias a complex expression -->
{% with author=post.author.get_full_name %}
  <p>Written by {{ author }}</p>
{% endwith %}

<!-- url tag -->
<a href="{% url 'blog:post-detail' slug=post.slug %}">Read more</a>

<!-- static tag -->
{% load static %}
<img src="{% static 'images/logo.png' %}" alt="Logo">
<link rel="stylesheet" href="{% static 'css/style.css' %}">
```

### Filters — `{{ value|filter }}`
```html
{{ post.title|upper }}                     <!-- UPPERCASE -->
{{ post.title|lower }}                     <!-- lowercase -->
{{ post.title|title }}                     <!-- Title Case -->
{{ post.title|truncatewords:10 }}          <!-- first 10 words -->
{{ post.body|truncatechars:200 }}          <!-- first 200 chars -->
{{ post.body|linebreaks }}                 <!-- \n → <p> tags -->
{{ post.body|linebreaksbr }}               <!-- \n → <br> -->
{{ post.published_at|date:"F j, Y" }}      <!-- "January 1, 2025" -->
{{ post.published_at|timesince }}          <!-- "3 days ago" -->
{{ price|floatformat:2 }}                  <!-- "12.50" -->
{{ count|pluralize }}                      <!-- "" or "s" -->
{{ html_content|safe }}                    <!-- render raw HTML (use carefully!) -->
{{ value|default:"No value" }}             <!-- fallback if falsy -->
{{ items|length }}                         <!-- list length -->
{{ items|first }}  {{ items|last }}        <!-- first/last item -->
```

---

## 5.4 Template Inheritance

The core pattern for avoiding repeated HTML.

### `templates/base.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}Django 101{% endblock %}</title>
  {% load static %}
  <link rel="stylesheet" href="{% static 'css/style.css' %}">
  {% block extra_css %}{% endblock %}
</head>
<body>
  {% include 'partials/_navbar.html' %}

  <main class="container">
    {% if messages %}
      <div class="messages">
        {% for message in messages %}
          <div class="alert alert-{{ message.tags }}">{{ message }}</div>
        {% endfor %}
      </div>
    {% endif %}

    {% block content %}{% endblock %}
  </main>

  {% include 'partials/_footer.html' %}

  <script src="{% static 'js/main.js' %}"></script>
  {% block extra_js %}{% endblock %}
</body>
</html>
```

### `blog/templates/blog/post_list.html`
```html
{% extends 'base.html' %}

{% block title %}Blog — Django 101{% endblock %}

{% block content %}
<h1>Latest Posts</h1>

{% if category %}
  <p>Category: <strong>{{ category.name }}</strong></p>
{% endif %}

<div class="post-grid">
  {% for post in posts %}
    {% include 'blog/_post_card.html' with post=post %}
  {% empty %}
    <p>No posts yet. <a href="{% url 'blog:post-create' %}">Write the first one!</a></p>
  {% endfor %}
</div>
{% endblock %}
```

### `blog/templates/blog/_post_card.html` (partial)
```html
<article class="card">
  <h2><a href="{{ post.get_absolute_url }}">{{ post.title }}</a></h2>
  <p class="meta">
    By {{ post.author.get_full_name|default:post.author.username }}
    · {{ post.published_at|date:"M d, Y" }}
    · {{ post.comments.count }} comment{{ post.comments.count|pluralize }}
  </p>
  <p>{{ post.summary }}</p>
  <a href="{{ post.get_absolute_url }}" class="btn">Read More →</a>
</article>
```

### `blog/templates/blog/post_detail.html`
```html
{% extends 'base.html' %}

{% block title %}{{ post.title }} — Django 101{% endblock %}

{% block content %}
<article>
  <h1>{{ post.title }}</h1>
  <div class="meta">
    <span>{{ post.author.username }}</span> ·
    <time>{{ post.published_at|date:"F j, Y" }}</time>
  </div>

  <div class="body">
    {{ post.body|linebreaks }}
  </div>

  <section class="comments">
    <h3>Comments ({{ comments|length }})</h3>
    {% for comment in comments %}
      <div class="comment">
        <strong>{{ comment.author.username }}</strong>
        <p>{{ comment.body }}</p>
        <small>{{ comment.created_at|timesince }} ago</small>
      </div>
    {% empty %}
      <p>No comments yet.</p>
    {% endfor %}
  </section>
</article>
{% endblock %}
```

---

## 5.5 Custom Template Tags & Filters

```python
# blog/templatetags/blog_extras.py
from django import template
from blog.models import Post

register = template.Library()


@register.filter
def reading_time(text):
    """Estimate reading time in minutes."""
    words = len(text.split())
    minutes = max(1, round(words / 200))
    return f"{minutes} min read"


@register.simple_tag
def latest_posts(count=5):
    """Return the N most recent published posts."""
    return Post.objects.filter(status='published').order_by('-published_at')[:count]


@register.inclusion_tag('blog/_sidebar.html')
def sidebar():
    """Render sidebar with latest posts."""
    posts = Post.objects.filter(status='published')[:5]
    return {'posts': posts}
```

```html
<!-- Usage in template -->
{% load blog_extras %}
<p>{{ post.body|reading_time }}</p>

{% latest_posts as recent %}
{% for p in recent %}...{% endfor %}

{% sidebar %}
```

---

## Exercises

1. Create a `base.html` with a navbar, footer, and a `{% block content %}` area.
2. Create a template that extends base and displays a list of items using `{% for %}`.
3. Use at least 5 different filters in your templates.
4. Create a partial `_item_card.html` and `{% include %}` it inside your list loop.
5. **Bonus:** Write a custom filter that truncates text to a given number of sentences.

---

**Next:** [Module 06 — Forms →](../06-forms/README.md)
