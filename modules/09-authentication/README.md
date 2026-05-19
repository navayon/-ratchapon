# Module 09 — Authentication & User Management

## Learning Objectives
- Use Django's built-in authentication system
- Implement login, logout, and sign-up flows
- Protect views with `@login_required` and `LoginRequiredMixin`
- Work with the `User` model and extend it with a `Profile`
- Understand permissions and groups

---

## 9.1 Django's Built-in Auth

Django ships with a complete auth system in `django.contrib.auth`:

| Feature | What's included |
|---------|----------------|
| User model | username, password (hashed), email, is_staff, is_active |
| Views | login, logout, password change, password reset |
| Decorators | `@login_required`, `@permission_required` |
| Middleware | `AuthenticationMiddleware` (attaches `request.user`) |
| Template context | `{{ user }}`, `{{ user.is_authenticated }}` |

---

## 9.2 Wiring Auth URLs

```python
# myproject/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls', namespace='blog')),
    # Provides: /accounts/login/, /accounts/logout/,
    #            /accounts/password_change/, /accounts/password_reset/
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),  # your custom signup, profile, etc.
]
```

Settings:
```python
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'      # redirect after successful login
LOGOUT_REDIRECT_URL = '/accounts/login/'
```

---

## 9.3 Login & Logout Templates

Django's built-in views use templates at these paths:

```
templates/
└── registration/
    ├── login.html
    ├── logout.html
    ├── password_change_form.html
    ├── password_change_done.html
    ├── password_reset_form.html
    ├── password_reset_done.html
    ├── password_reset_confirm.html
    └── password_reset_complete.html
```

### `templates/registration/login.html`
```html
{% extends 'base.html' %}
{% block title %}Login{% endblock %}

{% block content %}
<div class="auth-box">
  <h1>Sign In</h1>
  <form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <input type="hidden" name="next" value="{{ next }}">
    <button type="submit" class="btn btn-primary">Login</button>
  </form>
  <p>No account? <a href="{% url 'accounts:signup' %}">Sign up here</a></p>
</div>
{% endblock %}
```

---

## 9.4 Custom Sign-up View

Django doesn't include a registration view — you build it:

```python
# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=150, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user
```

```python
# accounts/views.py
from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import SignUpForm


def signup(request):
    if request.user.is_authenticated:
        return redirect('/')   # already logged in

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)   # log the user in immediately after signup
            return redirect('/')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})
```

```python
# accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
]
```

---

## 9.5 Protecting Views

### Decorator (function-based views)
```python
from django.contrib.auth.decorators import login_required, permission_required

@login_required                           # redirect to LOGIN_URL if not authenticated
def dashboard(request):
    return render(request, 'dashboard.html')

@permission_required('blog.add_post')    # requires specific permission
def post_create(request):
    ...
```

### Mixin (class-based views)
```python
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView

class DashboardView(LoginRequiredMixin, ListView):
    model = Post
    login_url = '/accounts/login/'

class PostCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'blog.add_post'
    ...
```

### Manual check inside a view
```python
from django.core.exceptions import PermissionDenied

def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user and not request.user.is_staff:
        raise PermissionDenied
    post.delete()
    return redirect('blog:post-list')
```

---

## 9.6 Working with request.user

```python
# In any view, request.user is the currently logged-in user (or AnonymousUser)
request.user.is_authenticated    # True / False
request.user.username
request.user.email
request.user.get_full_name()
request.user.is_staff
request.user.is_superuser

# In templates
{% if user.is_authenticated %}
  <p>Hello, {{ user.get_full_name|default:user.username }}</p>
  <a href="{% url 'logout' %}">Logout</a>
{% else %}
  <a href="{% url 'login' %}">Login</a>
{% endif %}
```

---

## 9.7 Permissions & Groups

```python
# Check permissions in views
if request.user.has_perm('blog.change_post'):
    ...

# Assign permissions to a user
from django.contrib.auth.models import Permission
perm = Permission.objects.get(codename='add_post')
user.user_permissions.add(perm)

# Groups — assign permissions in bulk
from django.contrib.auth.models import Group
editors = Group.objects.get(name='Editors')
user.groups.add(editors)
```

---

## 9.8 Password Hashing

Django never stores raw passwords. It uses PBKDF2 by default.

```python
# Manually hash and check passwords
from django.contrib.auth.hashers import make_password, check_password

hashed = make_password('mysecretpassword')
check_password('mysecretpassword', hashed)  # True
```

---

## Exercises

1. Wire up `django.contrib.auth.urls` and create the `registration/login.html` template.
2. Build a sign-up view with `UserCreationForm`. Redirect to home after sign-up.
3. Add `@login_required` to a "create post" view and verify the redirect.
4. Create a profile edit page where the logged-in user can update their first/last name.
5. **Bonus:** Add a `PermissionDenied` check so a user can only edit their own posts.

---

**Next:** [Module 10 — Class-Based Views →](../10-class-based-views/README.md)
