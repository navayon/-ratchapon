# Module 03 — Models & the ORM

## Learning Objectives
- Define database models using Python classes
- Understand field types and field options
- Create and apply database migrations
- Perform CRUD operations using Django's QuerySet API
- Use model relationships (ForeignKey, ManyToMany, OneToOne)

---

## 3.1 What Is the ORM?

Django's **Object-Relational Mapper (ORM)** lets you interact with the database using Python instead of raw SQL. Each model class maps to a database table, and each instance maps to a row.

```
Python Class  ──►  Database Table
Attribute     ──►  Column
Instance      ──►  Row
```

---

## 3.2 Defining Models

```python
# blog/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Post(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
    ]

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='published_at')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blog_posts',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
    )
    tags = models.ManyToManyField('Tag', blank=True, related_name='posts')
    body = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
    )
    created_at = models.DateTimeField(auto_now_add=True)  # set once on creation
    updated_at = models.DateTimeField(auto_now=True)       # updated every save
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['status', '-published_at']),
        ]

    def __str__(self):
        return self.title

    def publish(self):
        self.status = self.STATUS_PUBLISHED
        self.published_at = timezone.now()
        self.save()


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Comment by {self.author} on '{self.post}'"
```

---

## 3.3 Common Field Types

| Field | Use Case | Example |
|-------|----------|---------|
| `CharField` | Short text (requires `max_length`) | name, title |
| `TextField` | Long/unlimited text | body, description |
| `IntegerField` | Whole numbers | count, age |
| `FloatField` / `DecimalField` | Decimal numbers | price, rating |
| `BooleanField` | True/False | is_active, is_staff |
| `DateField` | Date only | birth_date |
| `DateTimeField` | Date + time | created_at |
| `EmailField` | Validated email | user_email |
| `URLField` | Validated URL | website |
| `SlugField` | URL-friendly string | post-slug |
| `ImageField` | Image upload path (requires Pillow) | avatar |
| `FileField` | File upload path | attachment |
| `ForeignKey` | Many-to-one relationship | author → User |
| `ManyToManyField` | Many-to-many relationship | tags |
| `OneToOneField` | One-to-one relationship | profile → User |

### Common Field Options
```python
models.CharField(
    max_length=200,
    null=True,        # allow NULL in DB
    blank=True,       # allow empty in forms
    unique=True,      # enforce uniqueness
    default='',       # default value
    db_index=True,    # add a DB index
    verbose_name='My Field',
    help_text='Helpful text for forms/admin',
)
```

---

## 3.4 Migrations

Migrations are version-controlled snapshots of your models.

```bash
# After changing models.py:
python manage.py makemigrations          # generate migration file(s)
python manage.py makemigrations blog     # for a specific app
python manage.py migrate                 # apply to the database

# Inspect generated SQL without applying
python manage.py sqlmigrate blog 0001

# See all migration statuses
python manage.py showmigrations
```

**Migration workflow:**
```
Edit models.py  ──►  makemigrations  ──►  review migration  ──►  migrate
```

---

## 3.5 QuerySet API — CRUD Operations

### Open the Django Shell
```bash
python manage.py shell
```

### Create
```python
from blog.models import Post, Category
from django.contrib.auth.models import User

user = User.objects.get(username='admin')
cat = Category.objects.create(name='Technology', slug='technology')

# Method 1 — create() in one step
post = Post.objects.create(
    title='My First Post',
    slug='my-first-post',
    author=user,
    category=cat,
    body='This is the post body.',
)

# Method 2 — instantiate and save
post = Post(title='Second Post', slug='second-post', author=user, body='...')
post.save()
```

### Read
```python
# Get all posts
posts = Post.objects.all()

# Filter
published = Post.objects.filter(status='published')
by_author = Post.objects.filter(author=user)

# Chaining filters
recent = Post.objects.filter(status='published').order_by('-published_at')[:5]

# Get a single object (raises DoesNotExist if not found)
post = Post.objects.get(id=1)
post = Post.objects.get(slug='my-first-post')

# get_or_create — returns (object, created_bool)
tag, created = Tag.objects.get_or_create(name='Python', defaults={'slug': 'python'})

# Field lookups
Post.objects.filter(title__icontains='django')    # case-insensitive contains
Post.objects.filter(created_at__year=2025)
Post.objects.filter(id__in=[1, 2, 3])
Post.objects.filter(author__username='admin')     # traverse FK with __

# Exclude
Post.objects.exclude(status='draft')

# Count
Post.objects.filter(status='published').count()

# Exists
Post.objects.filter(status='published').exists()   # returns True/False
```

### Update
```python
# Update a single instance
post = Post.objects.get(id=1)
post.title = 'Updated Title'
post.save()

# Bulk update (no save() needed, more efficient)
Post.objects.filter(status='draft').update(status='published')
```

### Delete
```python
# Delete a single instance
post = Post.objects.get(id=1)
post.delete()

# Bulk delete
Post.objects.filter(status='draft').delete()
```

### Many-to-Many
```python
from blog.models import Tag

# Add tags to a post
tag_python = Tag.objects.get(slug='python')
tag_django = Tag.objects.get(slug='django')

post.tags.add(tag_python, tag_django)
post.tags.remove(tag_python)
post.tags.set([tag_django])    # replace all tags
post.tags.all()                # get all tags for this post
tag_django.posts.all()         # reverse lookup
```

---

## 3.6 Model Methods & Properties

```python
class Post(models.Model):
    # ... fields ...

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blog:post-detail', kwargs={'slug': self.slug})

    @property
    def summary(self):
        """Return the first 150 characters of the body."""
        return self.body[:150]

    @property
    def comment_count(self):
        return self.comments.filter(is_approved=True).count()
```

---

## Exercises

1. Create a `bookstore` app with a `Book` model that has: `title`, `author` (CharField), `isbn` (unique), `price` (DecimalField), `published_date`, `is_available` (BooleanField).
2. Run `makemigrations` and `migrate`.
3. In the Django shell, create 5 books, then filter to find all books where `price < 25`.
4. Update all unavailable books to `is_available=True`.
5. **Bonus:** Add a `Publisher` model with a ForeignKey from `Book`.

---

**Next:** [Module 04 — Views & URLs →](../04-views-urls/README.md)
