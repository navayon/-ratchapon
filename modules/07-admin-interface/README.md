# Module 07 — The Django Admin Interface

## Learning Objectives
- Register models with the Django admin
- Customise list display, filters, and search
- Add inline editing for related models
- Restrict admin access with permissions

---

## 7.1 Accessing the Admin

```bash
# 1. Create a superuser
python manage.py createsuperuser

# 2. Start the server
python manage.py runserver

# 3. Open http://127.0.0.1:8000/admin/
```

---

## 7.2 Registering Models

```python
# blog/admin.py
from django.contrib import admin
from .models import Category, Tag, Post, Comment

# Minimal registration
admin.site.register(Category)
admin.site.register(Tag)
```

---

## 7.3 Customising ModelAdmin

```python
# blog/admin.py
from django.contrib import admin
from django.utils import timezone
from .models import Category, Tag, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}   # auto-fill slug from name
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class CommentInline(admin.TabularInline):
    """Inline comments on the Post admin page."""
    model = Comment
    extra = 0           # no blank extra rows
    fields = ['author', 'body', 'is_approved']
    readonly_fields = ['author', 'created_at']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'published_at', 'comment_count']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'body', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']       # search widget instead of dropdown (for large tables)
    date_hierarchy = 'published_at'
    ordering = ['-published_at']
    filter_horizontal = ['tags']     # nice widget for ManyToMany
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CommentInline]

    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'author', 'body'),
        }),
        ('Categorisation', {
            'fields': ('category', 'tags'),
        }),
        ('Publishing', {
            'fields': ('status', 'published_at'),
            'classes': ('collapse',),   # collapsible section
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    # Custom list column
    @admin.display(description='Comments')
    def comment_count(self, obj):
        return obj.comments.count()

    # Custom admin action
    @admin.action(description='Publish selected posts')
    def publish_posts(self, request, queryset):
        count = queryset.filter(status='draft').update(
            status='published',
            published_at=timezone.now(),
        )
        self.message_user(request, f'{count} post(s) published.')

    actions = [publish_posts]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    list_editable = ['is_approved']   # edit directly in the list view
    search_fields = ['body', 'author__username', 'post__title']

    @admin.action(description='Approve selected comments')
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)

    actions = [approve_comments]
```

---

## 7.4 Customising the Admin Site

```python
# myproject/urls.py or in an AppConfig.ready()
from django.contrib import admin

admin.site.site_header = 'Django 101 Administration'
admin.site.site_title = 'Django 101 Admin'
admin.site.index_title = 'Site Administration'
```

---

## 7.5 Admin Permissions

```python
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete posts."""
        return request.user.is_superuser

    def get_queryset(self, request):
        """Non-superusers only see their own posts."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)
```

---

## Exercises

1. Register `Post`, `Category`, and `Tag` models with the admin.
2. Add `list_display`, `list_filter`, and `search_fields` to `PostAdmin`.
3. Use `prepopulated_fields` to auto-fill the `slug` field from the `title`.
4. Create a custom admin action to mark selected posts as drafts.
5. **Bonus:** Add a `CommentInline` to the `PostAdmin` so you can manage comments inline.

---

**Next:** [Module 08 — Static & Media Files →](../08-static-media/README.md)
