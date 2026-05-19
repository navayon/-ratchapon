# Module 08 — Static Files & Media Uploads

## Learning Objectives
- Understand the difference between static files and media files
- Configure `STATIC_URL`, `STATICFILES_DIRS`, and `MEDIA_ROOT`
- Serve static and media files during development
- Handle image/file uploads with `ImageField` and `FileField`
- Run `collectstatic` for production

---

## 8.1 Static Files vs Media Files

| | Static Files | Media Files |
|-|-------------|-------------|
| **What** | CSS, JS, images bundled with the code | User-uploaded files |
| **Examples** | `style.css`, `logo.png`, `app.js` | Profile photos, attachments |
| **Where stored** | `static/` inside your app or project | `media/` directory (outside codebase) |
| **Settings** | `STATIC_URL`, `STATICFILES_DIRS` | `MEDIA_URL`, `MEDIA_ROOT` |
| **Version control** | Yes | No (never commit user uploads) |

---

## 8.2 Settings Configuration

```python
# settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Static files ─────────────────────────────────────────────
STATIC_URL = '/static/'

# Directories to search for static files (in addition to app/static/)
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Production: where collectstatic copies all files
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ── Media files ──────────────────────────────────────────────
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### Directory structure
```
myproject/
├── static/                ← project-wide static files
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── images/
│       └── logo.png
├── media/                 ← user uploads (git-ignored)
│   └── avatars/
│       └── user_1.jpg
└── myapp/
    └── static/
        └── myapp/         ← app-specific static files (namespaced)
            └── app.css
```

---

## 8.3 Serving Files in Development

Django's dev server does NOT serve media files by default. Add this to `urls.py`:

```python
# myproject/urls.py
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... your URL patterns ...
]

# Serve static and media files in development only
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## 8.4 Using Static Files in Templates

```html
{% load static %}

<!DOCTYPE html>
<html>
<head>
  <!-- CSS -->
  <link rel="stylesheet" href="{% static 'css/style.css' %}">
  <!-- Favicon -->
  <link rel="icon" href="{% static 'images/favicon.ico' %}">
</head>
<body>
  <!-- Image -->
  <img src="{% static 'images/logo.png' %}" alt="Logo" width="120">

  <!-- JavaScript -->
  <script src="{% static 'js/main.js' %}"></script>
</body>
</html>
```

---

## 8.5 File Upload Models

```python
# blog/models.py
from django.db import models
from django.contrib.auth.models import User


def avatar_upload_path(instance, filename):
    """Store avatar as media/avatars/<user_id>/<filename>."""
    return f'avatars/{instance.user.id}/{filename}'


def post_image_upload_path(instance, filename):
    return f'posts/{instance.slug}/{filename}'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    avatar = models.ImageField(
        upload_to=avatar_upload_path,
        null=True,
        blank=True,
    )
    website = models.URLField(blank=True)

    def __str__(self):
        return f'Profile of {self.user.username}'

    @property
    def avatar_url(self):
        """Return avatar URL or a default placeholder."""
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.png'


class PostImage(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=post_image_upload_path)
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Image for {self.post}'
```

---

## 8.6 Upload Forms & Views

```python
# forms.py
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar', 'website']


class PostImageForm(forms.ModelForm):
    class Meta:
        model = PostImage
        fields = ['image', 'caption']
```

```python
# views.py
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import ProfileForm


@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        # IMPORTANT: include request.FILES for file uploads
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'accounts/profile_edit.html', {'form': form})
```

```html
<!-- Template: MUST include enctype -->
<form method="post" enctype="multipart/form-data">
  {% csrf_token %}
  {{ form.as_p }}
  {% if profile.avatar %}
    <p>Current avatar:</p>
    <img src="{{ profile.avatar.url }}" width="80" alt="Current avatar">
  {% endif %}
  <button type="submit">Save Profile</button>
</form>
```

---

## 8.7 Auto-create Profile on User Signup (Signal)

```python
# blog/signals.py
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
```

```python
# blog/apps.py
class BlogConfig(AppConfig):
    name = 'blog'

    def ready(self):
        import blog.signals  # noqa: F401 — connect signals on startup
```

---

## 8.8 collectstatic for Production

```bash
# Copies all static files to STATIC_ROOT (e.g. staticfiles/)
python manage.py collectstatic --no-input

# Your web server (Nginx / CDN) then serves files from STATIC_ROOT
```

---

## Exercises

1. Add a `profile_picture` ImageField to a `UserProfile` model. Run migrations.
2. Create an upload form and view. Test that the file is saved under `media/`.
3. Display the uploaded image in a template using `{{ profile.avatar.url }}`.
4. Write a signal that automatically creates a `UserProfile` when a new `User` is saved.
5. **Bonus:** Validate in the form that the uploaded file is under 2 MB.

---

**Next:** [Module 09 — Authentication →](../09-authentication/README.md)
