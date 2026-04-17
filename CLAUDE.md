# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MentorFlow is a Django 6.0 mentorship platform where mentors manage multiple mentees. The platform uses organization-based multi-tenancy, role-based access control, and automated notifications (email/SMS) to facilitate daily todo tracking and progress reporting.

## Core Architecture

### App Structure
- **accounts/**: User management, profiles, roles, organizations, authentication
- **todo/**: Daily todo list creation and management (mentee → mentor workflow)
- **reports/**: Daily progress reporting with mood tracking
- **notifications/**: Messaging system, email/SMS notifications, scheduled reminders

### Data Model Patterns
- **UserProfile**: One-to-one with User, contains role (mentor/mentee), organization, notification preferences
- **Organization**: Multi-tenancy container, users belong to orgs, join codes for new org setup
- **MentorAssignment**: Tracks mentor-mentee relationships, supports reassignment with history
- **Notification**: Logs all notification attempts (email/SMS), includes error tracking
- **TodoList + DailyReport**: Daily workflow artifacts, one-per-day per mentee

### Service Layer Pattern
- `NotificationService` in `notifications/services.py`: Centralized notification handling
- `MNotifySMSProvider` in `notifications/sms_providers.py`: SMS provider abstraction
- Services handle both email and SMS, with graceful degradation when providers unavailable

### Signal Integration
- `accounts/signals.py`: Auto-creates UserProfile on User creation
- Registered in `accounts/apps.py.py` via `ready()` method

## Development Commands

### Server & Database
```bash
# Run development server
python manage.py runserver

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser interactively
python manage.py createsuperuser

# Create test users via script
python create_superuser.py
```

### Scheduled Tasks (Cron)
```bash
# Add cron jobs (Linux/Mac only)
python manage.py crontab add

# Show active cron jobs
python manage.py crontab show

# Remove all cron jobs
python manage.py crontab remove

# Manual trigger for testing (Windows compatible)
python -c "from notifications.cron import send_morning_reminders; send_morning_reminders()"
python -c "from notifications.cron import send_evening_reminders; send_evening_reminders()"
```

### Testing & Debugging
```bash
# Django shell for testing
python manage.py shell

# Test SMS provider
python -c "from notifications.sms_providers import MNotifySMSProvider; provider = MNotifySMSProvider(); print(provider.send_sms('0201234567', 'Test message'))"

# Check system for issues
python manage.py check
```

## Configuration Requirements

### Environment Variables (.env)
Required for email/SMS functionality:
```
MNOTIFY_API_KEY=your_mnotify_api_key
MNOTIFY_SENDER_ID=MentorFlow
DATABASE_URL=sqlite:///db.sqlite3  # or PostgreSQL URL
```

### Email Settings
- Configured in `mentorship_platform/settings.py`
- Default: Gmail SMTP (requires App Password)
- Update `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` for production

### SMS Configuration
- Provider: mNotify (Ghana-focused SMS service)
- API key: https://apps.mnotify.net/api/api
- Phone format: `02XXXXXXXXX` or `+233XXXXXXXXX`
- Fallback: Gracefully handles SMS failures

### Cron Schedule
- **8:00 AM**: Morning todo reminders (`send_morning_reminders`)
- **6:00 PM**: Evening report reminders (`send_evening_reminders`)
- **Windows**: django-crontab incompatible, use manual triggers or Task Scheduler

## Key Business Logic

### Mentor-Mentee Assignment
- Mentees assigned via `MentorAssignment` model
- One active assignment per mentee at a time
- Reassignment deactivates previous assignment (preserves history)
- Organization boundary: mentors can only mentor mentees in same org

### Daily Workflow
1. **Morning (8 AM)**: Mentees receive reminder to create todo list
2. **Todo Creation**: Mentees create TodoList with TodoItems (High/Medium/Low priority)
3. **Todo Review**: Mentors view submitted todos, add notes, mark as reviewed
4. **Evening (6 PM)**: Mentees receive reminder to submit daily report
5. **Daily Report**: Mentees submit progress (mood, achievements, challenges, goals)
6. **Report Review**: Mentors provide feedback on reports

### Notification Routing
- **Todo Submissions**: Mentor receives notification when mentee submits todo
- **New Messages**: Users receive SMS for new messages (if enabled)
- **Reminders**: Email + SMS to mentees based on notification preferences
- **All notifications logged**: Check `Notification` model for delivery status

## Important Constraints

### Platform Limitations
- **Cron on Windows**: django-crontab doesn't work, use manual triggers or Task Scheduler
- **SMS Region**: mNotify optimized for Ghanaian phone numbers
- **Database**: SQLite default, PostgreSQL recommended for production

### Data Integrity
- Organization isolation enforced in `MentorAssignment.save()`
- Unique constraints: One todo list per mentee per day
- Cascade deletes: User deletion deletes profile, but assignments preserve history

### Security Considerations
- `SECRET_KEY` in settings.py (move to environment variable for production)
- `DEBUG = True` (change to `False` for production)
- CORS configured for specific domains only
- CSRF trusted origins configured for cross-origin requests

## URL Patterns & Namespacing

All apps use namespaced URLs:
- `accounts:login`, `accounts:profile`, `accounts:mentor_dashboard`, etc.
- `todo:create`, `todo:today`, `todo:mentor_todos`, etc.
- `reports:create`, `reports:today`, `reports:mentor_reports`, etc.
- `notifications:inbox`, `notifications:send`, `notifications:message_detail`, etc.

Direct dashboard access routes available:
- `/dashboard/mentor/` → `mentor_dashboard_direct`
- `/dashboard/mentee/` → `mentee_dashboard_direct`

## Admin Panel

- **Branding**: Custom "MentorFlow" branding configured in settings
- **User Management**: Create users via admin, assign roles in UserProfile
- **Organization Setup**: Create orgs, share join codes for new member registration
- **Notification Monitoring**: Check `Notification` model for delivery status/errors
- **Assignment Management**: View/manage mentor-mentee assignments via admin

## Common Patterns

### Querying Mentor-Mentee Relationships
```python
# Get mentees for a mentor
mentees = mentor_profile.get_mentees()

# Get current mentor for a mentee
mentor = mentee_profile.get_current_mentor()

# Filter by organization
org_mentors = Organization.objects.get(name="Org Name").get_mentors()
```

### Notification Service Usage
```python
from notifications.services import NotificationService

NotificationService.send_notification(
    recipient=user,
    trigger_event='todo_submitted',
    subject='New Todo Submitted',
    message='Your mentee submitted a todo list',
    notification_type='email'  # or 'sms'
)
```

### Checking Notification Delivery
```python
# All notifications logged in Notification model
failed_notifications = Notification.objects.filter(sent_successfully=False)
recent_notifications = Notification.objects.filter(recipient=user).order_by('-created_at')[:10]
```

## Production Deployment Checklist

- [ ] Update `ALLOWED_HOSTS` with production domain
- [ ] Set `DEBUG = False`
- [ ] Move `SECRET_KEY` to environment variable
- [ ] Configure production database (PostgreSQL recommended)
- [ ] Set up production web server (Gunicorn)
- [ ] Configure reverse proxy (Nginx/Apache)
- [ ] Enable HTTPS
- [ ] Set up monitoring (error tracking, SMS balance monitoring)
- [ ] Configure logging
- [ ] Set up backup strategy
- [ ] Test email/SMS delivery with production credentials
- [ ] Set up cron jobs or alternative task scheduler
- [ ] Review and update CORS settings for production domain