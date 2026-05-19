# blog/tests.py — Module 12 example
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Post, Category
from .forms import PostForm


# ── Model Tests ──────────────────────────────────────────────────────────────

class CategoryModelTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name='Tech', slug='tech')

    def test_str_representation(self):
        self.assertEqual(str(self.category), 'Tech')


class PostModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            author=self.user,
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

    def test_summary_returns_first_150_chars(self):
        self.post.body = 'A' * 300
        self.assertEqual(len(self.post.summary), 150)


# ── View Tests ───────────────────────────────────────────────────────────────

class PostViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='viewer', password='pass123')
        self.post = Post.objects.create(
            title='Visible Post', slug='visible-post', author=self.user,
            body='Content.', status='published',
        )

    def test_post_list_returns_200(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

    def test_post_create_requires_login(self):
        response = self.client.get('/blog/create/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])


# ── Form Tests ───────────────────────────────────────────────────────────────

class PostFormTest(TestCase):

    def test_valid_form(self):
        form = PostForm(data={'title': 'Valid Post Title', 'body': 'Some body.', 'status': 'draft'})
        self.assertTrue(form.is_valid())

    def test_title_too_short_fails_validation(self):
        form = PostForm(data={'title': 'Hi', 'body': 'Body.', 'status': 'draft'})
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)


# ── API Tests ────────────────────────────────────────────────────────────────

class PostAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='apiuser', password='pass123')
        self.post = Post.objects.create(
            title='API Post', slug='api-post', author=self.user,
            body='API body.', status='published',
        )

    def test_list_posts_returns_200(self):
        response = self.client.get('/api/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_post_requires_auth(self):
        response = self.client.post('/api/posts/', {'title': 'X', 'body': 'Y'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_post_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/posts/', {
            'title': 'Authenticated Post', 'body': 'Body here.', 'status': 'published',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
