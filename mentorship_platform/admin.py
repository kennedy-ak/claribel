"""
Custom Admin Configuration for MentorFlow
"""
from django.contrib import admin
from django.contrib.admin import AdminSite

# Custom Admin Site for MentorFlow branding
class MentorFlowAdminSite(AdminSite):
    site_title = "MentorFlow Administration"
    site_header = "MentorFlow"
    index_title = "Welcome to MentorFlow Admin Portal"

    def get_app_list(self, request):
        """
        Reorder apps in admin dashboard
        """
        app_list = super().get_app_list(request)
        # Priority order: Accounts, Todo, Reports, Notifications
        priority = {"accounts": 1, "todo": 2, "reports": 3, "notifications": 4}
        app_list.sort(key=lambda x: priority.get(x.get("app_label", ""), 99))
        return app_list

# Create custom admin site instance
mentorflow_admin_site = MentorFlowAdminSite(name="mentorflow_admin")
