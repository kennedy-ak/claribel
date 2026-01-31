from django.contrib import admin
from .models import DailyReport


@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    list_display = ['mentee', 'report_date', 'mood', 'has_mentor_feedback']
    list_filter = ['mood', 'report_date']
    search_fields = ['mentee__username', 'mentee__email', 'achievements', 'next_steps']
    date_hierarchy = 'report_date'
    readonly_fields = ['mentee', 'report_date', 'mood', 'achievements', 'challenges', 'learnings', 'next_steps']

    def has_mentor_feedback(self, obj):
        return bool(obj.mentor_feedback)
    has_mentor_feedback.boolean = True
    has_mentor_feedback.short_description = 'Feedback Given'
