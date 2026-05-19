# hello/views.py — Module 01 example
from django.http import HttpResponse
import datetime


def index(request):
    return HttpResponse("<h1>Hello, Django World!</h1>")


def current_time(request):
    now = datetime.datetime.now()
    html = f"<p>Current server time: <strong>{now.strftime('%Y-%m-%d %H:%M:%S')}</strong></p>"
    return HttpResponse(html)
