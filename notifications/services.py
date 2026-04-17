from django.core.mail import send_mail
from django.conf import settings
from .models import Notification
from .sms_providers import MNotifySMSProvider


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
                notification.sent_successfully = True
            elif notification_type == 'sms':
                # Check if user has SMS enabled and phone number
                if not (recipient.profile.phone_number and recipient.profile.sms_notifications_enabled):
                    notification.error_message = "SMS not enabled or no phone number provided"
                    notification.save()
                    return notification

                # Send SMS using mNotify
                sms_provider = MNotifySMSProvider()
                result = sms_provider.send_sms(
                    recipient_phone=str(recipient.profile.phone_number),
                    message=message
                )

                if result['success']:
                    notification.sent_successfully = True
                else:
                    notification.error_message = result['message']

            notification.save()
        except Exception as e:
            notification.error_message = str(e)
            notification.save()

        return notification
