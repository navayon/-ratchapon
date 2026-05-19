# Module 11 — REST API with Django REST Framework (DRF)

## Learning Objectives
- Install and configure Django REST Framework
- Write serializers to convert models to/from JSON
- Use `APIView`, `GenericAPIView`, and `ViewSets`
- Implement CRUD endpoints with routers
- Add authentication and permissions to API endpoints

---

## 11.1 Installation & Setup

```bash
pip install djangorestframework
```

```python
# settings.py
INSTALLED_APPS = [
    ...
    'rest_framework',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}
```

---

## 11.2 Serializers

A serializer converts model instances ↔ JSON (or other formats).

```python
# blog/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Category, Tag, Comment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class PostListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'author', 'category', 'tags',
                  'status', 'published_at', 'comment_count']

    def get_comment_count(self, obj):
        return obj.comments.filter(is_approved=True).count()


class PostDetailSerializer(serializers.ModelSerializer):
    """Full serializer including body."""
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'author', 'category', 'tags',
                  'body', 'status', 'created_at', 'updated_at', 'published_at']
        read_only_fields = ['slug', 'created_at', 'updated_at', 'author']


class PostCreateSerializer(serializers.ModelSerializer):
    """Used for creating / updating posts (writable)."""
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True, required=False
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), source='tags', many=True, write_only=True, required=False
    )

    class Meta:
        model = Post
        fields = ['title', 'body', 'status', 'category_id', 'tag_ids']

    def validate_title(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Title must be at least 5 characters.")
        return value.strip()

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        post = Post.objects.create(**validated_data)
        post.tags.set(tags)
        return post

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'body', 'created_at', 'is_approved']
        read_only_fields = ['author', 'created_at', 'is_approved']
```

---

## 11.3 APIView (Low-Level)

```python
# blog/api_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Post
from .serializers import PostListSerializer, PostDetailSerializer, PostCreateSerializer


class PostListAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        posts = Post.objects.filter(status='published').order_by('-published_at')
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, slug):
        from django.shortcuts import get_object_or_404
        return get_object_or_404(Post, slug=slug, status='published')

    def get(self, request, slug):
        post = self.get_object(slug)
        serializer = PostDetailSerializer(post)
        return Response(serializer.data)

    def put(self, request, slug):
        post = self.get_object(slug)
        if post.author != request.user:
            return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = PostCreateSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        post = self.get_object(slug)
        if post.author != request.user:
            return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

---

## 11.4 ViewSets & Routers (Recommended)

ViewSets remove boilerplate by combining related views. Routers auto-generate URLs.

```python
# blog/api_views.py
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Post, Comment
from .serializers import PostListSerializer, PostDetailSerializer, CommentSerializer


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Allow read to all, write only to the post's author."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(status='published').order_by('-published_at')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        return PostDetailSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['get'], url_path='comments')
    def comments(self, request, pk=None):
        """Custom endpoint: GET /api/posts/<pk>/comments/"""
        post = self.get_object()
        comments = post.comments.filter(is_approved=True)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
```

### Wiring up the Router

```python
# blog/api_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'posts', api_views.PostViewSet, basename='post')

urlpatterns = [
    path('', include(router.urls)),
]
```

```python
# myproject/urls.py
urlpatterns = [
    ...
    path('api/', include('blog.api_urls')),
    path('api-auth/', include('rest_framework.urls')),   # browsable API login
]
```

### Generated URLs from `DefaultRouter`
| URL | Method | Action |
|-----|--------|--------|
| `/api/posts/` | GET | list |
| `/api/posts/` | POST | create |
| `/api/posts/{pk}/` | GET | retrieve |
| `/api/posts/{pk}/` | PUT/PATCH | update |
| `/api/posts/{pk}/` | DELETE | destroy |
| `/api/posts/{pk}/comments/` | GET | comments (custom) |

---

## 11.5 Testing the API

### Using VS Code REST Client (`.http` file)
```http
### List all posts
GET http://127.0.0.1:8000/api/posts/
Accept: application/json

### Create a post (requires login)
POST http://127.0.0.1:8000/api/posts/
Content-Type: application/json
Authorization: Basic admin:password

{
  "title": "My API Post",
  "body": "Written via REST API",
  "status": "published"
}

### Get one post
GET http://127.0.0.1:8000/api/posts/1/
```

---

## Exercises

1. Install DRF and configure `REST_FRAMEWORK` in settings with `IsAuthenticatedOrReadOnly`.
2. Create a `PostListSerializer` and test it returns correct JSON via the browsable API.
3. Build a `PostViewSet` with CRUD operations and wire it to a router.
4. Add a custom `@action` endpoint that returns the top 3 most-commented posts.
5. **Bonus:** Add token authentication (`rest_framework.authtoken`) and test with a token header.

---

**Next:** [Module 12 — Testing →](../12-testing/README.md)
