from accounts.models import UserProfile
from .services import NotificationService


def send_morning_reminders():
    """
    Send morning reminders to all mentees to create their daily todo lists.
    This should be scheduled to run at 8 AM every day.
    """
    mentee_profiles = UserProfile.objects.filter(role='mentee', email_notifications_enabled=True)

    for profile in mentee_profiles:
        if profile.user.email:
            # Send email notification
            NotificationService.send_notification(
                recipient=profile.user,
                trigger_event='morning_reminder',
                subject='Good Morning! Time to Plan Your Day',
                message=f'''Hi {profile.user.first_name or profile.user.username},

It's time to create your todo list for today!

Please log in to the mentorship platform and create your daily todo list to track your tasks and goals.

Best regards,
Mentorship Platform Team''',
                notification_type='email'
            )

        # Send SMS notification if enabled
        if profile.sms_notifications_enabled and profile.phone_number:
            NotificationService.send_notification(
                recipient=profile.user,
                trigger_event='morning_reminder',
                subject='Todo Reminder',
                message='Morning! Time to create your todo list. Login to your dashboard.',
                notification_type='sms'
            )


def send_evening_reminders():
    """
    Send evening reminders to all mentees to submit their daily reports.
    This should be scheduled to run at 6 PM every day.
    """
    mentee_profiles = UserProfile.objects.filter(role='mentee', email_notifications_enabled=True)

    for profile in mentee_profiles:
        if profile.user.email:
            # Send email notification
            NotificationService.send_notification(
                recipient=profile.user,
                trigger_event='evening_reminder',
                subject='How Did Your Day Go?',
                message=f'''Hi {profile.user.first_name or profile.user.username},

It's time to submit your daily report!

Please log in to the mentorship platform and share:
- Your achievements today
- Any challenges you faced
- What you learned
- Your goals for tomorrow

Best regards,
Mentorship Platform Team''',
                notification_type='email'
            )

        # Send SMS notification if enabled
        if profile.sms_notifications_enabled and profile.phone_number:
            NotificationService.send_notification(
                recipient=profile.user,
                trigger_event='evening_reminder',
                subject='Daily Report',
                message='Evening! Time to submit your daily report. Login to your dashboard.',
                notification_type='sms'
            )
