# Django Mentorship Platform

A comprehensive Django-based mentorship management system where mentors can manage multiple mentees. Mentees receive reminders to submit daily todo lists (morning) and daily reports (evening). Mentors receive notifications and can view submissions, provide feedback, and send messages.

## Features

### For Mentees
- **Daily Todo Lists**: Create and manage daily task lists with priorities
- **Evening Reports**: Submit daily progress reports with mood tracking, achievements, challenges, and goals
- **Messaging**: Communicate directly with assigned mentors
- **Automated Reminders**: Email/SMS reminders at scheduled times (8 AM for todos, 6 PM for reports)

### For Mentors
- **Dashboard**: Overview of all assigned mentees
- **Review Todos**: View and provide feedback on mentee todo lists
- **Review Reports**: Access and give feedback on daily reports
- **Messaging**: Send messages to mentees
- **Admin Panel**: Manage users and monitor platform activity

## Tech Stack

- **Backend**: Django 6.0
- **Frontend**: HTML/CSS, Bootstrap 5
- **Database**: SQLite
- **Notifications**: Email (SMTP), SMS (Twilio - optional)
- **Task Scheduling**: django-crontab

## Installation

### Prerequisites
- Python 3.9+
- pip package manager

### Setup Instructions

1. **Navigate to the project directory**
   ```bash
   cd C:\Users\User2\Desktop\claribel
   ```

2. **Activate virtual environment** (if using one)
   ```bash
   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install django django-crontab
   # Optional for SMS:
   pip install twilio
   ```

4. **Run migrations** (already done)
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create users** (already done)
   ```bash
   python create_superuser.py
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - App: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/

## Default Login Credentials

| Type      | Username | Password |
|-----------|----------|----------|
| Admin     | admin    | admin123 |
| Mentor    | mentor1  | mentor123 |
| Mentee    | mentee1  | mentee123 |

## Configuration

### Email Settings (Required for notifications)

Edit `mentorship_platform/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Use App Password for Gmail
DEFAULT_FROM_EMAIL = 'Mentorship Platform <noreply@mentorship.com>'
```

**For Gmail:**
1. Enable 2-Factor Authentication
2. Generate an App Password: Google Account → Security → App Passwords
3. Use the App Password in `EMAIL_HOST_PASSWORD`

### Twilio SMS Configuration (Optional)

Edit `mentorship_platform/settings.py`:

```python
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = '+1234567890'
```

### Cron Job Configuration

The system is configured to send reminders at:
- **8:00 AM** - Morning reminder to create todo lists
- **6:00 PM** - Evening reminder to submit reports

To enable cron jobs on Linux/Mac:
```bash
python manage.py crontab add
```

To view active cron jobs:
```bash
python manage.py crontab show
```

To remove all cron jobs:
```bash
python manage.py crontab remove
```

**Note**: On Windows, django-crontab may not work. Use Windows Task Scheduler or run manually:
```bash
python -c "from notifications.cron import send_morning_reminders; send_morning_reminders()"
python -c "from notifications.cron import send_evening_reminders; send_evening_reminders()"
```

## Project Structure

```
claribel/
├── mentorship_platform/    # Main project settings
│   ├── settings.py         # Configuration
│   ├── urls.py             # Root URL configuration
│   └── wsgi.py
├── accounts/               # User management
│   ├── models.py           # UserProfile model
│   ├── views.py            # Auth, dashboards
│   ├── urls.py
│   └── signals.py          # Auto-create profiles
├── todo/                   # Todo list management
│   ├── models.py           # TodoList, TodoItem
│   ├── views.py            # Create, view todos
│   └── forms.py            # Todo forms
├── reports/                # Daily reports
│   ├── models.py           # DailyReport
│   └── views.py            # Create, view reports
├── notifications/          # Messaging & alerts
│   ├── models.py           # Notification, Message
│   ├── services.py         # Email/SMS service
│   ├── cron.py             # Scheduled tasks
│   └── views.py            # Inbox, messaging
├── templates/              # HTML templates
│   ├── base.html           # Base template
│   ├── accounts/           # Account templates
│   ├── todo/               # Todo templates
│   ├── reports/            # Report templates
│   └── notifications/      # Notification templates
├── static/                 # Static files
│   └── css/
│       └── custom.css      # Custom styles
├── db.sqlite3              # Database (SQLite)
├── manage.py
└── create_superuser.py     # User creation script
```

## Usage Guide

### Admin Panel Usage

1. **Login to Admin Panel**: http://127.0.0.1:8000/admin/
2. **Manage Users**:
   - Go to "User Profiles" to view all users
   - Set user roles (mentor/mentee)
   - Assign mentees to mentors
   - Configure notification preferences

### Mentee Workflow

1. **Login**: Navigate to http://127.0.0.1:8000/accounts/login/
2. **Morning**: Receive reminder at 8 AM
   - Go to "Create Todo"
   - Add tasks with priorities (High/Medium/Low)
   - Submit todo list
3. **Evening**: Receive reminder at 6 PM
   - Go to "Submit Report"
   - Rate your mood (1-5)
   - Share achievements, challenges, learnings
   - Set goals for tomorrow
4. **Communicate**: Use "Messages" to contact mentor

### Mentor Workflow

1. **Login**: Navigate to http://127.0.0.1:8000/accounts/login/
2. **Dashboard**: View all assigned mentees
3. **Review Todos**:
   - Go to "Mentee Todos"
   - Click on a todo list to view details
   - Add mentor notes
   - Mark as reviewed
4. **Review Reports**:
   - Go to "Mentee Reports"
   - Click on a report to view details
   - Provide feedback
5. **Communicate**: Send messages to mentees

## Testing the System

### Test Morning Reminder (Manual Trigger)
```bash
python -c "from notifications.cron import send_morning_reminders; send_morning_reminders()"
```

### Test Evening Reminder (Manual Trigger)
```bash
python -c "from notifications.cron import send_evening_reminders; send_evening_reminders()"
```

### Create New Users

**Via Admin Panel:**
1. Go to http://127.0.0.1:8000/admin/
2. Add User in "Users" section
3. Set role in "User Profiles" section
4. For mentees, assign a mentor

**Via Script:**
Edit `create_superuser.py` and add more users following the existing pattern.

## Troubleshooting

### Email Not Sending
- Check SMTP settings in `settings.py`
- Verify email credentials
- For Gmail, use App Password (not regular password)
- Check firewall/antivirus blocking port 587

### Cron Jobs Not Running (Windows)
- django-crontab doesn't work on Windows
- Use Windows Task Scheduler instead
- Or run manually using Python commands

### Twilio SMS Issues
- Verify Twilio credentials
- Check phone number format (include country code: +1234567890)
- Ensure mentee has phone_number in profile
- Verify SMS notifications are enabled for user

### Static Files Not Loading
```bash
python manage.py collectstatic
```

## Production Deployment

For production deployment:

1. **Change Security Settings**:
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['yourdomain.com']
   SECRET_KEY = 'generate-new-secret-key'
   ```

2. **Use Production Database**:
   - PostgreSQL or MySQL recommended
   - Update DATABASES setting

3. **Serve Static Files**:
   - Use WhiteNoise or serve via CDN

4. **Use Production Web Server**:
   - Gunicorn or uWSGI
   - Configure with Nginx/Apache

5. **Environment Variables**:
   - Store sensitive credentials in .env file
   - Use django-environ or python-dotenv

## License

This project is for educational purposes.

## Support

For issues or questions, refer to Django documentation:
- Django Docs: https://docs.djangoproject.com/
- Bootstrap Docs: https://getbootstrap.com/docs/
- Twilio Docs: https://www.twilio.com/docs

---

**Built with Django 6.0 | Bootstrap 5 | Python 3.13**
