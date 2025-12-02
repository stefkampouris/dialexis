# Niniko Implementation Guide
# Using Context7 MCP for Documentation

This guide provides step-by-step implementation instructions using Context7 MCP to retrieve the latest documentation for all required services.

---

## Phase 1: Setup & Core Infrastructure

### Step 1: Upstash Redis Setup

#### 1.1 Research Upstash Redis
Use Context7 to get documentation:
```
Query: Upstash Redis Python client setup and connection
Library: /upstash/upstash-redis
```

**Key Information Needed:**
- Connection URL format
- Authentication methods
- Python client installation
- Basic CRUD operations
- Connection pooling
- Async support

#### 1.2 Create Redis Helper Module
File: `src/database/redis_client.py`

**Requirements:**
- Connection management
- Retry logic
- Error handling
- Async operations support

### Step 2: Twilio Integration

#### 2.1 Research Twilio Voice
Use Context7 to get documentation:
```
Query: Twilio Python SDK voice calls webhooks inbound outbound
Library: /twilio/twilio-python
```

**Key Information Needed:**
- Making outbound calls
- Handling inbound call webhooks
- TwiML response generation
- Call recording options
- SMS sending
- Phone number management

#### 2.2 Create Twilio Service Module
File: `src/telephony/twilio_service.py`

**Requirements:**
- Outbound call initiation
- Webhook handlers (FastAPI endpoints)
- Call status tracking
- SMS notification service
- Error handling

### Step 3: User Identification System

#### 3.1 Research Phone Number Handling
Use Context7 to get documentation:
```
Query: phonenumbers library Python validation formatting
Library: Search for "phonenumbers" or use general docs
```

#### 3.2 Implement User Identification
File: `src/users/identification.py`

**Features:**
- Phone number validation and normalization
- User lookup by phone number
- New user registration flow
- Session management

---

## Phase 2: Call Management System

### Step 4: Pipecat Integration with Telephony

#### 4.1 Research Pipecat Transports
Use Context7 to get documentation:
```
Query: Pipecat Twilio transport integration WebRTC
Library: /pipecat-ai/pipecat
Topic: transports, telephony integration
```

**Key Information Needed:**
- Twilio transport setup
- Audio streaming configuration
- Event handlers (on_connected, on_disconnected)
- Context management
- Interruption handling

#### 4.2 Update Bot Configuration
File: `bot.py` (modify existing)

**Changes:**
- Add user identification on connection
- Load user profile from Redis
- Inject user context into LLM
- Log conversation to Redis

### Step 5: Call Scheduler

#### 5.1 Research Celery Beat
Use Context7 to get documentation:
```
Query: Celery periodic tasks scheduling Redis backend
Library: /celery/celery
Topic: beat scheduler, periodic tasks
```

**Key Information Needed:**
- Periodic task definition
- Crontab scheduling
- Redis as broker
- Task monitoring
- Error handling

#### 5.2 Implement Scheduler
File: `src/scheduler/tasks.py`

**Features:**
- Daily call scheduling per user
- Retry logic for failed calls
- Missed call detection
- Alert escalation

---

## Phase 3: Health Management Features

### Step 6: Medication Reminder System

#### 6.1 Design Medication Data Model
File: `src/health/medications.py`

**Features:**
- Add/update/delete medications
- Schedule-based reminders
- Adherence tracking
- Report generation

#### 6.2 Integrate with Call Flow
Modify: `bot.py`

**Features:**
- Check for due medications during call
- Ask confirmation questions
- Log adherence in Redis
- Send alerts to caregivers

### Step 7: Appointment Management

#### 7.1 Implement Appointment System
File: `src/health/appointments.py`

**Features:**
- CRUD operations for appointments
- Reminder scheduling
- Notification to user and caregivers

---

## Phase 4: Emergency Detection & Alerts

### Step 8: Emergency Phrase Detection

#### 8.1 Research LLM Function Calling
Use Context7 to get documentation:
```
Query: Azure OpenAI function calling tools structured output
Library: Search for Azure OpenAI or OpenAI docs
```

**Approach Options:**
1. Real-time phrase matching in transcription
2. LLM function calling with emergency tool
3. Sentiment analysis for distress

#### 8.2 Implement Emergency Detection
File: `src/safety/emergency_detector.py`

**Features:**
- Real-time phrase detection
- Context analysis
- Emergency event creation
- Alert triggering

### Step 9: Alert Notification System

#### 9.1 Implement Alert Service
File: `src/alerts/notification_service.py`

**Features:**
- SMS alerts via Twilio
- Phone call alerts
- Priority-based contact list
- Delivery confirmation
- Retry logic

---

## Phase 5: Data Models & API

### Step 10: FastAPI Backend

#### 10.1 Research FastAPI
Use Context7 to get documentation:
```
Query: FastAPI async endpoints Redis dependency injection
Library: /tiangolo/fastapi
```

**Key Information Needed:**
- Async route handlers
- Dependency injection
- Pydantic models
- WebSocket support
- CORS configuration

#### 10.2 Create API Endpoints
File: `src/api/main.py`

**Endpoints:**
```
POST   /api/users/register
GET    /api/users/{user_id}
PUT    /api/users/{user_id}
GET    /api/users/{user_id}/medications
POST   /api/users/{user_id}/medications
GET    /api/users/{user_id}/calls
GET    /api/emergencies
POST   /api/webhooks/twilio/voice
POST   /api/webhooks/twilio/status
```

---

## Implementation Checklist

### Phase 1: Core Infrastructure ✅
- [ ] Set up Upstash Redis account
- [ ] Install and configure Upstash Redis Python client
- [ ] Create Redis connection module with retry logic
- [ ] Design and implement Redis key schema
- [ ] Set up Twilio account and purchase phone number
- [ ] Install Twilio Python SDK
- [ ] Create Twilio service wrapper
- [ ] Implement phone number validation
- [ ] Create user identification module
- [ ] Test user registration flow

### Phase 2: Call Management ✅
- [ ] Update Pipecat bot with Twilio transport
- [ ] Implement user context loading from Redis
- [ ] Add conversation logging
- [ ] Create call history storage
- [ ] Set up Celery with Redis broker
- [ ] Implement call scheduling tasks
- [ ] Add missed call detection
- [ ] Test outbound call flow
- [ ] Test inbound call flow

### Phase 3: Health Features ✅
- [ ] Design medication data model
- [ ] Implement medication CRUD operations
- [ ] Create medication reminder logic
- [ ] Integrate reminders with call flow
- [ ] Design appointment data model
- [ ] Implement appointment management
- [ ] Add health metrics tracking
- [ ] Test medication adherence flow

### Phase 4: Emergency & Safety ✅
- [ ] Implement emergency phrase detection
- [ ] Create emergency event data model
- [ ] Build alert notification service
- [ ] Implement SMS alerts via Twilio
- [ ] Add phone call alerts
- [ ] Create care circle management
- [ ] Implement alert escalation
- [ ] Test emergency scenarios

### Phase 5: API & Portal ✅
- [ ] Set up FastAPI application
- [ ] Create Pydantic models for all data types
- [ ] Implement user management endpoints
- [ ] Add medication endpoints
- [ ] Add call history endpoints
- [ ] Implement Twilio webhooks
- [ ] Add authentication/authorization
- [ ] Create basic care circle web portal
- [ ] Add API documentation (Swagger)

---

## Code Structure

```
pipecat-demo/
├── bot.py                          # Main Pipecat bot (modified)
├── src/
│   ├── __init__.py
│   ├── config.py                   # Configuration management
│   ├── database/
│   │   ├── __init__.py
│   │   ├── redis_client.py         # Redis connection & helpers
│   │   └── models.py               # Data models (Pydantic)
│   ├── users/
│   │   ├── __init__.py
│   │   ├── identification.py       # User ID by phone
│   │   ├── profile.py              # User profile management
│   │   └── preferences.py          # User preferences
│   ├── telephony/
│   │   ├── __init__.py
│   │   ├── twilio_service.py       # Twilio wrapper
│   │   └── call_manager.py         # Call orchestration
│   ├── health/
│   │   ├── __init__.py
│   │   ├── medications.py          # Medication management
│   │   ├── appointments.py         # Appointment management
│   │   └── metrics.py              # Health metrics
│   ├── safety/
│   │   ├── __init__.py
│   │   ├── emergency_detector.py   # Emergency detection
│   │   └── care_circle.py          # Care circle management
│   ├── alerts/
│   │   ├── __init__.py
│   │   └── notification_service.py # Alert notifications
│   ├── scheduler/
│   │   ├── __init__.py
│   │   ├── tasks.py                # Celery tasks
│   │   └── schedules.py            # Schedule management
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app
│   │   ├── routers/
│   │   │   ├── users.py
│   │   │   ├── health.py
│   │   │   ├── calls.py
│   │   │   └── webhooks.py
│   │   └── dependencies.py         # FastAPI dependencies
│   └── utils/
│       ├── __init__.py
│       ├── phone_numbers.py        # Phone validation
│       └── logging.py              # Custom logging
├── prompts/
│   └── elder-help.yaml             # Niniko prompt (existing)
├── tests/
│   ├── test_user_identification.py
│   ├── test_medications.py
│   ├── test_emergency.py
│   └── test_api.py
├── docs/
│   ├── PRD-NINIKO.md              # This PRD
│   ├── IMPLEMENTATION.md          # This guide
│   └── API.md                     # API documentation
├── .env                           # Environment variables
├── pyproject.toml                 # Dependencies
├── celeryconfig.py                # Celery configuration
└── README-NINIKO.md              # User documentation
```

---

## Environment Setup

### Install Additional Dependencies

Update `pyproject.toml`:
```toml
dependencies = [
    # Existing
    "pipecat-ai[webrtc,silero,soniox,azure,elevenlabs,local-smart-turn-v3,runner]",
    "pipecat-ai-cli",
    "pyyaml>=6.0",
    
    # New additions
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "upstash-redis>=0.15.0",
    "twilio>=8.10.0",
    "celery>=5.3.4",
    "redis>=5.0.0",
    "phonenumbers>=8.13.0",
    "python-dotenv>=1.0.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "httpx>=0.25.0",
    "pytz>=2023.3",
]
```

Install:
```bash
uv sync
```

---

## Context7 MCP Usage Examples

### Example 1: Getting Upstash Redis Documentation
```
You: "Use Context7 to get Upstash Redis Python client documentation"

AI Response:
- Library ID: /upstash/upstash-redis
- Retrieves: Connection setup, commands, async operations
- Provides code examples
```

### Example 2: Getting Twilio Voice Documentation
```
You: "Use Context7 to get Twilio Python SDK voice call examples"

AI Response:
- Library ID: /twilio/twilio-python
- Retrieves: Make calls, handle webhooks, TwiML
- Provides working code samples
```

### Example 3: Getting Celery Documentation
```
You: "Use Context7 to get Celery periodic tasks documentation"

AI Response:
- Library ID: /celery/celery
- Retrieves: Beat scheduler, task definition
- Provides configuration examples
```

---

## Testing Strategy

### Unit Tests
```bash
pytest tests/test_user_identification.py
pytest tests/test_medications.py
pytest tests/test_emergency.py
```

### Integration Tests
```bash
pytest tests/test_api.py --integration
```

### End-to-End Tests
1. Test call flow locally with ngrok
2. Test emergency detection
3. Test medication reminder
4. Test care circle alerts

---

## Deployment

### Docker Setup
Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependencies
COPY pyproject.toml .
RUN uv sync --no-dev

# Copy application
COPY . .

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    
  celery-worker:
    build: .
    command: celery -A src.scheduler.tasks worker --loglevel=info
    env_file: .env
    
  celery-beat:
    build: .
    command: celery -A src.scheduler.tasks beat --loglevel=info
    env_file: .env
```

---

## Monitoring & Logging

### Application Metrics
- Call success rate
- Emergency response time
- Medication adherence rate
- User engagement metrics

### Infrastructure Metrics
- Redis connection pool
- Twilio API latency
- Celery queue length
- API response times

---

## Next Steps

1. **Review PRD with stakeholders**
2. **Set up development environment**
3. **Create Upstash Redis account**
4. **Create Twilio account**
5. **Begin Phase 1 implementation**
6. **Use Context7 MCP for documentation as needed**

---

**Document Version:** 1.0  
**Last Updated:** November 3, 2025  
**Status:** Ready for Implementation
