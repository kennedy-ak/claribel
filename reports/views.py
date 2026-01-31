from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from .models import DailyReport
from notifications.services import NotificationService


@login_required
def report_create_view(request):
    if request.user.profile.role != 'mentee':
        messages.error(request, 'Only mentees can submit reports.')
        return redirect('accounts:profile')

    # Check if report already exists for today
    today = timezone.now().date()
    existing_report = DailyReport.objects.filter(
        mentee=request.user,
        report_date=today
    ).first()

    if existing_report:
        messages.info(request, 'You have already submitted a report for today.')
        return redirect('reports:today')

    if request.method == 'POST':
        report = DailyReport.objects.create(
            mentee=request.user,
            mood=int(request.POST.get('mood', 3)),
            achievements=request.POST.get('achievements', ''),
            challenges=request.POST.get('challenges', ''),
            learnings=request.POST.get('learnings', ''),
            next_steps=request.POST.get('next_steps', '')
        )

        messages.success(request, 'Daily report submitted successfully!')

        # Notify mentor if assigned
        current_mentor = request.user.profile.get_current_mentor()
        if current_mentor:
            NotificationService.send_notification(
                recipient=current_mentor.user,
                trigger_event='report_submitted',
                subject=f'Daily Report from {request.user.username}',
                message=f'{request.user.username} has submitted their daily report. '
                       f'Please review it on the mentor dashboard.',
                notification_type='email'
            )

        return redirect('reports:today')

    return render(request, 'reports/report_form.html')


@login_required
def report_today_view(request):
    if request.user.profile.role != 'mentee':
        return redirect('accounts:profile')

    today = timezone.now().date()
    report = DailyReport.objects.filter(
        mentee=request.user,
        report_date=today
    ).first()

    context = {
        'report': report,
        'today': today
    }
    return render(request, 'reports/report_today.html', context)


@login_required
def mentor_reports_view(request):
    if request.user.profile.role != 'mentor':
        return redirect('accounts:profile')

    mentees = request.user.profile.get_mentees()
    mentee_ids = [m.user.id for m in mentees]

    # Get recent reports from all mentees
    reports = DailyReport.objects.filter(
        mentee_id__in=mentee_ids
    ).select_related('mentee').order_by('-report_date')

    context = {
        'reports': reports
    }
    return render(request, 'reports/mentor_reports.html', context)


@login_required
def mentor_report_detail_view(request, report_id):
    if request.user.profile.role != 'mentor':
        return redirect('accounts:profile')

    report = get_object_or_404(DailyReport, id=report_id)

    # Verify this report belongs to one of the mentor's mentees
    mentee_ids = [m.user.id for m in request.user.profile.get_mentees()]
    if report.mentee_id not in mentee_ids:
        messages.error(request, 'You can only view reports of your mentees.')
        return redirect('reports:mentor_reports')

    if request.method == 'POST':
        feedback = request.POST.get('mentor_feedback', '')
        report.mentor_feedback = feedback
        report.save()
        messages.success(request, 'Feedback saved successfully.')
        return redirect('reports:mentor_report_detail', report_id=report_id)

    context = {
        'report': report
    }
    return render(request, 'reports/mentor_report_detail.html', context)
