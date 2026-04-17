# mNotify SMS Integration - Setup Guide

## Implementation Complete

The SMS notification system using mNotify has been successfully implemented for MentorFlow. This guide will help you configure and test the system.

---

## What Was Implemented

### 1. New mNotify SMS Provider Module
**File:** `notifications/sms_providers.py`
- Created `MNotifySMSProvider` class
- Implements mNotify API integration
- Includes error handling and validation
- Supports SMS sending and balance checking

### 2. Updated Configuration
**File:** `mentorship_platform/settings.py`
- Added `MNOTIFY_API_KEY` configuration
- Added `MNOTIFY_SENDER_ID` configuration (default: "MentorFlow")
- Kept Twilio settings for reference (marked as legacy)

### 3. Updated Notification Service
**File:** `notifications/services.py`
- Replaced Twilio with mNotify SMS provider
- Enhanced error handling for SMS notifications
- Validates user phone number and SMS preferences

### 4. SMS Notifications Enabled For:
- **Todo Submissions** (`todo/views.py`): Mentors receive SMS when mentees submit todo lists
- **New Messages** (`notifications/views.py`): Users receive SMS for new messages
- **Morning Reminders** (`notifications/cron.py`): SMS reminder to create daily todo list
- **Evening Reminders** (`notifications/cron.py`): SMS reminder to submit daily report

---

## Configuration Steps

### Step 1: Get mNotify API Credentials

1. **Sign up/Login** to mNotify: https://apps.mnotify.net
2. **Get your API Key** from: https://apps.mnotify.net/api/api
3. **Choose a Sender ID** (max 11 characters, e.g., "MentorFlow")

### Step 2: Update .env File

Add the following lines to your `.env` file:

```env
MNOTIFY_API_KEY=your_actual_api_key_here
MNOTIFY_SENDER_ID=MentorFlow
```

**Important:**
- Replace `your_actual_api_key_here` with your actual mNotify API key
- The Sender ID should be max 11 characters
- Keep the Sender ID recognizable for your users

### Step 3: Restart Django Server

After updating the `.env` file, restart your Django server:

```bash
# If using runserver
python manage.py runserver

# If using gunicorn (production)
sudo systemctl restart gunicorn
```

---

## Testing the Implementation

### Test 1: Test mNotify Connection (Python Shell)

Open Django shell and test the SMS provider:

```bash
python manage.py shell
```

```python
from notifications.sms_providers import MNotifySMSProvider

# Create provider instance
provider = MNotifySMSProvider()

# Test sending SMS (use your own phone number)
result = provider.send_sms(
    recipient_phone='0201234567',  # Replace with your phone number
    message='Test message from MentorFlow!'
)

print(result)
# Should show: {'success': True, 'message': 'SMS sent successfully', ...}
```

### Test 2: Check SMS Balance

```python
# In Django shell
balance = provider.check_balance()
print(balance)
# Should show: {'success': True, 'balance': {...}}
```

### Test 3: Test Todo Submission Notification

1. Create a test mentee account with phone number
2. Create a test mentor account with phone number and SMS enabled
3. As mentee, submit a todo list
4. Check that mentor receives SMS notification

### Test 4: Test Message Notification

1. Enable SMS notifications for a user
2. Send a message to that user
3. Verify SMS is received

---

## Verification Checklist

- [ ] mNotify API key added to `.env` file
- [ ] Sender ID configured (max 11 characters)
- [ ] Django server restarted after configuration
- [ ] Test SMS sent successfully via shell
- [ ] SMS balance checked and sufficient
- [ ] User profiles have phone numbers in correct format
- [ ] Users have `sms_notifications_enabled = True` in profile
- [ ] Todo submission triggers SMS to mentor
- [ ] New messages trigger SMS notifications
- [ ] Cron jobs configured and running
- [ ] Morning/evening reminders send SMS

---

## Phone Number Format

mNotify accepts Ghanaian phone numbers in these formats:
- `02XXXXXXXXX` (e.g., 0201234567)
- `+233XXXXXXXXX` (e.g., +233201234567)

**Note:** When users register, ensure they enter phone numbers in the correct format.

---

## Database Verification

Check SMS notifications in Django Admin:

1. Go to Django Admin: `/admin/`
2. Navigate to **Notifications** → **Notifications**
3. Filter by `notification_type = 'sms'`
4. Verify:
   - `sent_successfully = True` for successful sends
   - Check `error_message` field for any failures
   - Verify `trigger_event` values

---

## Monitoring & Maintenance

### Check SMS Delivery Status

Log into mNotify dashboard: https://apps.mnotify.net
- View sent SMS history
- Check delivery reports
- Monitor account balance

### Monitor Balance Regularly

```python
# Add this to your admin or monitoring script
from notifications.sms_providers import MNotifySMSProvider

provider = MNotifySMSProvider()
balance_info = provider.check_balance()

if not balance_info['success']:
    print(f"Error checking balance: {balance_info['message']}")
else:
    print(f"Balance: {balance_info['balance']}")
```

### Error Handling

All SMS errors are logged in the `Notification` model:
- Check `error_message` field for failure reasons
- Common errors:
  - "SMS not enabled or no phone number provided" - User needs to enable SMS
  - "mNotify API key is not configured" - Add API key to `.env`
  - "Network error" - Check internet connection
  - "Failed to send SMS" - Check mNotify account balance

---

## SMS Best Practices

1. **Keep messages under 160 characters** (single SMS segment)
   - Longer messages are split and cost more

2. **Use clear, concise text**
   - SMS is limited, get to the point quickly

3. **Include app name in Sender ID**
   - Use "MentorFlow" or your organization name

4. **Handle rate limiting**
   - mNotify may have limits on messages per minute/day

5. **Log all SMS attempts**
   - All SMS are logged in the Notification model for audit

---

## Troubleshooting

### Issue: SMS not sending

**Check:**
1. API key is correctly set in `.env`
2. Sender ID is max 11 characters
3. User has phone number in profile
4. User has `sms_notifications_enabled = True`
5. mNotify account has sufficient balance
6. Phone number format is correct (02XXXXXXXXX or +233XXXXXXXXX)

### Issue: Users not receiving SMS

**Check:**
1. SMS appears in Django Admin with `sent_successfully = True`
2. Check mNotify dashboard for delivery status
3. Verify phone number is correct and active
4. Check if phone carrier blocks automated SMS

### Issue: API errors

**Check:**
1. API key is valid and active
2. Internet connection is stable
3. mNotify service is operational
4. Check mNotify status page or contact support

---

## Cost Considerations

mNotify charges per SMS:
- Check current pricing at: https://www.mnotify.com/
- Ghana rates are typically affordable
- Monitor balance regularly to avoid service interruption

**To minimize costs:**
- Keep messages under 160 characters
- Only enable SMS for users who need it
- Consider sending SMS only for high-priority notifications

---

## Future Enhancements

Optional improvements you can add:

1. **SMS Template System**: Pre-defined message templates for different events
2. **SMS Queueing**: Use Celery for async SMS sending to avoid blocking requests
3. **Multiple Providers**: Add fallback to other SMS providers
4. **Delivery Webhooks**: Handle delivery status callbacks from mNotify
5. **SMS Scheduling**: Schedule reminders for specific times
6. **Bulk SMS**: Send batch notifications more efficiently

---

## mNotify Resources

- **Website**: https://www.mnotify.com/
- **Developer Portal**: https://mnotifybms.com/developer/
- **API Documentation**: https://readthedocs.mnotify.com/
- **API Key Location**: https://apps.mnotify.net/api/api
- **Dashboard**: https://apps.mnotify.net

---

## Support

For issues with:
- **MentorFlow integration**: Check Django logs and Notification model
- **mNotify API**: Contact mNotify support via their dashboard
- **Account/Billing**: Visit mNotify dashboard for account management

---

## Implementation Summary

| Component | Status | Notes |
|-----------|--------|-------|
| mNotify SMS Provider | ✅ Complete | `notifications/sms_providers.py` |
| Configuration | ✅ Complete | Settings updated, needs .env values |
| Notification Service | ✅ Complete | Updated to use mNotify |
| Todo Notifications | ✅ Complete | SMS + Email sent to mentors |
| Message Notifications | ✅ Complete | SMS sent for new messages |
| Morning Reminders | ✅ Complete | SMS + Email sent at 8 AM |
| Evening Reminders | ✅ Complete | SMS + Email sent at 6 PM |
| Error Handling | ✅ Complete | All errors logged in Notification model |

---

**Next Steps:**
1. Add mNotify API credentials to `.env` file
2. Test SMS sending via Django shell
3. Enable SMS notifications for test users
4. Verify end-to-end workflow
5. Monitor mNotify dashboard for delivery reports
