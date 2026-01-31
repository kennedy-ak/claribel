from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from .models import TodoList, TodoItem
from .forms import TodoListForm
from notifications.services import NotificationService


@login_required
def todo_create_view(request):
    if request.user.profile.role != 'mentee':
        messages.error(request, 'Only mentees can create todo lists.')
        return redirect('accounts:profile')

    # Check if todo list already exists for today
    today = timezone.now().date()
    existing_todo = TodoList.objects.filter(
        mentee=request.user,
        submission_date=today
    ).first()

    if existing_todo:
        messages.info(request, 'You have already created a todo list for today.')
        return redirect('todo:today')

    if request.method == 'POST':
        # Create the todo list
        todo_list = TodoList.objects.create(mentee=request.user)

        # Get the number of items from the form
        item_count = int(request.POST.get('item_count', 1))

        # Add items from the form data
        for i in range(item_count):
            title = request.POST.get(f'title_{i}', '').strip()
            priority = request.POST.get(f'priority_{i}', 'medium')

            if title:  # Only create if title is not empty
                TodoItem.objects.create(
                    todo_list=todo_list,
                    title=title,
                    priority=priority
                )

        messages.success(request, 'Todo list created successfully!')

        # Notify mentor if assigned
        current_mentor = request.user.profile.get_current_mentor()
        if current_mentor:
            NotificationService.send_notification(
                recipient=current_mentor.user,
                trigger_event='todo_submitted',
                subject=f'Todo List Submitted by {request.user.username}',
                message=f'{request.user.username} has created their daily todo list. '
                       f'Please review it on the mentor dashboard.',
                notification_type='email'
            )

        return redirect('todo:today')

    return render(request, 'todo/todo_form.html')


@login_required
def todo_today_view(request):
    if request.user.profile.role != 'mentee':
        return redirect('accounts:profile')

    today = timezone.now().date()
    todo_list = TodoList.objects.filter(
        mentee=request.user,
        submission_date=today
    ).first()

    # Calculate progress
    completed_count = 0
    total_count = 0
    if todo_list:
        total_count = todo_list.tasks.count()
        completed_count = todo_list.tasks.filter(status='completed').count()

    context = {
        'todo_list': todo_list,
        'today': today,
        'completed_count': completed_count,
        'total_count': total_count
    }
    return render(request, 'todo/todo_today.html', context)


@login_required
def mentor_todos_view(request):
    if request.user.profile.role != 'mentor':
        return redirect('accounts:profile')

    mentees = request.user.profile.get_mentees()
    mentee_ids = [m.user.id for m in mentees]

    # Get today's todos from all mentees
    today = timezone.now().date()
    todos = TodoList.objects.filter(
        mentee_id__in=mentee_ids,
        submission_date=today
    ).select_related('mentee')

    context = {
        'todos': todos,
        'today': today
    }
    return render(request, 'todo/mentor_todos.html', context)


@login_required
def mentor_todo_detail_view(request, todo_id):
    if request.user.profile.role != 'mentor':
        return redirect('accounts:profile')

    todo_list = get_object_or_404(TodoList, id=todo_id)

    # Verify this todo belongs to one of the mentor's mentees
    mentee_ids = [m.user.id for m in request.user.profile.get_mentees()]
    if todo_list.mentee_id not in mentee_ids:
        messages.error(request, 'You can only view todo lists of your mentees.')
        return redirect('todo:mentor_todos')

    if request.method == 'POST':
        form = TodoListForm(request.POST, instance=todo_list)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mentor notes saved successfully.')
            return redirect('todo:mentor_todo_detail', todo_id=todo_id)
    else:
        form = TodoListForm(instance=todo_list)

    context = {
        'todo_list': todo_list,
        'form': form
    }
    return render(request, 'todo/mentor_todo_detail.html', context)


@login_required
def toggle_todo_item_view(request, item_id):
    """Toggle the completion status of a todo item."""
    if request.user.profile.role != 'mentee':
        messages.error(request, 'Only mentees can update their todo items.')
        return redirect('accounts:profile')

    todo_item = get_object_or_404(TodoItem, id=item_id)

    # Verify this todo item belongs to the logged-in mentee
    if todo_item.todo_list.mentee != request.user:
        messages.error(request, 'You can only update your own todo items.')
        return redirect('todo:today')

    # Toggle the status
    if todo_item.status == 'pending':
        todo_item.status = 'completed'
    else:
        todo_item.status = 'pending'
    todo_item.save()

    messages.success(request, f'Todo item marked as {todo_item.status}.')
    return redirect('todo:today')
