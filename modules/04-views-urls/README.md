# Module 04 — Views & URLs

## Learning Objectives
- Write function-based views (FBVs)
- Use URL patterns and path converters
- Handle HTTP methods (GET, POST)
- Return JSON responses
- Use `shortcuts` helpers (`render`, `get_object_or_404`, `redirect`)

---

## 4.1 The Request-Response Cycle

```
Browser  ──GET /blog/posts/──►  urls.py  ──►  view function
                                                    │
                                           QuerySet / logic
                                                    │
                                           render(request, template, context)
                                                    │
Browser  ◄──── HTML Response ──────────────────────┘
```

---

## 4.2 Function-Based Views

A view is simply a Python function that takes an `HttpRequest` and returns an `HttpResponse`.

```python
# blog/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required

from .models import Post, Category


def post_list(request):
    """List all published posts."""
    posts = Post.objects.filter(status='published').select_related('author', 'category')
    context = {'posts': posts, 'title': 'All Posts'}
    return render(request, 'blog/post_list.html', context)


def post_detail(request, slug):
    """Show a single post by slug."""
    post = get_object_or_404(Post, slug=slug, status='published')
    comments = post.comments.filter(is_approved=True)
    context = {'post': post, 'comments': comments}
    return render(request, 'blog/post_detail.html', context)


def post_by_category(request, category_slug):
    """Filter posts by category."""
    category = get_object_or_404(Category, slug=category_slug)
    posts = Post.objects.filter(category=category, status='published')
    return render(request, 'blog/post_list.html', {'posts': posts, 'category': category})


@login_required
def post_create(request):
    """Handle GET (show form) and POST (process form)."""
    if request.method == 'POST':
        # Form processing covered in Module 06
        title = request.POST.get('title')
        body = request.POST.get('body')
        Post.objects.create(title=title, body=body, author=request.user)
        return redirect('blog:post-list')

    return render(request, 'blog/post_form.html', {'action': 'Create'})


def post_api(request):
    """Return posts as JSON."""
    posts = list(
        Post.objects.filter(status='published').values('id', 'title', 'slug', 'author__username')
    )
    return JsonResponse({'posts': posts})
```

---

## 4.3 URL Configuration

### App-level URLs — `blog/urls.py`
```python
from django.urls import path
from . import views

app_name = 'blog'   # enables namespacing: reverse('blog:post-list')

urlpatterns = [
    path('', views.post_list, name='post-list'),
    path('<slug:slug>/', views.post_detail, name='post-detail'),
    path('category/<slug:category_slug>/', views.post_by_category, name='post-by-category'),
    path('create/', views.post_create, name='post-create'),
    path('api/posts/', views.post_api, name='post-api'),
]
```

### Root URL conf — `myproject/urls.py`
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls', namespace='blog')),
    path('accounts/', include('django.contrib.auth.urls')),
]
```

---

## 4.4 Path Converters

| Converter | Matches | Example |
|-----------|---------|---------|
| `str` | Any non-empty string without `/` | `<str:username>` |
| `int` | Positive integers | `<int:pk>` |
| `slug` | Slug strings (`a-z`, `0-9`, `-`, `_`) | `<slug:slug>` |
| `uuid` | UUID strings | `<uuid:id>` |
| `path` | Any string, including `/` | `<path:file_path>` |

```python
# Examples
path('<int:pk>/', views.post_detail_by_id, name='post-detail-id'),
path('archive/<int:year>/<int:month>/', views.archive, name='archive'),
path('files/<path:file_path>/', views.serve_file, name='serve-file'),
```

---

## 4.5 URL Reversing

Use `reverse()` in Python or `{% url %}` in templates — **never hardcode URLs**.

```python
# In Python code
from django.urls import reverse

url = reverse('blog:post-detail', kwargs={'slug': 'my-first-post'})
# → '/blog/my-first-post/'

# redirect using the model's get_absolute_url()
return redirect(post.get_absolute_url())
```

```html
<!-- In templates -->
<a href="{% url 'blog:post-detail' slug=post.slug %}">{{ post.title }}</a>
<a href="{% url 'blog:post-list' %}">All Posts</a>
```

---

## 4.6 Useful Shortcuts

```python
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect

# render — shortcut for Template + HttpResponse
return render(request, 'template.html', context_dict)

# get_object_or_404 — returns 404 if not found (instead of raising exception)
obj = get_object_or_404(MyModel, pk=pk)

# get_list_or_404 — returns 404 if the list is empty
items = get_list_or_404(MyModel, is_active=True)

# redirect
return redirect('home')                          # by URL name
return redirect('/some/absolute/path/')          # by path
return redirect(post)                            # calls get_absolute_url()
```

---

## 4.7 HTTP Status Codes

```python
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden

HttpResponse('OK')                               # 200
HttpResponse('Created', status=201)
HttpResponseNotFound('Page not found')           # 404
HttpResponseForbidden('Access denied')           # 403

# Preferred: use exceptions
from django.core.exceptions import PermissionDenied
from django.http import Http404

if not request.user.is_authenticated:
    raise PermissionDenied

if not Post.objects.filter(id=pk).exists():
    raise Http404("Post not found")
```

---

## Exercises

1. Create a `products` app with views for: list all products, show one product by `pk`.
2. Add a URL pattern `products/<int:pk>/` and verify it in the browser.
3. Create a view that accepts a query parameter `?q=search_term` and filters products by name.
4. Add a `JsonResponse` view at `/products/api/` that returns all products as JSON.
5. **Bonus:** Create a view that returns a 404 if a product is out of stock.

---

**Next:** [Module 05 — Templates →](../05-templates/README.md)
