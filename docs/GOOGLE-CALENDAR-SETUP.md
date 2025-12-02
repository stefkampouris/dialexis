# Google Calendar Integration Setup Guide

## Overview

Your dental secretary agent can now check doctor availability and suggest appointment slots using Google Calendar integration.

## Prerequisites

1. A Google Cloud Project
2. Google Calendar API enabled
3. Service Account credentials

---

## Setup Steps

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your Project ID

### 2. Enable Google Calendar API

1. In the Cloud Console, go to **APIs & Services** > **Library**
2. Search for "Google Calendar API"
3. Click **Enable**

### 3. Create a Service Account

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **Service Account**
3. Fill in details:
   - Service account name: `dental-secretary-bot`
   - Service account ID: (auto-generated)
   - Description: "Service account for dental clinic appointment bot"
4. Click **Create and Continue**
5. Grant role: **Project** > **Viewer** (or create custom role with Calendar permissions)
6. Click **Continue** > **Done**

### 4. Create and Download Service Account Key

1. In the **Credentials** page, find your service account
2. Click on the service account email
3. Go to the **Keys** tab
4. Click **Add Key** > **Create new key**
5. Choose **JSON** format
6. Click **Create**
7. The key file will download automatically
8. **Important:** Keep this file secure!

### 5. Share Calendar with Service Account

1. Open [Google Calendar](https://calendar.google.com/)
2. Find the calendar you want to use (or create a new "Dental Clinic" calendar)
3. Click the **⋮** (three dots) next to the calendar name
4. Select **Settings and sharing**
5. Scroll to **Share with specific people**
6. Click **Add people**
7. Enter the service account email (format: `dental-secretary-bot@your-project-id.iam.gserviceaccount.com`)
8. Set permissions to **See all event details** (or **Make changes to events** if you want to create/modify appointments)
9. Click **Send**

### 6. Get Your Calendar ID

1. In Calendar Settings, scroll to **Integrate calendar**
2. Copy the **Calendar ID** (usually looks like `your-email@gmail.com` or `random-id@group.calendar.google.com`)
3. Save this for the next step

---

## Configuration

### 1. Move the Service Account Key File

```powershell
# Create a credentials directory
New-Item -ItemType Directory -Force -Path "C:\Users\steve\Desktop\pipecat-demo\credentials"

# Move your downloaded key file there
Move-Item "C:\Users\steve\Downloads\your-project-id-xxxxx.json" "C:\Users\steve\Desktop\pipecat-demo\credentials\google-calendar-key.json"
```

### 2. Update Your `.env` File

Add these lines to your `.env`:

```env
# Google Calendar Configuration
GOOGLE_CALENDAR_CREDENTIALS_PATH=credentials/google-calendar-key.json
GOOGLE_CALENDAR_ID=your-calendar-id@gmail.com
```

Replace `your-calendar-id@gmail.com` with the Calendar ID you copied earlier.

### 3. Install Required Python Packages

```powershell
# In your project directory
uv add google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

---

## Testing the Integration

### 1. Start Your Bot

```powershell
uv run bot.py
```

### 2. Test Calendar Functions

Try these voice commands with your bot:

**Check availability:**
- "Πότε έχει διαθέσιμο ο γιατρός;" (When is the doctor available?)
- "Θέλω ραντεβού αύριο" (I want an appointment tomorrow)
- "Έχετε διαθέσιμο την Τρίτη το πρωί;" (Do you have availability Tuesday morning?)

**Create appointment:**
- "Θέλω να κλείσω ραντεβού" (I want to book an appointment)
- "Μπορώ να κάνω ραντεβού για καθαρισμό;" (Can I make an appointment for a cleaning?)

**Update/reschedule appointment:**
- "Θέλω να αλλάξω το ραντεβού μου" (I want to change my appointment)
- "Μπορώ να μετακινήσω το ραντεβού;" (Can I move my appointment?)

**Cancel appointment:**
- "Θέλω να ακυρώσω το ραντεβού μου" (I want to cancel my appointment)

**Get next available slots:**
- "Ποιο είναι το πιο γρήγορο ραντεβού;" (What's the earliest appointment?)
- "Πες μου τα επόμενα 5 διαθέσιμα ραντεβού" (Tell me the next 5 available appointments)

### 3. Verify Calendar Access

You should see logs like:
```
✓ Google Calendar service initialized
✓ Calendar functions registered with LLM
📅 Checking availability: 2025-11-16 to N/A
✓ Found 23 available slots
```

---

## Troubleshooting

### Error: "Calendar service not initialized"

**Cause:** Service account key file not found or invalid path.

**Solution:**
1. Check the file exists: `Test-Path "credentials/google-calendar-key.json"`
2. Verify the path in `.env` is correct
3. Make sure the JSON file is valid

### Error: "notFound" or "Access Denied"

**Cause:** Service account doesn't have access to the calendar.

**Solution:**
1. Go back to Calendar Settings
2. Verify the service account email is in the "Share with specific people" list
3. Make sure it has at least "See all event details" permission
4. Wait a few minutes for permissions to propagate

### No Available Slots Returned

**Cause:** Either the calendar is fully booked, or the date range is outside working hours.

**Solution:**
1. Check your calendar has some free time
2. The bot only checks Monday-Friday, 9 AM - 6 PM by default
3. Adjust working hours in `src/calendar/google_calendar.py` if needed

### Calendar Shows Wrong Timezone

**Cause:** Timezone mismatch.

**Solution:**
1. The default timezone is "Europe/Athens" (Greece)
2. To change it, edit `src/calendar/google_calendar.py`:
   ```python
   timezone: str = "Europe/Athens"  # Change this
   ```

---

## Customization

### Change Working Hours

Edit `src/calendar/google_calendar.py`:

```python
# Line ~160
WORK_START = 9   # Change start hour (9 AM)
WORK_END = 18    # Change end hour (6 PM)
```

### Change Appointment Slot Duration

Edit `src/calendar/google_calendar.py`:

```python
# Line ~150
slot_duration_minutes: int = 30  # Change from 30 to 15, 45, 60, etc.
```

### Include Weekends

Edit `src/calendar/google_calendar.py`:

```python
# Line ~172 - Comment out or remove this section:
# if current_day.weekday() >= 5:  # Saturday = 5, Sunday = 6
#     current_day += timedelta(days=1)
#     continue
```

---

## Security Best Practices

1. **Never commit the service account key file to git**
   - Already added to `.gitignore`
   - Keep it in `credentials/` folder

2. **Restrict Service Account Permissions**
   - Use principle of least privilege
   - Required scopes:
     - `https://www.googleapis.com/auth/calendar` (full calendar access)
     - `https://www.googleapis.com/auth/calendar.events` (event management)

3. **Rotate Keys Regularly**
   - Create new keys every 90 days
   - Delete old keys from Google Cloud Console

4. **Use Different Calendars for Testing**
   - Don't use your personal calendar
   - Create a dedicated "Dental Clinic Test" calendar

---

## Features Available

✅ **Check Availability** - Query free/busy time slots
✅ **Create Appointments** - Book new appointments with patient details
✅ **Update/Reschedule** - Modify existing appointment times
✅ **Cancel Appointments** - Delete appointments from calendar
✅ **Smart Filtering** - Filter by morning/afternoon/evening preferences
✅ **Greek Language** - All responses in natural Greek

---

## Next Steps

- Integrate with **patient database** for automatic identification
- Add **email/SMS confirmations** when appointments are booked
- Implement **appointment reminders** (24h before)
- Add **recurring appointments** support
- Integrate **payment processing** for deposits

---

## Support

If you encounter issues:

1. Check the logs in your terminal for specific error messages
2. Verify all environment variables are set correctly
3. Test the service account key manually:
   ```python
   from google.oauth2.service_account import Credentials
   creds = Credentials.from_service_account_file(
       'credentials/google-calendar-key.json',
       scopes=['https://www.googleapis.com/auth/calendar.readonly']
   )
   print("✓ Key is valid")
   ```

Good luck! 🚀
