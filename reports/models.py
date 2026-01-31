from django.db import models
from django.contrib.auth.models import User

class DailyReport(models.Model):
    MOOD_CHOICES = [(1, 'Very Bad'), (2, 'Bad'), (3, 'Neutral'), (4, 'Good'), (5, 'Very Good')]

    mentee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_reports')
    report_date = models.DateField(auto_now_add=True)
    mood = models.IntegerField(choices=MOOD_CHOICES)
    achievements = models.TextField()
    challenges = models.TextField(blank=True)
    learnings = models.TextField(blank=True)
    next_steps = models.TextField(help_text="Your plans, action items, or goals for the next session/day")
    mentor_feedback = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['mentee', 'report_date']
        ordering = ['-report_date']

    def __str__(self):
        return f"Daily Report - {self.mentee.username} ({self.report_date})"
