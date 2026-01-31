from django.contrib import admin
from django.conf import settings
from .models import UserProfile, Organization, MentorAssignment

# Apply MentorFlow branding to admin site
admin.site.site_title = getattr(settings, 'ADMIN_SITE_TITLE', 'MentorFlow Administration')
admin.site.site_header = getattr(settings, 'ADMIN_SITE_HEADER', 'MentorFlow')
admin.site.index_title = getattr(settings, 'ADMIN_INDEX_TITLE', 'Welcome to MentorFlow Admin Portal')


class MentorAssignmentInline(admin.TabularInline):
    model = MentorAssignment
    extra = 0
    fk_name = 'mentee'
    fields = ['mentor', 'is_active', 'assigned_at', 'notes']
    readonly_fields = ['assigned_at']


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'join_code', 'is_active', 'created_at', 'get_mentor_count', 'get_mentee_count']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'join_code', 'created_by__username']
    readonly_fields = ['join_code', 'created_at']

    def get_mentor_count(self, obj):
        return obj.get_mentors().count()
    get_mentor_count.short_description = 'Mentors'

    def get_mentee_count(self, obj):
        return obj.get_mentees().count()
    get_mentee_count.short_description = 'Mentees'


@admin.register(MentorAssignment)
class MentorAssignmentAdmin(admin.ModelAdmin):
    list_display = ['mentee', 'mentor', 'is_active', 'assigned_at', 'assigned_by']
    list_filter = ['is_active', 'assigned_at']
    search_fields = ['mentee__user__username', 'mentor__user__username', 'notes']
    readonly_fields = ['assigned_at']
    date_hierarchy = 'assigned_at'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'organization', 'email_notifications_enabled', 'sms_notifications_enabled', 'get_current_mentor_display']
    list_filter = ['role', 'organization', 'email_notifications_enabled', 'sms_notifications_enabled']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'organization__name']
    inlines = [MentorAssignmentInline]

    def get_current_mentor_display(self, obj):
        if obj.role == 'mentee':
            mentor = obj.get_current_mentor()
            if mentor:
                return mentor.user.username
            return 'Unassigned'
        return 'N/A'
    get_current_mentor_display.short_description = 'Current Mentor'
