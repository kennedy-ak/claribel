"""
Script to create initial users for the mentorship platform.
Run this after migrations to create admin, mentor, and mentee accounts.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mentorship_platform.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile


def create_users():
    # Create admin/superuser
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@mentorship.com',
            password='admin123'
        )
        admin.profile.role = 'mentor'
        admin.profile.email_notifications_enabled = True
        admin.profile.save()
        print(f"✓ Created admin user: {admin.username}")
    else:
        print("✗ Admin user already exists")

    # Create a mentor
    if not User.objects.filter(username='mentor1').exists():
        mentor = User.objects.create_user(
            username='mentor1',
            email='mentor1@example.com',
            password='mentor123',
            first_name='John',
            last_name='Mentor'
        )
        mentor.profile.role = 'mentor'
        mentor.profile.email_notifications_enabled = True
        mentor.profile.save()
        print(f"✓ Created mentor user: {mentor.username}")
    else:
        print("✗ Mentor user already exists")

    # Create a mentee
    if not User.objects.filter(username='mentee1').exists():
        mentee = User.objects.create_user(
            username='mentee1',
            email='mentee1@example.com',
            password='mentee123',
            first_name='Jane',
            last_name='Mentee'
        )
        mentee.profile.role = 'mentee'
        mentee.profile.email_notifications_enabled = True
        mentee.profile.mentor = mentor.profile
        mentee.profile.save()
        print(f"✓ Created mentee user: {mentee.username}")
        print(f"  - Assigned to mentor: {mentor.username}")
    else:
        print("✗ Mentee user already exists")

    print("\n" + "="*50)
    print("User Accounts Created Successfully!")
    print("="*50)
    print("\nLogin Credentials:")
    print("┌────────────┬──────────────┬────────────┐")
    print("│ Type       │ Username     │ Password   │")
    print("├────────────┼──────────────┼────────────┤")
    print("│ Admin      │ admin        │ admin123   │")
    print("│ Mentor     │ mentor1      │ mentor123  │")
    print("│ Mentee     │ mentee1      │ mentee123  │")
    print("└────────────┴──────────────┴────────────┘")
    print("\nNext Steps:")
    print("1. Run the development server: python manage.py runserver")
    print("2. Login to admin panel: http://127.0.0.1:8000/admin/")
    print("3. Login to app: http://127.0.0.1:8000/accounts/login/")
    print("4. Configure email settings in settings.py for notifications")
    print("5. Optional: Configure Twilio for SMS notifications")


if __name__ == '__main__':
    create_users()
