from django.db import models
from django.contrib.auth.models import User

class TodoList(models.Model):
    mentee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todo_lists')
    submission_date = models.DateField(auto_now_add=True)
    is_submitted_to_mentor = models.BooleanField(default=False)
    mentor_notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['mentee', 'submission_date']

    def __str__(self):
        return f"Todo List - {self.mentee.username} ({self.submission_date})"


class TodoItem(models.Model):
    PRIORITY_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]
    STATUS_CHOICES = [('pending', 'Pending'), ('completed', 'Completed')]

    todo_list = models.ForeignKey(TodoList, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.title} - {self.get_priority_display()}"
