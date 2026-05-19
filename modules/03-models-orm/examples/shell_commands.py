# shell_commands.py — Module 03: QuerySet API cheatsheet
# Run: python manage.py shell, then paste these commands

# ── Setup ────────────────────────────────────────────────────────────────────
from blog.models import Post, Category, Tag, Comment
from django.contrib.auth.models import User

# ── CREATE ───────────────────────────────────────────────────────────────────
user = User.objects.get(username='admin')

cat = Category.objects.create(name='Technology', slug='technology')

post = Post.objects.create(
    title='Hello Django',
    slug='hello-django',
    author=user,
    category=cat,
    body='Django is awesome!',
    status='published',
)

# ── READ ─────────────────────────────────────────────────────────────────────
Post.objects.all()
Post.objects.filter(status='published')
Post.objects.filter(title__icontains='django')
Post.objects.get(slug='hello-django')
Post.objects.order_by('-created_at')[:5]

# ── UPDATE ───────────────────────────────────────────────────────────────────
post.title = 'Hello Django — Updated'
post.save()

Post.objects.filter(status='draft').update(status='published')

# ── DELETE ───────────────────────────────────────────────────────────────────
# Post.objects.get(id=99).delete()        # single
# Post.objects.filter(status='draft').delete()   # bulk

# ── MANY-TO-MANY ─────────────────────────────────────────────────────────────
t1, _ = Tag.objects.get_or_create(name='Python', defaults={'slug': 'python'})
t2, _ = Tag.objects.get_or_create(name='Django', defaults={'slug': 'django'})

post.tags.add(t1, t2)
print(post.tags.all())
print(t1.posts.all())   # reverse lookup
