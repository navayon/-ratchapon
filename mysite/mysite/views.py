from django.shortcuts import render, redirect
from .models import Task


def task_list(request):
        tasks = Task.objects.all()
        # SELECT * FROM mysite_task ORDER BY completed, due_date, created_at
        # task = Task.objects.raw('SELECT * FROM mysite_task WHERE completed = %s AND due_date < %s', [False, timezone.now().date()])
        return render(request, 'mysite/task_list.html', {'tasks': tasks})

def task_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        due_date = request.POST.get('due_date')
        # ORM
        Task.objects.create(title=title, due_date=due_date)
        # Raw SQL
        # from django.db import connection
        # with connection.cursor() as cursor:
        #     cursor.execute('INSERT INTO myToDo_task (title, due_date) VALUES
        return redirect('task_list')
    return render(request, 'mysite/task_form.html')