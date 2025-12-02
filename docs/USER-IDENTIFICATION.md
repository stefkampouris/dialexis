# User Identification System - Implementation Complete ✓

## Overview

Section 2.1 of the PRD (User Identification & Authentication) has been successfully implemented. The system can now:

- ✅ Identify users by phone number (Greek format)
- ✅ Store user profiles in Upstash Redis
- ✅ Register new users
- ✅ Update user preferences
- ✅ Generate user context for LLM conversations
- ✅ Track conversation history

## Architecture

```
src/
├── config.py                    # Configuration management
├── database/
│   ├── models.py               # Pydantic data models
│   ├── redis_client.py         # Redis operations
│   └── __init__.py
├── users/
│   ├── identification.py       # User identification service
│   └── __init__.py
└── utils/
    ├── phone_numbers.py        # Phone validation & normalization
    └── __init__.py
```

## Setup Instructions

### 1. Create Upstash Redis Account

1. Go to [https://console.upstash.com](https://console.upstash.com)
2. Sign up or log in
3. Click "Create Database"
4. Choose:
   - Name: `niniko-prod` (or your preferred name)
   - Region: Select closest to your users (Europe recommended for Greece)
   - Type: Regional
5. Click "Create"

### 2. Get Redis Credentials

After creating the database:

1. Go to your database dashboard
2. Scroll to "REST API" section
3. Copy:
   - `UPSTASH_REDIS_REST_URL`
   - `UPSTASH_REDIS_REST_TOKEN`

### 3. Update .env File

Add to your `.env` file:

```bash
# Upstash Redis Configuration
UPSTASH_REDIS_REST_URL=https://your-database-url.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_token_here

# Optional: For testing user identification
TEST_PHONE_NUMBER=+306912345678
```

### 4. Install Dependencies

Already installed! The following packages were added:
- `upstash-redis>=0.15.0` - Upstash Redis Python client
- `python-dotenv>=1.0.0` - Environment variable loading
- `pydantic>=2.5.0` - Data validation and models

## Redis Schema

### Key Structure

All keys follow the pattern: `niniko:{resource}:{identifier}:{sub_resource}`

```
niniko:user:{user_id}              # User profile (hash)
niniko:phone:{phone_number}        # Phone → user_id mapping (string)
niniko:users                       # Set of all user IDs
niniko:call:{user_id}:{call_id}    # Call record (hash)
niniko:user:{user_id}:calls        # Sorted set of call IDs (by timestamp)
```

### Data Models

#### UserProfile
```python
{
    "user_id": "uuid-v4",
    "phone_number": "+30xxxxxxxxxx",
    "name": "Μαρία Παπαδοπούλου",
    "preferred_name": "κυρία Μαρία",
    "registration_date": "2025-11-03T10:00:00Z",
    "status": "active",
    "timezone": "Europe/Athens",
    "interests": ["εκκλησία", "χειροτεχνία", "μουσική"],
    "favorite_topics": ["εγγόνια", "κήπος", "μαγειρική"],
    "avoid_topics": [],
    "preferred_greeting": "Καλημέρα κυρία Μαρία"
}
```

#### CallRecord
```python
{
    "call_id": "uuid-v4",
    "user_id": "uuid",
    "timestamp": "2025-11-03T09:00:00Z",
    "duration_seconds": 180,
    "summary": "User mentioned feeling tired. Discussed weather.",
    "mood": "neutral",
    "topics": ["weather", "family", "health"],
    "emergency_detected": false
}
```

## Usage Examples

### Testing the System

Run the test suite:

```bash
uv run python test_user_identification.py
```

This will test:
1. Phone number normalization
2. Redis connection
3. User registration
4. User retrieval
5. Preferences update
6. Context generation
7. List all users

### In Bot Code

The bot has been updated to:

1. **Initialize Redis on startup:**
```python
await redis_client.initialize()
```

2. **Identify user on connection:**
```python
user_profile, is_new_user = await user_identification_service.identify_user(phone_number)
```

3. **Generate context for LLM:**
```python
user_context = await user_identification_service.generate_user_context(user_profile)
```

4. **Personalized greeting:**
```python
messages.append({
    "role": "system",
    "content": f"ΠΛΗΡΟΦΟΡΙΕΣ ΧΡΗΣΤΗ:\n{user_context}\n\nGreet {user_profile.preferred_name} warmly."
})
```

### Programmatic Usage

```python
from src.database.redis_client import redis_client
from src.users.identification import user_identification_service

# Initialize
await redis_client.initialize()

# Identify user
user, is_new = await user_identification_service.identify_user("+306912345678")

if user:
    print(f"Welcome back, {user.preferred_name}!")
else:
    # Register new user
    user = await user_identification_service.register_new_user(
        phone_number="+306912345678",
        name="Μαρία Παπαδοπούλου",
        preferred_name="κυρία Μαρία"
    )

# Update preferences
await user_identification_service.update_user_preferences(
    user_id=user.user_id,
    interests=["εκκλησία", "μουσική"],
    favorite_topics=["εγγόνια"]
)

# Get user by ID
user = await user_identification_service.get_user_by_id(user_id)
```

## Phone Number Formats

The system handles various Greek phone number formats:

| Input Format | Normalized Output | Type |
|--------------|------------------|------|
| `6912345678` | `+306912345678` | Mobile |
| `0030 691 234 5678` | `+306912345678` | Mobile |
| `+30 691-234-5678` | `+306912345678` | Mobile |
| `06912345678` | `+306912345678` | Mobile |
| `2103456789` | `+302103456789` | Landline |
| `+30 210 345 6789` | `+302103456789` | Landline |

## Features Implemented

### ✅ Core Features

- [x] Phone number normalization (Greek format)
- [x] Phone number validation
- [x] User identification by phone
- [x] User registration
- [x] User profile storage
- [x] User preferences management
- [x] Conversation context generation
- [x] Call history tracking

### ✅ Technical Features

- [x] Async Redis operations
- [x] Pydantic data models
- [x] Error handling and logging
- [x] Configuration management
- [x] Phone format display utilities
- [x] Integration with bot.py

## API Reference

### RedisClient

```python
# Initialize
await redis_client.initialize()

# User operations
user = await redis_client.get_user_by_phone(phone_number)
user = await redis_client.get_user_profile(user_id)
success = await redis_client.create_user(user_profile)
success = await redis_client.update_user(user_profile)

# Call history
success = await redis_client.save_call_record(call_record)
calls = await redis_client.get_recent_calls(user_id, limit=10)

# Stats
total = await redis_client.get_total_users()
user_ids = await redis_client.get_all_user_ids()
```

### UserIdentificationService

```python
# Identify user
user, is_new = await user_identification_service.identify_user(phone_number)

# Register
user = await user_identification_service.register_new_user(
    phone_number, name, preferred_name
)

# Get by ID
user = await user_identification_service.get_user_by_id(user_id)

# Update preferences
success = await user_identification_service.update_user_preferences(
    user_id, interests, favorite_topics, avoid_topics, preferred_greeting
)

# Generate context
context = await user_identification_service.generate_user_context(user_profile)
```

### Phone Utilities

```python
from src.utils.phone_numbers import *

# Normalize
normalized = normalize_phone_number("6912345678")  # Returns "+306912345678"

# Validate
is_valid = validate_greek_phone_number("+306912345678")

# Format for display
display = format_phone_display("+306912345678")  # Returns "+30 691 234 5678"

# Check type
is_mobile = is_mobile_number("+306912345678")
is_landline = is_landline_number("+302103456789")
```

## Testing

### Quick Test

```bash
# Run full test suite
uv run python test_user_identification.py
```

### Manual Testing

```bash
# Test phone normalization only
uv run python -c "from src.utils.phone_numbers import test_phone_normalization; test_phone_normalization()"
```

### Integration Test with Bot

1. Set `TEST_PHONE_NUMBER` in `.env`:
   ```
   TEST_PHONE_NUMBER=+306912345678
   ```

2. Run bot:
   ```bash
   uv run bot.py
   ```

3. Connect via browser - bot will identify user and personalize greeting

## Next Steps

Now that User Identification (2.1) is complete, you can proceed with:

1. **Section 2.2: Daily Communication**
   - Scheduled phone calls
   - Call history tracking
   - Conversation memory

2. **Section 2.3: Health & Medication Reminders**
   - Medication schedules
   - Reminder system
   - Adherence tracking

3. **Twilio Integration**
   - Connect real phone numbers
   - Inbound/outbound calls
   - Caller ID capture

## Troubleshooting

### Redis Connection Issues

```
✗ Failed to initialize Redis: HTTPError...
```

**Solution:**
- Verify `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN` in `.env`
- Check Upstash dashboard - database must be active
- Test connection: `curl $UPSTASH_REDIS_REST_URL/ping`

### Import Errors

```
ModuleNotFoundError: No module named 'upstash_redis'
```

**Solution:**
```bash
uv sync
```

### Phone Number Not Normalized

```
✗ Invalid phone number format: ...
```

**Solution:**
- Ensure Greek format: starts with 2 (landline) or 6 (mobile)
- Must be 10 digits after country code
- Valid examples: `+306912345678`, `+302103456789`

## Support

For issues or questions:
1. Check the PRD: `docs/PRD-NINIKO.md`
2. Check implementation guide: `docs/IMPLEMENTATION.md`
3. Run test suite: `python test_user_identification.py`

---

**Status:** ✅ Section 2.1 Complete  
**Next:** Section 2.2 (Daily Communication & Call Scheduling)
