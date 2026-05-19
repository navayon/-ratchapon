# hello/urls.py — Module 01 example
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('time/', views.current_time, name='current-time'),
]
