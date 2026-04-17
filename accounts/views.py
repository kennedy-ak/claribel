from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from .models import UserProfile, Organization, MentorAssignment, TaskAssignment, Meeting
from .forms import RegistrationForm, OrganizationForm, MentorAssignmentForm, ProfileUpdateForm, TaskAssignmentForm, TaskUpdateForm, MeetingForm
from notifications.services import NotificationService

ALLOW_MENTOR_REGISTRATION = getattr(settings, 'ALLOW_MENTOR_REGISTRATION', True)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:mentor_dashboard' if request.user.profile.role == 'mentor' else 'accounts:mentee_dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if request.POST.get('remember_me'):
                request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days
            else:
                request.session.set_expiry(0)  # expires when browser closes
            return redirect(request.GET.get('next') or (
                'accounts:mentor_dashboard' if user.profile.role == 'mentor' else 'accounts:mentee_dashboard'
            ))
    else:
        form = AuthenticationForm(request)

    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    """User registration with organization code for mentees."""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Get form data
            role = 'mentee' if not ALLOW_MENTOR_REGISTRATION else form.cleaned_data['role']
            phone_number = form.cleaned_data.get('phone_number', '').strip()
            sms_notifications_enabled = form.cleaned_data.get('sms_notifications_enabled', False)
            join_code = form.cleaned_data.get('join_code', '').strip().upper()
            org_name = form.cleaned_data.get('org_name', '').strip()
            org_description = form.cleaned_data.get('org_description', '').strip()

            user = form.save()

            # Save phone number and SMS preferences to profile
            if phone_number:
                user.profile.phone_number = phone_number
            user.profile.sms_notifications_enabled = sms_notifications_enabled
            user.profile.save()

            # Handle organization assignment
            if role == 'mentee' and join_code:
                try:
                    organization = Organization.objects.get(join_code=join_code, is_active=True)
                    user.profile.organization = organization
                    user.profile.role = 'mentee'
                    user.profile.save()

                    # Assign to a mentor automatically if available
                    available_mentors = organization.get_mentors()
                    if available_mentors.exists():
                        # Simple round-robin: assign to mentor with fewest mentees
                        mentors_with_count = []
                        for mentor in available_mentors:
                            mentee_count = mentor.get_mentees().count()
                            mentors_with_count.append((mentor, mentee_count))

                        # Sort by mentee count and assign to the one with fewest
                        mentors_with_count.sort(key=lambda x: x[1])
                        assigned_mentor = mentors_with_count[0][0]

                        MentorAssignment.objects.create(
                            mentee=user.profile,
                            mentor=assigned_mentor,
                            notes="Auto-assigned on registration"
                        )

                    messages.success(request, f'Successfully joined {organization.name}!')
                except Organization.DoesNotExist:
                    messages.warning(request, 'Invalid organization code. You can join an organization later from your profile.')
                    user.profile.role = 'mentee'
                    user.profile.save()

            elif role == 'mentor':
                user.profile.role = 'mentor'
                user.profile.save()

                # Create organization if mentor provided org name
                if org_name:
                    organization = Organization.objects.create(
                        name=org_name,
                        description=org_description or '',
                        created_by=user,
                        is_active=True
                    )
                    user.profile.organization = organization
                    user.profile.save()
                    messages.success(request, f'Organization "{organization.name}" created successfully! Your join code is: {organization.join_code}')
                else:
                    messages.info(request, 'Mentor account created! Please ask an administrator to add you to an organization, or create your own organization.')

            return redirect('accounts:login')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {
        'form': form,
        'allow_mentor_registration': ALLOW_MENTOR_REGISTRATION,
    })


@login_required
def profile_view(request):
    """View user profile with organization info."""
    context = {
        'user_profile': request.user.profile
    }

    if request.user.profile.role == 'mentee':
        context['current_mentor'] = request.user.profile.get_current_mentor()

    return render(request, 'accounts/profile.html', context)


@login_required
def profile_update_view(request):
    """Update user profile information."""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'form': form
    }
    return render(request, 'accounts/profile_update.html', context)


@login_required
def mentor_dashboard_view(request):
    """Mentor dashboard showing assigned mentees, tasks, and meetings."""
    if request.user.profile.role != 'mentor':
        messages.error(request, 'Access restricted to mentors.')
        return redirect('accounts:profile')

    if not request.user.profile.organization:
        messages.warning(request, 'You are not assigned to any organization.')
        return redirect('accounts:profile')

    mentees = request.user.profile.get_mentees()
    organization = request.user.profile.organization

    # Get recent task assignments (last 5)
    recent_tasks = TaskAssignment.objects.filter(
        mentor=request.user
    ).select_related('mentee').order_by('-created_at')[:5]

    # Get upcoming meetings (next 5)
    upcoming_meetings = Meeting.objects.filter(
        mentor=request.user,
        status='scheduled',
        start_time__gt=timezone.now()
    ).select_related('mentee').order_by('start_time')[:5]

    context = {
        'mentees': mentees,
        'organization': organization,
        'recent_tasks': recent_tasks,
        'upcoming_meetings': upcoming_meetings
    }
    return render(request, 'accounts/mentor_dashboard.html', context)


@login_required
def mentee_dashboard_view(request):
    """Mentee dashboard showing current mentor, assigned tasks, and meetings."""
    if request.user.profile.role != 'mentee':
        return redirect('accounts:profile')

    current_mentor = request.user.profile.get_current_mentor()
    organization = request.user.profile.organization

    # Get assigned tasks (incomplete tasks first)
    my_tasks = TaskAssignment.objects.filter(
        mentee=request.user
    ).exclude(status='completed').select_related('mentor').order_by('due_date')[:5]

    # Get upcoming meetings
    my_meetings = Meeting.objects.filter(
        mentee=request.user,
        status='scheduled',
        start_time__gt=timezone.now()
    ).select_related('mentor').order_by('start_time')[:5]

    # Add is_overdue attribute to tasks
    for task in my_tasks:
        task.is_overdue = task.status != 'completed' and task.due_date < timezone.now().date()

    context = {
        'mentor': current_mentor,
        'organization': organization,
        'my_tasks': my_tasks,
        'my_meetings': my_meetings
    }
    return render(request, 'accounts/mentee_dashboard.html', context)


@login_required
def organization_create_view(request):
    """Create a new organization."""
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            organization = form.save(commit=False)
            organization.created_by = request.user
            organization.save()

            # Add creator as a mentor in the organization
            request.user.profile.organization = organization
            request.user.profile.role = 'mentor'
            request.user.profile.save()

            messages.success(request, f'Organization "{organization.name}" created successfully!')
            messages.info(request, f'Your organization join code is: {organization.join_code}')
            return redirect('accounts:organization_detail', org_id=organization.id)
    else:
        form = OrganizationForm()

    return render(request, 'accounts/organization_create.html', {'form': form})


@login_required
def organization_update_view(request, org_id):
    """Edit organization name and description. Restricted to org admin (creator)."""
    organization = get_object_or_404(Organization, id=org_id)

    if organization.created_by != request.user and not request.user.is_superuser:
        messages.error(request, 'Only the organization creator can edit it.')
        return redirect('accounts:organization_detail', org_id=org_id)

    if request.method == 'POST':
        form = OrganizationForm(request.POST, instance=organization)
        if form.is_valid():
            form.save()
            messages.success(request, 'Organization updated successfully.')
            return redirect('accounts:organization_detail', org_id=org_id)
    else:
        form = OrganizationForm(instance=organization)

    return render(request, 'accounts/organization_edit.html', {'form': form, 'organization': organization})


@login_required
def organization_detail_view(request, org_id):
    """View organization details and manage mentors/mentees."""
    organization = get_object_or_404(Organization, id=org_id)

    # Check if user belongs to this organization
    if request.user.profile.organization != organization:
        messages.error(request, 'You do not have permission to view this organization.')
        return redirect('accounts:profile')

    is_admin = organization.created_by == request.user or request.user.is_superuser
    is_mentee = request.user.profile.role == 'mentee'
    is_mentor = request.user.profile.role == 'mentor'

    mentors = organization.get_mentors()

    # Filter mentees based on user role
    if is_mentee:
        # Mentees only see themselves in the list
        mentees = organization.get_mentees().filter(user=request.user)
    else:
        # Mentors and admins see all mentees
        mentees = organization.get_mentees()

    context = {
        'organization': organization,
        'mentors': mentors,
        'mentees': mentees,
        'is_admin': is_admin,
        'is_mentee': is_mentee,
        'is_mentor': is_mentor
    }
    return render(request, 'accounts/organization_detail.html', context)


@login_required
def organization_join_view(request):
    """Join an organization using a code."""
    if request.user.profile.organization:
        messages.warning(request, 'You are already a member of an organization.')
        return redirect('accounts:profile')

    if request.method == 'POST':
        join_code = request.POST.get('join_code', '').strip().upper()
        try:
            organization = Organization.objects.get(join_code=join_code, is_active=True)

            if request.user.profile.role == 'mentor':
                request.user.profile.organization = organization
                request.user.profile.save()
                messages.success(request, f'Joined {organization.name} as a mentor!')
            else:
                # Assign to a mentor
                request.user.profile.organization = organization
                request.user.profile.save()

                available_mentors = organization.get_mentors()
                if available_mentors.exists():
                    mentors_with_count = []
                    for mentor in available_mentors:
                        mentee_count = mentor.get_mentees().count()
                        mentors_with_count.append((mentor, mentee_count))

                    mentors_with_count.sort(key=lambda x: x[1])
                    assigned_mentor = mentors_with_count[0][0]

                    MentorAssignment.objects.create(
                        mentee=request.user.profile,
                        mentor=assigned_mentor,
                        notes="Auto-assigned on joining organization"
                    )
                    messages.success(request, f'Joined {organization.name} and assigned to {assigned_mentor.user.username}!')
                else:
                    messages.warning(request, f'Joined {organization.name}, but no mentors available yet.')

            return redirect('accounts:profile')

        except Organization.DoesNotExist:
            messages.error(request, 'Invalid organization code. Please check and try again.')

    return render(request, 'accounts/organization_join.html')


@login_required
def mentor_assign_view(request, mentee_id):
    """Assign or reassign a mentee to a mentor."""
    mentee = get_object_or_404(UserProfile, id=mentee_id, role='mentee')

    # Check permissions: must be org admin or superuser
    org = mentee.organization
    if not org or (org.created_by != request.user and not request.user.is_superuser):
        messages.error(request, 'You do not have permission to assign mentors.')
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = MentorAssignmentForm(request.POST, organization=org)
        if form.is_valid():
            mentor = form.cleaned_data['mentor']
            notes = form.cleaned_data.get('notes', 'Reassigned by admin')

            MentorAssignment.objects.create(
                mentee=mentee,
                mentor=mentor,
                assigned_by=request.user,
                notes=notes
            )

            messages.success(request, f'{mentee.user.username} assigned to {mentor.user.username}')
            return redirect('accounts:organization_detail', org_id=org.id)
    else:
        current_mentor = mentee.get_current_mentor()
        form = MentorAssignmentForm(organization=org, initial={'mentor': current_mentor})

    context = {
        'form': form,
        'mentee': mentee,
        'organization': org
    }
    return render(request, 'accounts/mentor_assign.html', context)


# ==================== Task Assignment Views ====================

@login_required
def task_create_view(request):
    """Mentor creates a new task assignment for a mentee."""
    if request.user.profile.role != 'mentor':
        messages.error(request, 'Only mentors can create task assignments.')
        return redirect('accounts:profile')

    if not request.user.profile.organization:
        messages.warning(request, 'You must join an organization first.')
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = TaskAssignmentForm(request.POST, mentor=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.mentor = request.user
            task.save()

            # Send notification to mentee
            NotificationService.send_notification(
                recipient=task.mentee,
                trigger_event='task_assigned',
                subject=f'New Task Assigned: {task.title}',
                message=f'''Hi {task.mentee.first_name or task.mentee.username},

Your mentor has assigned you a new task: {task.title}

Due Date: {task.due_date}
Priority: {task.get_priority_display()}

Description: {task.description}

Please log in to view the full task details and update your progress.

Best regards,
MentorFlow Team''',
                notification_type='email'
            )

            messages.success(request, f'Task "{task.title}" assigned to {task.mentee.username} successfully!')
            return redirect('accounts:task_list')
    else:
        form = TaskAssignmentForm(mentor=request.user)

    context = {
        'form': form,
        'action': 'Create Task'
    }
    return render(request, 'accounts/task_form.html', context)


@login_required
def task_list_view(request):
    """Show task assignments - mentors see all tasks, mentees see only their tasks."""
    if not request.user.profile.organization:
        messages.warning(request, 'You must join an organization first.')
        return redirect('accounts:profile')

    if request.user.profile.role == 'mentor':
        # Mentors see all tasks they've assigned
        tasks = TaskAssignment.objects.filter(mentor=request.user)
    else:
        # Mentees see only tasks assigned to them
        tasks = TaskAssignment.objects.filter(mentee=request.user)

    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    # Calculate task statistics
    from django.db.models import Count
    task_stats = {
        'total': tasks.count(),
        'pending': tasks.filter(status='pending').count(),
        'in_progress': tasks.filter(status='in_progress').count(),
        'completed': tasks.filter(status='completed').count(),
        'overdue': tasks.filter(status='overdue').count(),
    }

    context = {
        'tasks': tasks.select_related('mentee', 'mentor'),
        'task_stats': task_stats,
        'status_filter': status_filter,
        'is_mentor': request.user.profile.role == 'mentor'
    }
    return render(request, 'accounts/task_list.html', context)


@login_required
def task_detail_view(request, task_id):
    """View task details and update status."""
    task = get_object_or_404(TaskAssignment, id=task_id)

    # Check permissions
    if request.user.profile.role == 'mentor':
        # Mentors can only see tasks they created
        if task.mentor != request.user:
            messages.error(request, 'You can only view tasks you created.')
            return redirect('accounts:task_list')
    else:
        # Mentees can only see tasks assigned to them
        if task.mentee != request.user:
            messages.error(request, 'You can only view tasks assigned to you.')
            return redirect('accounts:task_list')

    if request.method == 'POST':
        if request.user.profile.role == 'mentee':
            # Mentees can update status and notes
            form = TaskUpdateForm(request.POST, instance=task)
            if form.is_valid():
                updated_task = form.save()

                # Notify mentor of status change
                if updated_task.status == 'completed':
                    NotificationService.send_notification(
                        recipient=updated_task.mentor,
                        trigger_event='task_completed',
                        subject=f'Task Completed: {updated_task.title}',
                        message=f'''Hi {updated_task.mentor.first_name or updated_task.mentor.username},

Your mentee {updated_task.mentee.username} has completed the task: {updated_task.title}

Completion Notes: {updated_task.notes}

Best regards,
MentorFlow Team''',
                        notification_type='email'
                    )

                messages.success(request, 'Task updated successfully!')
                return redirect('accounts:task_detail', task_id=task.id)

    if request.user.profile.role == 'mentee':
        form = TaskUpdateForm(instance=task)
    else:
        form = None

    # Check if task is overdue
    is_overdue = task.status != 'completed' and task.due_date < timezone.now().date()

    context = {
        'task': task,
        'form': form,
        'is_mentor': request.user.profile.role == 'mentor',
        'is_overdue': is_overdue
    }
    return render(request, 'accounts/task_detail.html', context)


@login_required
def task_update_view(request, task_id):
    """Mentor updates task details."""
    if request.user.profile.role != 'mentor':
        messages.error(request, 'Only mentors can update task details.')
        return redirect('accounts:profile')

    task = get_object_or_404(TaskAssignment, id=task_id, mentor=request.user)

    if request.method == 'POST':
        form = TaskAssignmentForm(request.POST, instance=task, mentor=request.user)
        if form.is_valid():
            updated_task = form.save()
            messages.success(request, f'Task "{updated_task.title}" updated successfully!')

            # Notify mentee of changes
            NotificationService.send_notification(
                recipient=updated_task.mentee,
                trigger_event='task_updated',
                subject=f'Task Updated: {updated_task.title}',
                message=f'''Hi {updated_task.mentee.first_name or updated_task.mentee.username},

Your mentor has updated the task: {updated_task.title}

Please log in to view the updated task details.

Best regards,
MentorFlow Team''',
                notification_type='email'
            )

            return redirect('accounts:task_detail', task_id=task.id)
    else:
        form = TaskAssignmentForm(instance=task, mentor=request.user)

    context = {
        'form': form,
        'task': task,
        'action': 'Update Task'
    }
    return render(request, 'accounts/task_form.html', context)


@login_required
def task_delete_view(request, task_id):
    """Mentor deletes a task."""
    if request.user.profile.role != 'mentor':
        messages.error(request, 'Only mentors can delete tasks.')
        return redirect('accounts:profile')

    task = get_object_or_404(TaskAssignment, id=task_id, mentor=request.user)

    if request.method == 'POST':
        task_title = task.title
        task.delete()
        messages.success(request, f'Task "{task_title}" deleted successfully!')
        return redirect('accounts:task_list')

    context = {
        'task': task
    }
    return render(request, 'accounts/task_confirm_delete.html', context)


# ==================== Meeting Views ====================

@login_required
def meeting_create_view(request):
    """Mentor schedules a new meeting with a mentee."""
    if request.user.profile.role != 'mentor':
        messages.error(request, 'Only mentors can schedule meetings.')
        return redirect('accounts:profile')

    if not request.user.profile.organization:
        messages.warning(request, 'You must join an organization first.')
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = MeetingForm(request.POST, mentor=request.user)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.mentor = request.user
            meeting.save()

            # Send notification to mentee
            NotificationService.send_notification(
                recipient=meeting.mentee,
                trigger_event='meeting_scheduled',
                subject=f'Meeting Scheduled: {meeting.title}',
                message=f'''Hi {meeting.mentee.first_name or meeting.mentee.username},

Your mentor has scheduled a meeting with you.

Title: {meeting.title}
Date & Time: {meeting.start_time.strftime('%Y-%m-%d %I:%M %p')}
End Time: {meeting.end_time.strftime('%I:%M %p')}

Description: {meeting.description}

{"Google Meet Link: " + meeting.google_meet_url if meeting.google_meet_url else ""}

Please log in to view meeting details and join when it's time.

Best regards,
MentorFlow Team''',
                notification_type='email'
            )

            messages.success(request, f'Meeting "{meeting.title}" scheduled with {meeting.mentee.username} successfully!')
            return redirect('accounts:meeting_list')
    else:
        form = MeetingForm(mentor=request.user)

    context = {
        'form': form,
        'action': 'Schedule Meeting'
    }
    return render(request, 'accounts/meeting_form.html', context)


@login_required
def meeting_list_view(request):
    """Show meetings - mentors see all meetings, mentees see only their meetings."""
    if not request.user.profile.organization:
        messages.warning(request, 'You must join an organization first.')
        return redirect('accounts:profile')

    if request.user.profile.role == 'mentor':
        # Mentors see all meetings they've scheduled
        meetings = Meeting.objects.filter(mentor=request.user)
    else:
        # Mentees see only meetings scheduled for them
        meetings = Meeting.objects.filter(mentee=request.user)

    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        meetings = meetings.filter(status=status_filter)

    # Separate upcoming and past meetings
    now = timezone.now()
    upcoming_meetings = meetings.filter(start_time__gt=now, status='scheduled')
    past_meetings = meetings.filter(start_time__lte=now) | meetings.exclude(status='scheduled')

    context = {
        'upcoming_meetings': upcoming_meetings.select_related('mentee', 'mentor'),
        'past_meetings': past_meetings.select_related('mentee', 'mentor'),
        'status_filter': status_filter,
        'is_mentor': request.user.profile.role == 'mentor',
        'now': now
    }
    return render(request, 'accounts/meeting_list.html', context)


@login_required
def meeting_detail_view(request, meeting_id):
    """View meeting details with join meeting button."""
    meeting = get_object_or_404(Meeting, id=meeting_id)

    # Check permissions
    if request.user.profile.role == 'mentor':
        # Mentors can only see meetings they created
        if meeting.mentor != request.user:
            messages.error(request, 'You can only view meetings you created.')
            return redirect('accounts:meeting_list')
    else:
        # Mentees can only see meetings scheduled for them
        if meeting.mentee != request.user:
            messages.error(request, 'You can only view meetings scheduled for you.')
            return redirect('accounts:meeting_list')

    # Check if meeting is joinable (within 15 minutes of start time)
    is_joinable = meeting.is_joinable()

    context = {
        'meeting': meeting,
        'is_mentor': request.user.profile.role == 'mentor',
        'is_joinable': is_joinable
    }
    return render(request, 'accounts/meeting_detail.html', context)


@login_required
def meeting_update_view(request, meeting_id):
    """Mentor updates meeting details."""
    if request.user.profile.role != 'mentor':
        messages.error(request, 'Only mentors can update meeting details.')
        return redirect('accounts:profile')

    meeting = get_object_or_404(Meeting, id=meeting_id, mentor=request.user)

    if request.method == 'POST':
        form = MeetingForm(request.POST, instance=meeting, mentor=request.user)
        if form.is_valid():
            updated_meeting = form.save()
            messages.success(request, f'Meeting "{updated_meeting.title}" updated successfully!')

            # Notify mentee of changes
            if updated_meeting.status != 'cancelled':
                NotificationService.send_notification(
                    recipient=updated_meeting.mentee,
                    trigger_event='meeting_updated',
                    subject=f'Meeting Updated: {updated_meeting.title}',
                    message=f'''Hi {updated_meeting.mentee.first_name or updated_meeting.mentee.username},

Your mentor has updated the meeting: {updated_meeting.title}

New Date & Time: {updated_meeting.start_time.strftime('%Y-%m-%d %I:%M %p')}

Please log in to view the updated meeting details.

Best regards,
MentorFlow Team''',
                    notification_type='email'
                )

            return redirect('accounts:meeting_detail', meeting_id=meeting.id)
    else:
        form = MeetingForm(instance=meeting, mentor=request.user)

    context = {
        'form': form,
        'meeting': meeting,
        'action': 'Update Meeting'
    }
    return render(request, 'accounts/meeting_form.html', context)


@login_required
def meeting_cancel_view(request, meeting_id):
    """Mentor cancels a meeting."""
    if request.user.profile.role != 'mentor':
        messages.error(request, 'Only mentors can cancel meetings.')
        return redirect('accounts:profile')

    meeting = get_object_or_404(Meeting, id=meeting_id, mentor=request.user)

    if request.method == 'POST':
        meeting.status = 'cancelled'
        meeting.save()

        # Notify mentee of cancellation
        NotificationService.send_notification(
            recipient=meeting.mentee,
            trigger_event='meeting_cancelled',
            subject=f'Meeting Cancelled: {meeting.title}',
            message=f'''Hi {meeting.mentee.first_name or meeting.mentee.username},

Your mentor has cancelled the meeting: {meeting.title}

Scheduled for: {meeting.start_time.strftime('%Y-%m-%d %I:%M %p')}

The meeting has been cancelled. Your mentor will reschedule if needed.

Best regards,
MentorFlow Team''',
            notification_type='email'
        )

        messages.success(request, f'Meeting "{meeting.title}" cancelled successfully!')
        return redirect('accounts:meeting_list')

    context = {
        'meeting': meeting
    }
    return render(request, 'accounts/meeting_confirm_cancel.html', context)
