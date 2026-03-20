from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from .forms import TaskForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from taskcore.priority import auto_priority
from taskcore.deadline import days_remaining
from taskcore.validator import validate_title
from taskcore.validator import validate_title, validate_due_date


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('task_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def task_list(request):
    tasks = Task.objects.filter(created_by=request.user)

    query = request.GET.get('q')
    if query:
        tasks = tasks.filter(title__icontains=query)

    task_data = []
    completed_count = 0

    for task in tasks:
        remaining = days_remaining(task.due_date)

        if task.completed:
            completed_count += 1

        task_data.append({
            "task": task,
            "remaining": remaining,
            "overdue": remaining < 0
        })

    total_tasks = len(task_data)
    pending_tasks = total_tasks - completed_count

    return render(request, 'tasks/task_list.html', {
        'tasks': task_data,
        'total_tasks': total_tasks,
        'completed_tasks': completed_count,
        'pending_tasks': pending_tasks,
        'query': query
    })


@login_required
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)

        if form.is_valid():
            task = form.save(commit=False)

            # Validate title
            title_error = validate_title(task.title)
            if title_error:
                form.add_error('title', title_error)

            # Validate due date
            date_error = validate_due_date(task.due_date)
            if date_error:
                form.add_error('due_date', date_error)

            if title_error or date_error:
                return render(request, 'tasks/task_form.html', {'form': form})

            task.created_by = request.user
            task.priority = auto_priority(task.due_date)
            task.save()

            return redirect('task_list')

    else:
        form = TaskForm()

    return render(request, 'tasks/task_form.html', {'form': form})


@login_required
def edit_task(request, pk):
    task = get_object_or_404(Task, pk=pk, created_by=request.user)
    form = TaskForm(request.POST or None, instance=task)

    if form.is_valid():
        task = form.save(commit=False)

        title_error = validate_title(task.title)
        if title_error:
            form.add_error('title', title_error)

        date_error = validate_due_date(task.due_date)
        if date_error:
            form.add_error('due_date', date_error)

        if title_error or date_error:
            return render(request, 'tasks/task_form.html', {'form': form})

        task.priority = auto_priority(task.due_date)
        task.save()

        return redirect('task_list')

    return render(request, 'tasks/task_form.html', {'form': form})


@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, created_by=request.user)
    task.delete()
    return redirect('task_list')

@login_required
def toggle_complete(request, pk):
    task = get_object_or_404(Task, pk=pk, created_by=request.user)
    task.completed = not task.completed
    task.save()
    return redirect('task_list')