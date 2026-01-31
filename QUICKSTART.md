# Quick Start Guide - Django Mentorship Platform

## 🚀 Get Started in 5 Minutes

### 1. Start the Server
```bash
cd C:\Users\User2\Desktop\claribel
python manage.py runserver
```

### 2. Open in Browser
- **Main App**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

### 3. Login with Test Accounts

**Mentor Account:**
- Username: `mentor1`
- Password: `mentor123`

**Mentee Account:**
- Username: `mentee1`
- Password: `mentee123`

**Admin Account:**
- Username: `admin`
- Password: `admin123`

---

## 📋 Daily Workflow Test

### Test as Mentee (mentee1)

1. **Login** at http://127.0.0.1:8000/accounts/login/

2. **Create Morning Todo List**
   - Click "Create Todo" in navigation
   - Add a few tasks with priorities
   - Click "Submit Todo List"

3. **View Today's Todo**
   - Click "Dashboard" or navigate to "Today's Todo"

4. **Submit Evening Report**
   - Click "Submit Report" in navigation
   - Rate your mood (1-5)
   - Fill in achievements, challenges, learnings
   - Add tomorrow's goals
   - Click "Submit Report"

5. **Send Message to Mentor**
   - Click "Messages" in navigation
   - Click your mentor's name
   - Compose and send a message

### Test as Mentor (mentor1)

1. **Login** at http://127.0.0.1:8000/accounts/login/

2. **View Dashboard**
   - See all your mentees
   - Navigate to their todos and reports

3. **Review Mentee Todo**
   - Click "Mentee Todos" in navigation
   - Click on a todo list to view details
   - Add mentor notes
   - Click "Save Notes"

4. **Review Mentee Report**
   - Click "Mentee Reports" in navigation
   - Click on a report to view details
   - Provide feedback in the text area
   - Click "Save Feedback"

5. **Send Message to Mentee**
   - Click "Messages" in navigation
   - Click on a mentee's name
   - Compose and send a message

### Test as Admin (admin)

1. **Login** at http://127.0.0.1:8000/admin/

2. **Manage Users**
   - Click "User Profiles"
   - View all users and their roles
   - Add new users
   - Assign mentees to mentors

3. **View Notifications**
   - Check "Notifications" to see sent emails
   - Verify notification delivery

---

## ✅ Test Notifications Manually

### Test Morning Reminder
Open a new terminal:
```bash
cd C:\Users\User2\Desktop\claribel
python -c "from notifications.cron import send_morning_reminders; send_morning_reminders()"
```

### Test Evening Reminder
```bash
python -c "from notifications.cron import send_evening_reminders; send_evening_reminders()"
```

**Note**: For actual email delivery, configure SMTP settings in `settings.py`

---

## 🎯 Key Features to Try

| Feature | URL | Description |
|---------|-----|-------------|
| Register | `/accounts/register/` | Create new user account |
| Login | `/accounts/login/` | User login |
| Profile | `/accounts/profile/` | View user profile |
| Mentor Dashboard | `/accounts/mentor/dashboard/` | Mentor overview |
| Mentee Dashboard | `/accounts/mentee/dashboard/` | Mentee overview |
| Create Todo | `/todo/create/` | Create daily todo list |
| Today's Todo | `/todo/today/` | View today's todo list |
| Mentee Todos | `/todo/mentor/todos/` | Mentor view mentee todos |
| Submit Report | `/reports/create/` | Submit daily report |
| Today's Report | `/reports/today/` | View today's report |
| Mentee Reports | `/reports/mentor/reports/` | Mentor view mentee reports |
| Messages | `/notifications/inbox/` | View messages |
| Admin Panel | `/admin/` | Django admin interface |

---

## 🔧 Enable Email Notifications

Edit `mentorship_platform/settings.py`:

```python
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Generate in Gmail settings
```

Restart server after changes.

---

## 📱 Add New Users

### Via Admin Panel (Recommended)
1. Login as admin
2. Go to `/admin/`
3. Add User
4. Set role in User Profiles
5. Assign mentor (if mentee)

### Via Script
Edit `create_superuser.py` and run:
```bash
python create_superuser.py
```

---

## 🐛 Troubleshooting

**Server won't start?**
```bash
# Check if port 8000 is in use
# Try different port:
python manage.py runserver 8080
```

**Templates not loading?**
```bash
python manage.py collectstatic
```

**Database issues?**
```bash
# Reset database (WARNING: Deletes all data)
rm db.sqlite3
python manage.py migrate
python create_superuser.py
```

---

## 📚 Next Steps

1. ✅ Configure email settings for notifications
2. ✅ Add more test users via admin
3. ✅ Test the full mentor-mentee workflow
4. ✅ Set up cron jobs for automated reminders (Linux/Mac)
5. ✅ Optional: Configure Twilio for SMS notifications

---

**Need Help?** Check the full README.md for detailed documentation.
