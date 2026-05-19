# Module 10 — Class-Based Views (CBV)

## Learning Objectives
- Understand when to use CBVs vs function-based views
- Use generic CBVs: `ListView`, `DetailView`, `CreateView`, `UpdateView`, `DeleteView`
- Apply mixins for authentication and permissions
- Override CBV methods to customise behaviour

---

## 10.1 Why Class-Based Views?

| | FBV | CBV |
|-|-----|-----|
| Simple view | Simpler | More boilerplate |
| Common CRUD patterns | Repetitive | Much less code |
| Reusability | Copy/paste | Inheritance & mixins |
| Customisation | Very flexible | Requires knowing which method to override |

---

## 10.2 Generic Display Views

### `ListView`
```python
# blog/views.py
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Post


class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'   # default: blog/post_list.html
    context_object_name = 'posts'           # default: object_list
    paginate_by = 10                        # adds pagination automatically

    def get_queryset(self):
        """Only show published posts, honour ?q= search."""
        qs = Post.objects.filter(status='published').select_related('author', 'category')
        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(title__icontains=query)
        return qs

    def get_context_data(self, **kwargs):
        """Add extra data to the template context."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'All Posts'
        context['query'] = self.request.GET.get('q', '')
        return context
```

### `DetailView`
```python
class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'              # which model field to look up
    slug_url_kwarg = 'slug'          # URL keyword argument name

    def get_queryset(self):
        return Post.objects.filter(status='published')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(is_approved=True)
        return context
```

---

## 10.3 Generic Editing Views

```python
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms import PostForm


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        """Called when the form is valid — set author before saving."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def get_queryset(self):
        """Users can only edit their own posts."""
        return Post.objects.filter(author=self.request.user)

    def get_success_url(self):
        return self.object.get_absolute_url()


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('blog:post-list')

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)
```

---

## 10.4 URL Patterns for CBVs

```python
# blog/urls.py
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post-list'),
    path('create/', views.PostCreateView.as_view(), name='post-create'),
    path('<slug:slug>/', views.PostDetailView.as_view(), name='post-detail'),
    path('<slug:slug>/edit/', views.PostUpdateView.as_view(), name='post-edit'),
    path('<slug:slug>/delete/', views.PostDeleteView.as_view(), name='post-delete'),
]
```

---

## 10.5 Pagination in Templates

`ListView` with `paginate_by` automatically passes a `page_obj` to the template:

```html
<!-- Pagination -->
{% if is_paginated %}
<nav class="pagination">
  {% if page_obj.has_previous %}
    <a href="?page={{ page_obj.previous_page_number }}">&laquo; Previous</a>
  {% endif %}

  <span>Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}</span>

  {% if page_obj.has_next %}
    <a href="?page={{ page_obj.next_page_number }}">Next &raquo;</a>
  {% endif %}
</nav>
{% endif %}
```

---

## 10.6 Mixins

Mixins are reusable pieces of behaviour you combine with views:

```python
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class AuthorRequiredMixin(UserPassesTestMixin):
    """Only allow the post's author to access this view."""

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class PostUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    ...
```

### Custom Mixin for context
```python
class PageTitleMixin:
    page_title = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        return context


class PostListView(PageTitleMixin, ListView):
    page_title = 'Blog Posts'
    ...
```

---

## 10.7 CBV Method Resolution Order (key methods to override)

| Method | When to override |
|--------|-----------------|
| `get_queryset()` | Filter which objects are fetched |
| `get_object()` | Custom lookup logic |
| `get_context_data()` | Add extra template context |
| `form_valid()` | Extra logic when form passes validation |
| `form_invalid()` | Extra logic when form fails validation |
| `get_success_url()` | Dynamic redirect after success |
| `dispatch()` | Pre-process every request |

---

## Exercises

1. Convert your `post_list` FBV into a `PostListView` with `paginate_by=5`.
2. Add `get_queryset()` to filter by `?q=` query parameter.
3. Create `PostCreateView` and `PostUpdateView` ensuring only the author can edit.
4. Add a `PostDeleteView` with a confirmation template.
5. **Bonus:** Create a `UserPostListView` that shows only posts by a given username (from URL).

---

**Next:** [Module 11 — REST API with DRF →](../11-rest-api/README.md)
