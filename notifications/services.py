from django.core.mail import send_mail
from django.conf import settings
from .models import Notification

try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False


class NotificationService:
    @staticmethod
    def send_notification(recipient, trigger_event, subject, message, notification_type='email'):
        """
        Send a notification to a user via email, SMS, or in-app.

        Args:
            recipient: User object
            trigger_event: The event that triggered this notification
            subject: Subject line for the notification
            message: Message content
            notification_type: 'email', 'sms', or 'in_app'
        """
        notification = Notification.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            trigger_event=trigger_event,
            subject=subject,
            message=message
        )

        try:
            if notification_type == 'email':
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient.email],
                    fail_silently=False
                )
            elif notification_type == 'sms':
                if not TWILIO_AVAILABLE:
                    notification.error_message = "Twilio is not installed"
                    notification.save()
                    return notification

                if recipient.profile.phone_number and recipient.profile.sms_notifications_enabled:
                    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                    client.messages.create(
                        body=message,
                        from_=settings.TWILIO_PHONE_NUMBER,
                        to=recipient.profile.phone_number
                    )
                else:
                    notification.error_message = "SMS not enabled or no phone number provided"
                    notification.save()
                    return notification

            notification.sent_successfully = True
            notification.save()
        except Exception as e:
            notification.error_message = str(e)
            notification.save()

        return notification
