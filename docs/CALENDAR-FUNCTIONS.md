# Calendar Function Calling - Quick Reference

## What It Does

Your dental secretary agent can now:

✅ Check doctor availability in real-time  
✅ Find next available appointment slots  
✅ Filter by time preference (morning/afternoon/evening)  
✅ Handle Greek date requests ("αύριο", "τη Δευτέρα", etc.)

---

## How It Works

The agent uses **function calling** to interact with Google Calendar:

1. **Patient asks** for an appointment
2. **LLM decides** it needs calendar data
3. **Function is called** to check Google Calendar
4. **Results returned** to LLM
5. **LLM responds** in natural Greek with available slots

---

## Example Conversations

### Example 1: Check Availability

**Patient:** "Θέλω ραντεβού αύριο το πρωί"  
**Agent:** *[Calls `check_doctor_availability` with start_date="tomorrow", preferred_time="morning"]*  
**Agent:** "Αύριο το πρωί έχω διαθέσιμα τα εξής ραντεβού: Τρίτη 16/11/2025 στις 09:00, στις 09:30, ή στις 10:00. Ποιο σας βολεύει;"

### Example 2: Next Available

**Patient:** "Πότε έχει ελεύθερο ο γιατρός;"  
**Agent:** *[Calls `get_next_available_slots` with count=5]*  
**Agent:** "Το πιο γρήγορο διαθέσιμο ραντεβού είναι Δευτέρα 18/11 στις 14:00. Θέλετε να το κλείσουμε;"

### Example 3: Specific Day

**Patient:** "Έχετε κάτι την Πέμπτη;"  
**Agent:** *[Calls `check_doctor_availability` with start_date="next Thursday"]*  
**Agent:** "Ναι, την Πέμπτη έχω διαθέσιμα: 14:00, 15:00, και 16:30. Ποια ώρα σας βολεύει καλύτερα;"

---

## Functions Available

### 1. `check_doctor_availability`

**Purpose:** Check calendar availability for a date range

**Parameters:**
- `start_date` (required): ISO date string (e.g., "2025-11-16")
- `end_date` (optional): ISO date string (defaults to +7 days)
- `preferred_time` (optional): "morning" | "afternoon" | "evening" | "any"

**Returns:**
```json
{
  "success": true,
  "has_availability": true,
  "total_slots": 23,
  "available_slots": [
    {
      "readable": "Δευτέρα 18/11/2025 στις 09:00",
      "start": "2025-11-18T09:00:00",
      "end": "2025-11-18T09:30:00",
      "duration": 30
    }
  ]
}
```

### 2. `get_next_available_slots`

**Purpose:** Get the next N available slots from now

**Parameters:**
- `from_date` (optional): ISO date string (defaults to now)
- `count` (optional): Number of slots to return (default: 5, max: 10)

**Returns:**
```json
{
  "success": true,
  "next_available": {
    "readable": "Τρίτη 19/11/2025 στις 14:00",
    "start": "2025-11-19T14:00:00"
  },
  "all_slots": [...]
}
```

---

## Default Settings

### Working Hours
- **Monday - Friday:** 9:00 AM - 6:00 PM
- **Weekends:** Closed
- **Slot Duration:** 30 minutes

### Timezone
- **Default:** `Europe/Athens` (EET/EEST for Greece)

### Appointment Types
Currently checks overall availability. Can be extended to filter by:
- Type of service (cleaning, filling, consultation, etc.)
- Specific dentist (if multiple doctors)
- Emergency vs routine

---

## Setup Required

Before the calendar functions work, you need:

1. ✅ Google Cloud Project with Calendar API enabled
2. ✅ Service account credentials JSON file
3. ✅ Calendar shared with service account
4. ✅ Environment variables set in `.env`

**See full setup guide:** [`docs/GOOGLE-CALENDAR-SETUP.md`](./GOOGLE-CALENDAR-SETUP.md)

---

## Code Structure

```
src/calendar/
├── google_calendar.py       # Google Calendar API integration
├── calendar_functions.py    # Function calling handlers for LLM
└── __init__.py

bot.py                       # Main bot with calendar tools registered
```

### Key Components

**`GoogleCalendarService`** (`google_calendar.py`)
- Handles Google Calendar API calls
- Calculates free/busy periods
- Manages authentication

**`create_calendar_tools()`** (`calendar_functions.py`)
- Defines function schemas for the LLM
- Specifies parameters and descriptions

**`register_calendar_functions()`** (`calendar_functions.py`)
- Registers function handlers with LLM service
- Called during bot initialization

---

## Extending Functionality

### Add Appointment Creation

```python
# In calendar_functions.py

create_appointment_function = FunctionSchema(
    name="create_appointment",
    description="Create a new appointment in the calendar",
    properties={
        "patient_name": {"type": "string"},
        "start_time": {"type": "string"},
        "duration_minutes": {"type": "integer", "default": 30},
        "reason": {"type": "string"}
    },
    required=["patient_name", "start_time"]
)
```

### Add Specific Doctor Selection

```python
# If you have multiple doctors
check_availability_function = FunctionSchema(
    name="check_doctor_availability",
    properties={
        "doctor_id": {
            "type": "string",
            "description": "Doctor ID to check (dr_smith, dr_jones, etc.)",
            "enum": ["dr_smith", "dr_jones", "any"]
        },
        # ... other properties
    }
)
```

### Add Appointment Types

```python
# Filter by service type
properties={
    "service_type": {
        "type": "string",
        "description": "Type of dental service",
        "enum": ["cleaning", "checkup", "filling", "root_canal", "emergency"]
    }
}
```

---

## Troubleshooting

### Function Not Being Called

**Symptoms:** Agent responds generically without checking calendar

**Causes:**
1. Function not registered properly
2. LLM context missing tools
3. Function description not clear enough

**Solution:**
```python
# Check logs for:
"✓ Calendar functions registered with LLM"
"✓ Calendar functions registered"

# Make function descriptions more explicit
description="ALWAYS use this function when a patient asks about appointments or availability"
```

### Wrong Date Interpretation

**Symptoms:** Agent checks wrong dates

**Solution:**
- Add more examples to system prompt:
  ```yaml
  - "αύριο" = tomorrow
  - "τη Δευτέρα" = next Monday
  - "σε δυο μέρες" = in 2 days
  ```
- Use `gpt-4o` instead of `gpt-4o-mini` for better date parsing

### No Slots Returned

**Symptoms:** Always says "no availability"

**Causes:**
1. Calendar is actually fully booked
2. Looking outside working hours
3. Date range too narrow

**Solution:**
1. Check actual Google Calendar
2. Extend date range: `end_date = start_date + 14 days`
3. Adjust working hours in `google_calendar.py`

---

## Performance Impact

**TTFB Impact:**
- Function call adds ~200-800ms to response time
- First call: ~800ms (cold start)
- Subsequent calls: ~200-400ms (cached)

**Optimization:**
- Set `cancel_on_interruption=False` for calendar checks
- Cache recent availability queries (future enhancement)
- Use `gpt-4o-mini` for faster function calling

---

## Security Notes

🔒 **Service Account Key**
- Never commit to git (in `.gitignore`)
- Store in `credentials/` folder
- Rotate every 90 days

🔒 **Calendar Permissions**
- Grant minimum required permissions
- Use read-only access unless creating appointments
- Separate calendar for production vs testing

🔒 **API Rate Limits**
- Google Calendar API: 1M requests/day free
- Monitor usage in Google Cloud Console

---

## Next Steps

- [ ] Add appointment creation function
- [ ] Integrate with patient database for auto-booking
- [ ] Add email/SMS confirmation after booking
- [ ] Implement appointment modification/cancellation
- [ ] Add multi-doctor support
- [ ] Cache availability for better performance

---

Happy booking! 📅✨
