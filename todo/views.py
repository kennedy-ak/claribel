from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from .models import TodoList, TodoItem
from .forms import TodoListForm
from notifications.services import NotificationService
from reports.models import DailyReport
from accounts.models import TaskAssignment


@login_required
def todo_create_view(request):
    if request.user.profile.role != 'mentee':
        messages.error(request, 'Only mentees can create todo lists.')
        return redirect('accounts:profile')

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
            # Send email notification
            NotificationService.send_notification(
                recipient=current_mentor.user,
                trigger_event='todo_submitted',
                subject=f'Todo List Submitted by {request.user.username}',
                message=f'{request.user.username} has created a todo list. '
                       f'Please review it on the mentor dashboard.',
                notification_type='email'
            )

            # Send SMS notification if mentor has SMS enabled
            if current_mentor.sms_notifications_enabled and current_mentor.phone_number:
                NotificationService.send_notification(
                    recipient=current_mentor.user,
                    trigger_event='todo_submitted',
                    subject='Todo List Submitted',
                    message=f'{request.user.username} submitted a todo list. Check your dashboard.',
                    notification_type='sms'
                )

        return redirect('todo:today')

    return render(request, 'todo/todo_form.html')


@login_required
def todo_today_view(request):
    if request.user.profile.role != 'mentee':
        return redirect('accounts:profile')

    today = timezone.now().date()
    todo_lists = TodoList.objects.filter(
        mentee=request.user,
        submission_date=today
    )

    # Calculate progress for all todos
    completed_count = 0
    total_count = 0
    for todo_list in todo_lists:
        total_count += todo_list.tasks.count()
        completed_count += todo_list.tasks.filter(status='completed').count()

    # Auto-mark overdue assigned tasks
    TaskAssignment.objects.filter(
        mentee=request.user,
        due_date__lt=today
    ).exclude(status__in=['completed', 'overdue']).update(status='overdue')

    # Assigned tasks due today (mentor-assigned)
    assigned_today = TaskAssignment.objects.filter(
        mentee=request.user,
        due_date=today
    ).select_related('mentor').order_by('priority')

    # Today's daily report (to control submit-button visibility)
    report_today = DailyReport.objects.filter(
        mentee=request.user,
        report_date=today
    ).first()

    context = {
        'todo_lists': todo_lists,
        'today': today,
        'completed_count': completed_count,
        'total_count': total_count,
        'assigned_today': assigned_today,
        'report_today': report_today,
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


@login_required
def mentor_toggle_review_view(request, item_id):
    """Toggle the mentor reviewed status of a todo item."""
    if request.user.profile.role != 'mentor':
        messages.error(request, 'Only mentors can review todo items.')
        return redirect('accounts:profile')

    todo_item = get_object_or_404(TodoItem, id=item_id)

    # Verify this todo item belongs to one of the mentor's mentees
    mentee_ids = [m.user.id for m in request.user.profile.get_mentees()]
    if todo_item.todo_list.mentee_id not in mentee_ids:
        messages.error(request, 'You can only review todo items of your mentees.')
        return redirect('todo:mentor_todos')

    # Toggle the mentor reviewed status
    todo_item.mentor_reviewed = not todo_item.mentor_reviewed
    todo_item.save()

    status = "reviewed" if todo_item.mentor_reviewed else "unreviewed"
    messages.success(request, f'Todo item marked as {status}.')
    return redirect('todo:mentor_todo_detail', todo_id=todo_item.todo_list.id)


@login_required
def mentor_item_comment_view(request, item_id):
    """Add or update mentor comment on a todo item."""
    if request.user.profile.role != 'mentor':
        messages.error(request, 'Only mentors can comment on todo items.')
        return redirect('accounts:profile')

    todo_item = get_object_or_404(TodoItem, id=item_id)

    # Verify this todo item belongs to one of the mentor's mentees
    mentee_ids = [m.user.id for m in request.user.profile.get_mentees()]
    if todo_item.todo_list.mentee_id not in mentee_ids:
        messages.error(request, 'You can only comment on todo items of your mentees.')
        return redirect('todo:mentor_todos')

    if request.method == 'POST':
        comment = request.POST.get('mentor_comment', '').strip()
        todo_item.mentor_comment = comment
        todo_item.save()

        messages.success(request, 'Comment added successfully.')
        return redirect('todo:mentor_todo_detail', todo_id=todo_item.todo_list.id)

    return redirect('todo:mentor_todo_detail', todo_id=todo_item.todo_list.id)
