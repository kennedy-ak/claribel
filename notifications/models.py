from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [('email', 'Email'), ('sms', 'SMS'), ('in_app', 'In App')]
    TRIGGER_EVENT_CHOICES = [
        ('morning_reminder', 'Morning Reminder'),
        ('evening_reminder', 'Evening Reminder'),
        ('todo_submitted', 'Todo Submitted'),
        ('report_submitted', 'Report Submitted'),
        ('message_received', 'Message Received'),
        ('mentor_assigned', 'Mentor Assigned'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPE_CHOICES, default='email')
    trigger_event = models.CharField(max_length=30, choices=TRIGGER_EVENT_CHOICES)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    sent_successfully = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.subject} - {self.recipient.username}"


class Conversation(models.Model):
    """A conversation thread between two users."""
    participant1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_p1')
    participant2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_p2')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        unique_together = ['participant1', 'participant2']

    def __str__(self):
        return f"Conversation: {self.participant1.username} ↔ {self.participant2.username}"

    def get_other_participant(self, user):
        """Get the other participant in the conversation."""
        if user == self.participant1:
            return self.participant2
        return self.participant1

    def get_last_message(self):
        """Get the most recent message in this conversation."""
        return self.messages.first()

    def get_unread_count(self, user):
        """Get count of unread messages for a user."""
        return self.messages.filter(is_read=False, sender__ne=user).count()


class Message(models.Model):
    """Individual message within a conversation."""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages',
                                     null=True, blank=True)  # Temporarily nullable for migration
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_thread_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f"{self.sender.username}: {preview}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update conversation's updated_at timestamp
        self.conversation.save()
