# blog/views.py — Module 04 example
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required

from .models import Post, Category


def post_list(request):
    posts = Post.objects.filter(status='published').select_related('author', 'category')
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    comments = post.comments.filter(is_approved=True)
    return render(request, 'blog/post_detail.html', {'post': post, 'comments': comments})


def post_by_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    posts = Post.objects.filter(category=category, status='published')
    return render(request, 'blog/post_list.html', {'posts': posts, 'category': category})


def post_search(request):
    query = request.GET.get('q', '')
    posts = Post.objects.filter(title__icontains=query, status='published') if query else []
    return render(request, 'blog/post_list.html', {'posts': posts, 'query': query})


@login_required
def post_create(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '').strip()
        if title and body:
            post = Post.objects.create(title=title, body=body, author=request.user)
            return redirect(post.get_absolute_url())
    return render(request, 'blog/post_form.html', {'action': 'Create'})


def post_api(request):
    posts = list(
        Post.objects.filter(status='published').values('id', 'title', 'slug', 'author__username')
    )
    return JsonResponse({'posts': posts})
