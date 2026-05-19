# blog/urls.py — Module 04 example
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post-list'),
    path('search/', views.post_search, name='post-search'),
    path('api/', views.post_api, name='post-api'),
    path('create/', views.post_create, name='post-create'),
    path('category/<slug:category_slug>/', views.post_by_category, name='post-by-category'),
    path('<slug:slug>/', views.post_detail, name='post-detail'),
]
