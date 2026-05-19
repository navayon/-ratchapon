# Module 12 — Testing in Django

## Learning Objectives
- Write unit tests using Django's `TestCase`
- Test models, views, and forms
- Use the Django test `Client` to simulate HTTP requests
- Test API endpoints with DRF's `APIClient`
- Understand test coverage basics

---

## 12.1 Django Test Setup

Django's test runner discovers tests automatically in any `tests.py` file or `tests/` directory.

```bash
python manage.py test              # run all tests
python manage.py test blog         # run tests in the blog app
python manage.py test blog.tests.PostModelTestCase  # run specific class
python manage.py test -v 2         # verbose output
```

---

## 12.2 Model Tests

```python
# blog/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Post, Category, Tag


class CategoryModelTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name='Tech', slug='tech')

    def test_str_representation(self):
        self.assertEqual(str(self.category), 'Tech')

    def test_slug_is_unique(self):
        with self.assertRaises(Exception):
            Category.objects.create(name='Tech2', slug='tech')  # duplicate slug


class PostModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.category = Category.objects.create(name='Tech', slug='tech')
        self.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            author=self.user,
            category=self.category,
            body='This is a test post body.',
            status='draft',
        )

    def test_str_representation(self):
        self.assertEqual(str(self.post), 'Test Post')

    def test_default_status_is_draft(self):
        self.assertEqual(self.post.status, Post.STATUS_DRAFT)

    def test_publish_sets_status_and_date(self):
        self.post.publish()
        self.assertEqual(self.post.status, Post.STATUS_PUBLISHED)
        self.assertIsNotNone(self.post.published_at)
        self.assertAlmostEqual(
            self.post.published_at.timestamp(),
            timezone.now().timestamp(),
            delta=5,
        )

    def test_summary_returns_first_150_chars(self):
        long_body = 'A' * 300
        self.post.body = long_body
        self.assertEqual(len(self.post.summary), 150)

    def test_get_absolute_url(self):
        url = self.post.get_absolute_url()
        self.assertIn('test-post', url)
```

---

## 12.3 View Tests

```python
class PostViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='viewer', password='pass123')
        self.post = Post.objects.create(
            title='Visible Post',
            slug='visible-post',
            author=self.user,
            body='Some content.',
            status='published',
        )
        self.draft_post = Post.objects.create(
            title='Draft Post',
            slug='draft-post',
            author=self.user,
            body='Draft content.',
            status='draft',
        )

    def test_post_list_returns_200(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

    def test_post_list_shows_only_published(self):
        response = self.client.get('/blog/')
        self.assertContains(response, 'Visible Post')
        self.assertNotContains(response, 'Draft Post')

    def test_post_detail_returns_200_for_published(self):
        response = self.client.get(f'/blog/{self.post.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Visible Post')

    def test_post_detail_returns_404_for_draft(self):
        response = self.client.get(f'/blog/{self.draft_post.slug}/')
        self.assertEqual(response.status_code, 404)

    def test_post_create_requires_login(self):
        response = self.client.get('/blog/create/')
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])

    def test_post_create_by_logged_in_user(self):
        self.client.login(username='viewer', password='pass123')
        response = self.client.post('/blog/create/', {
            'title': 'Brand New Post',
            'body': 'New post content here.',
            'status': 'published',
        })
        self.assertEqual(response.status_code, 302)   # redirect on success
        self.assertTrue(Post.objects.filter(title='Brand New Post').exists())
```

---

## 12.4 Form Tests

```python
from .forms import PostForm, ContactForm


class PostFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='formuser', password='pass')

    def test_valid_form(self):
        form = PostForm(data={
            'title': 'Valid Post Title',
            'body': 'Some body content.',
            'status': 'draft',
        })
        self.assertTrue(form.is_valid())

    def test_title_too_short(self):
        form = PostForm(data={'title': 'Hi', 'body': 'Body.', 'status': 'draft'})
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_missing_body(self):
        form = PostForm(data={'title': 'Valid Title', 'status': 'draft'})
        self.assertFalse(form.is_valid())
        self.assertIn('body', form.errors)


class ContactFormTest(TestCase):

    def test_valid_contact_form(self):
        form = ContactForm(data={
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Hello',
            'message': 'This is a sufficiently long message for testing.',
        })
        self.assertTrue(form.is_valid())

    def test_spam_email_rejected(self):
        form = ContactForm(data={
            'name': 'Spammer',
            'email': 'user@spam.com',
            'subject': 'Buy',
            'message': 'Click this link for free money!!!',
        })
        self.assertFalse(form.is_valid())
```

---

## 12.5 API Tests with DRF APIClient

```python
from rest_framework.test import APITestCase, APIClient
from rest_framework import status


class PostAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='apiuser', password='pass123')
        self.post = Post.objects.create(
            title='API Test Post',
            slug='api-test-post',
            author=self.user,
            body='Body text.',
            status='published',
        )

    def test_list_posts_unauthenticated(self):
        response = self.client.get('/api/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_create_post_requires_auth(self):
        response = self.client.post('/api/posts/', {'title': 'New', 'body': 'Body'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_post_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/posts/', {
            'title': 'New Authenticated Post',
            'body': 'Body content here.',
            'status': 'published',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Authenticated Post')

    def test_delete_post_by_owner(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/posts/{self.post.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_post_by_non_owner_forbidden(self):
        other = User.objects.create_user(username='other', password='pass')
        self.client.force_authenticate(user=other)
        response = self.client.delete(f'/api/posts/{self.post.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
```

---

## 12.6 Test Coverage

```bash
pip install coverage

# Run tests with coverage
coverage run manage.py test

# Generate report in terminal
coverage report

# Generate HTML report (open htmlcov/index.html)
coverage html
```

---

## Exercises

1. Write model tests for your `Book` model (from Module 03) — test `__str__`, field defaults, and custom methods.
2. Write a view test that verifies an unauthenticated user is redirected from a `@login_required` view.
3. Write a form test that checks a `ContactForm` rejects an empty message.
4. Write an API test using `APIClient.force_authenticate` to create a new post.
5. **Bonus:** Run `coverage html` and aim for at least 80% coverage on your app.

---

**Next:** [Module 13 — Deployment →](../13-deployment/README.md)
