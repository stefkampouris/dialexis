# Product Requirements Document (PRD)
# Niniko - AI Voice Companion for Elderly Care

**Version:** 1.0  
**Date:** November 3, 2025  
**Status:** Draft  
**Owner:** Development Team

---

## 1. Executive Summary

### 1.1 Product Vision
Niniko is an AI-powered voice companion system designed specifically for elderly people in Greece. The system provides daily phone conversations, health reminders, emergency detection, and emotional support through natural Greek language interactions.

### 1.2 Problem Statement
Elderly individuals living alone or with limited social interaction face:
- Loneliness and social isolation
- Difficulty remembering medications and appointments
- Risk of medical emergencies without immediate help
- Need for regular check-ins and companionship
- Language barriers (need for Greek language support)

### 1.3 Solution Overview
A voice-based AI assistant that:
- Conducts scheduled daily phone calls in Greek
- Remembers user preferences, medications, and appointments
- Detects emergencies and alerts family/caregivers
- Provides companionship through natural conversation
- Integrates with existing phone systems (landline/mobile)

---

## 2. Core Features & Requirements

### 2.1 User Identification & Authentication

#### 2.1.1 Phone Number-Based Identification
**Priority:** P0 (Critical)

**Requirements:**
- System must identify users by their phone number (caller ID)
- Must support both landline and mobile numbers
- Must handle Greek phone number formats (+30 xxx xxx xxxx)
- Must verify user identity at call start

**User Flow:**
```
1. User calls Niniko or receives scheduled call
2. System captures caller phone number
3. System queries Redis DB for user profile
4. If found: Greet by name and continue
5. If not found: Initiate registration flow
```

**Data Structure (Redis):**
```json
{
  "user_id": "uuid-v4",
  "phone_number": "+30xxxxxxxxxx",
  "name": "Μαρία Παπαδοπούλου",
  "preferred_name": "κυρία Μαρία",
  "registration_date": "2025-11-03T10:00:00Z",
  "status": "active"
}
```

#### 2.1.2 Voice-Based Verification (Optional)
**Priority:** P2 (Future Enhancement)

**Requirements:**
- Optional voice biometric verification
- Store voice signature in secure storage
- Fallback to phone number if voice recognition fails

### 2.2 Daily Communication & Companionship

#### 2.2.1 Scheduled Phone Calls
**Priority:** P0 (Critical)

**Requirements:**
- System must initiate outbound calls at scheduled times
- Support multiple call times per day (morning, afternoon, evening)
- Handle missed calls with retry logic
- Track call history and duration

**Call Schedule Data Structure:**
```json
{
  "user_id": "uuid",
  "schedule": [
    {
      "time": "09:00",
      "days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
      "enabled": true,
      "type": "morning_checkin"
    },
    {
      "time": "17:00",
      "days": ["sunday"],
      "enabled": true,
      "type": "social_reminder"
    }
  ],
  "timezone": "Europe/Athens"
}
```

#### 2.2.2 Conversation Context & Memory
**Priority:** P0 (Critical)

**Requirements:**
- Remember previous conversation topics
- Track user's mood patterns over time
- Store preferences (favorite topics, hobbies, interests)
- Maintain conversation history for continuity

**Conversation Data Structure:**
```json
{
  "user_id": "uuid",
  "conversation_history": [
    {
      "call_id": "uuid",
      "timestamp": "2025-11-03T09:00:00Z",
      "duration_seconds": 180,
      "summary": "User mentioned feeling tired. Discussed weather and grandson's visit.",
      "mood": "neutral",
      "topics": ["weather", "family", "health"],
      "emergency_detected": false
    }
  ],
  "preferences": {
    "interests": ["church", "crafts", "music"],
    "favorite_topics": ["grandchildren", "garden", "cooking"],
    "avoid_topics": [],
    "preferred_greeting": "Καλημέρα κυρία Μαρία"
  }
}
```

### 2.3 Health & Medication Reminders

#### 2.3.1 Medication Management
**Priority:** P0 (Critical)

**Requirements:**
- Store medication schedules per user
- Send reminders at specified times
- Confirm medication taken during calls
- Track adherence rates
- Alert caregivers if medications missed

**Medication Data Structure:**
```json
{
  "user_id": "uuid",
  "medications": [
    {
      "medication_id": "uuid",
      "name": "Aspirin",
      "dosage": "100mg",
      "schedule": [
        {
          "time": "08:00",
          "frequency": "daily",
          "with_food": true
        }
      ],
      "start_date": "2025-01-01",
      "end_date": null,
      "active": true,
      "adherence_log": [
        {
          "date": "2025-11-03",
          "time": "08:00",
          "taken": true,
          "confirmed_at": "2025-11-03T08:15:00Z",
          "method": "call_confirmation"
        }
      ]
    }
  ]
}
```

#### 2.3.2 Appointment Reminders
**Priority:** P1 (High)

**Requirements:**
- Store medical appointments
- Remind user 1 day before and on the day
- Include doctor name, location, and time
- Offer to remind family member

**Appointment Data Structure:**
```json
{
  "user_id": "uuid",
  "appointments": [
    {
      "appointment_id": "uuid",
      "type": "medical",
      "doctor_name": "Δρ. Γεωργίου",
      "specialty": "cardiologist",
      "location": "Νοσοκομείο Αθηνών",
      "datetime": "2025-11-10T14:30:00Z",
      "duration_minutes": 30,
      "reminders_sent": [
        {
          "type": "1_day_before",
          "sent_at": "2025-11-09T09:00:00Z"
        }
      ],
      "notes": "Φέρτε τα αποτελέσματα των εξετάσεων"
    }
  ]
}
```

#### 2.3.3 Health Metrics Tracking
**Priority:** P2 (Medium)

**Requirements:**
- Remind user to measure blood pressure, glucose, etc.
- Store self-reported measurements
- Alert if measurements outside normal range
- Share data with caregivers (with consent)

**Health Data Structure:**
```json
{
  "user_id": "uuid",
  "health_metrics": {
    "blood_pressure": {
      "enabled": true,
      "frequency": "daily",
      "reminder_time": "10:00",
      "normal_range": {
        "systolic": [110, 140],
        "diastolic": [70, 90]
      },
      "measurements": [
        {
          "date": "2025-11-03",
          "systolic": 130,
          "diastolic": 85,
          "reported_at": "2025-11-03T10:15:00Z"
        }
      ]
    },
    "glucose": {
      "enabled": false
    }
  }
}
```

### 2.4 Safety & Emergency Detection

#### 2.4.1 Emergency Phrase Recognition
**Priority:** P0 (Critical)

**Requirements:**
- Detect emergency phrases in Greek during any call
- Trigger immediate alert workflow
- Log emergency event with context
- Continue reassuring user while processing

**Emergency Triggers:**
```python
EMERGENCY_PHRASES = [
    "δεν νιώθω καλά",
    "νινίκο βοήθεια",
    "έπεσα κάτω",
    "δεν μπορώ να κουνηθώ",
    "πονάω πολύ",
    "βοήθεια",
    "καλέστε γιατρό",
    "καλέστε ασθενοφόρο"
]
```

**Emergency Event Data Structure:**
```json
{
  "emergency_id": "uuid",
  "user_id": "uuid",
  "timestamp": "2025-11-03T14:30:00Z",
  "trigger_phrase": "δεν νιώθω καλά",
  "call_id": "uuid",
  "audio_recording_id": "uuid",
  "transcription": "Full conversation text",
  "location": "Stored user address",
  "status": "active|resolved|false_alarm",
  "alerts_sent": [
    {
      "contact_id": "uuid",
      "method": "sms",
      "sent_at": "2025-11-03T14:30:05Z",
      "delivered": true
    }
  ]
}
```

#### 2.4.2 Missed Call Detection
**Priority:** P1 (High)

**Requirements:**
- Track when scheduled calls are not answered
- Retry with exponential backoff
- Alert emergency contacts after N failed attempts
- Provide escalation workflow

**Missed Call Logic:**
```
Attempt 1: Call at scheduled time
Attempt 2: +15 minutes if no answer
Attempt 3: +30 minutes if no answer
Attempt 4: +1 hour + Alert primary contact
Attempt 5: +2 hours + Alert all emergency contacts
```

**Missed Call Data Structure:**
```json
{
  "missed_call_event_id": "uuid",
  "user_id": "uuid",
  "scheduled_time": "2025-11-03T09:00:00Z",
  "attempts": [
    {
      "attempt_number": 1,
      "timestamp": "2025-11-03T09:00:00Z",
      "status": "no_answer",
      "ring_duration_seconds": 45
    }
  ],
  "alerts_triggered": false,
  "resolved": false,
  "resolution_notes": ""
}
```

#### 2.4.3 Care Circle / Emergency Contacts
**Priority:** P0 (Critical)

**Requirements:**
- Store prioritized list of emergency contacts per user
- Support multiple notification methods (SMS, call, app)
- Include relationship and preferred contact method
- Allow contacts to confirm receipt of alerts

**Care Circle Data Structure:**
```json
{
  "user_id": "uuid",
  "care_circle": [
    {
      "contact_id": "uuid",
      "name": "Γιάννης Παπαδόπουλος",
      "relationship": "son",
      "priority": 1,
      "phone_number": "+30xxxxxxxxxx",
      "email": "giannis@example.com",
      "notification_methods": ["sms", "call"],
      "preferred_method": "call",
      "active": true,
      "verified": true
    },
    {
      "contact_id": "uuid",
      "name": "Ελένη Παπαδοπούλου",
      "relationship": "daughter",
      "priority": 2,
      "phone_number": "+30xxxxxxxxxx",
      "notification_methods": ["sms"],
      "preferred_method": "sms",
      "active": true,
      "verified": true
    }
  ]
}
```

### 2.5 Social Engagement

#### 2.5.1 Activity Suggestions
**Priority:** P1 (High)

**Requirements:**
- Store local activities (ΚΑΠΗ events, church services, etc.)
- Match activities to user interests
- Remind users about upcoming events
- Track attendance/participation

**Activities Data Structure:**
```json
{
  "activity_catalog": [
    {
      "activity_id": "uuid",
      "name": "Πρόβα Χορωδίας",
      "category": "music",
      "location": "ΚΑΠΗ Αθηνών",
      "schedule": {
        "day": "tuesday",
        "time": "15:00",
        "duration_minutes": 90
      },
      "description": "Εβδομαδιαία πρόβα χορωδίας",
      "target_audience": ["music_lovers"],
      "active": true
    }
  ],
  "user_activities": {
    "user_id": "uuid",
    "interested_in": ["music", "crafts", "church"],
    "subscribed_activities": ["uuid1", "uuid2"],
    "attendance_log": [
      {
        "activity_id": "uuid",
        "date": "2025-11-02",
        "attended": true,
        "feedback": "Enjoyed it"
      }
    ]
  }
}
```

---

## 3. Technical Architecture

### 3.1 System Components

#### 3.1.1 Core Services
1. **Voice Processing Pipeline**
   - Soniox STT (Speech-to-Text)
   - Azure OpenAI (LLM)
   - ElevenLabs TTS (Text-to-Speech)
   - Pipecat Framework (Orchestration)

2. **Telephony Integration**
   - Twilio for phone calls (inbound/outbound)
   - Plivo (alternative provider)
   - Daily.co for WebRTC testing

3. **Data Persistence**
   - Upstash Redis (primary database)
   - Redis data structure types: Strings, Hashes, Sets, Sorted Sets

4. **Background Services**
   - Call scheduler (cron-based)
   - Medication reminder service
   - Emergency alert service
   - Health metrics monitoring

5. **API Layer**
   - REST API for care circle portal
   - WebSocket for real-time updates
   - Webhook receivers for telephony events

#### 3.1.2 Infrastructure
- **Hosting:** Cloud provider (AWS, Azure, or GCP)
- **Container orchestration:** Docker + Kubernetes
- **Message queue:** Redis Pub/Sub or RabbitMQ
- **Monitoring:** Prometheus + Grafana
- **Logging:** ELK Stack or CloudWatch

### 3.2 Data Flow Architecture

```
┌─────────────────┐
│   Phone Call    │
│ (Twilio/Plivo)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Pipecat Bot    │
│  (Voice I/O)    │
└────────┬────────┘
         │
         ├─────────────────────┐
         │                     │
         ▼                     ▼
┌─────────────────┐   ┌─────────────────┐
│   Soniox STT    │   │ Emergency       │
│   (Greek)       │   │ Detection       │
└────────┬────────┘   └────────┬────────┘
         │                     │
         ▼                     ▼
┌─────────────────┐   ┌─────────────────┐
│ Azure OpenAI    │   │ Alert Service   │
│ (LLM + Prompt)  │   │ (SMS/Calls)     │
└────────┬────────┘   └─────────────────┘
         │
         ▼
┌─────────────────┐
│ ElevenLabs TTS  │
│ (Greek Voice)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Upstash Redis  │
│  (User Data)    │
└─────────────────┘
```

### 3.3 Redis Data Schema Design

#### 3.3.1 Key Naming Convention
```
niniko:{resource_type}:{user_id}:{sub_resource}
```

**Examples:**
```
niniko:user:550e8400-e29b-41d4-a716-446655440000:profile
niniko:user:550e8400-e29b-41d4-a716-446655440000:medications
niniko:user:550e8400-e29b-41d4-a716-446655440000:appointments
niniko:phone:+306912345678:user_id
niniko:call:call-uuid:metadata
niniko:emergency:emergency-uuid:event
```

#### 3.3.2 Data Types Usage

**User Profile (Hash):**
```redis
HSET niniko:user:{user_id}:profile
  phone_number "+306912345678"
  name "Μαρία Παπαδοπούλου"
  preferred_name "κυρία Μαρία"
  registration_date "2025-11-03T10:00:00Z"
  status "active"
```

**Phone Number Index (String):**
```redis
SET niniko:phone:+306912345678:user_id {user_id}
```

**Medications (JSON stored as String):**
```redis
SET niniko:user:{user_id}:medications "{json_data}"
```

**Call History (Sorted Set by timestamp):**
```redis
ZADD niniko:user:{user_id}:calls
  1699012800 "call-uuid-1"
  1699099200 "call-uuid-2"
```

**Active Emergencies (Set):**
```redis
SADD niniko:active_emergencies emergency-uuid
```

### 3.4 Integration Points

#### 3.4.1 Twilio Integration
- **Inbound calls:** Webhook → Bot Handler
- **Outbound calls:** Scheduler → Twilio API → Bot
- **SMS alerts:** Emergency → Twilio SMS API

#### 3.4.2 Upstash Redis Integration
- **Connection:** Redis client with connection pooling
- **Data access:** Async operations
- **Caching:** User profiles, schedules
- **Pub/Sub:** Real-time updates to care circle portal

---

## 4. User Stories & Acceptance Criteria

### 4.1 User Registration Flow

**As a** new user  
**I want to** register with Niniko by phone  
**So that** the system knows who I am

**Acceptance Criteria:**
- [ ] System captures caller phone number
- [ ] If phone not in database, start registration
- [ ] System asks for user's name in Greek
- [ ] System confirms name back to user
- [ ] System stores profile in Redis
- [ ] System confirms registration complete

### 4.2 Daily Check-in Call

**As a** registered user  
**I want to** receive a daily morning call  
**So that** I have someone to talk to

**Acceptance Criteria:**
- [ ] System calls user at scheduled time
- [ ] System greets user by name in Greek
- [ ] System asks how user is feeling
- [ ] System responds appropriately to user's answers
- [ ] System logs conversation summary
- [ ] Call ends with warm goodbye

### 4.3 Medication Reminder

**As a** user with medications  
**I want to** receive reminders to take my pills  
**So that** I don't forget

**Acceptance Criteria:**
- [ ] System asks about medication during call
- [ ] System reminds user at specified time
- [ ] User can confirm medication taken
- [ ] System logs adherence
- [ ] System alerts caregiver if skipped

### 4.4 Emergency Detection

**As a** user in distress  
**I want to** say "βοήθεια" and get help  
**So that** my family is notified

**Acceptance Criteria:**
- [ ] System detects emergency phrase
- [ ] System reassures user immediately
- [ ] System creates emergency event in Redis
- [ ] System sends SMS to primary contact within 10 seconds
- [ ] System calls primary contact within 30 seconds
- [ ] System logs full context

---

## 5. Implementation Phases

### Phase 1: Core Infrastructure (Week 1-2)
- [ ] Set up Upstash Redis database
- [ ] Design and implement Redis schema
- [ ] Set up Twilio account and phone number
- [ ] Configure Pipecat bot with Soniox, Azure, ElevenLabs
- [ ] Implement phone number-based user identification
- [ ] Create basic user profile management

### Phase 2: Call Management (Week 3-4)
- [ ] Implement call scheduler
- [ ] Build outbound call workflow
- [ ] Integrate Twilio webhooks
- [ ] Implement call logging and history
- [ ] Add conversation context management
- [ ] Test end-to-end call flow

### Phase 3: Health Features (Week 5-6)
- [ ] Implement medication data model
- [ ] Build medication reminder logic
- [ ] Add appointment management
- [ ] Implement health metrics tracking
- [ ] Create adherence reporting
- [ ] Test reminder workflows

### Phase 4: Emergency & Safety (Week 7-8)
- [ ] Implement emergency phrase detection
- [ ] Build alert notification system
- [ ] Set up care circle management
- [ ] Implement missed call detection
- [ ] Add escalation workflows
- [ ] Test emergency scenarios

### Phase 5: Social & Polish (Week 9-10)
- [ ] Add activity suggestion engine
- [ ] Implement attendance tracking
- [ ] Build care circle portal (web interface)
- [ ] Add analytics and reporting
- [ ] Conduct user testing
- [ ] Polish Greek language responses

---

## 6. Technical Requirements & Tools

### 6.1 Development Stack

#### Backend
- **Language:** Python 3.11+
- **Framework:** FastAPI (for API endpoints)
- **Voice Framework:** Pipecat AI
- **Database:** Upstash Redis
- **Task Queue:** Celery + Redis
- **Telephony:** Twilio SDK

#### Required Python Packages
```toml
dependencies = [
    "pipecat-ai[webrtc,silero,soniox,azure,elevenlabs,local-smart-turn-v3,runner]",
    "pipecat-ai-cli",
    "pyyaml>=6.0",
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    "redis>=5.0.0",
    "upstash-redis>=0.15.0",
    "twilio>=8.10.0",
    "celery>=5.3.4",
    "phonenumbers>=8.13.0",
    "python-dotenv>=1.0.0",
    "pydantic>=2.5.0",
    "httpx>=0.25.0",
    "pytz>=2023.3"
]
```

### 6.2 External Services & APIs

#### 6.2.1 Voice & AI Services
- **Soniox:** STT for Greek language
  - API Key required
  - Pricing: Pay per minute
  - Docs: https://soniox.com/docs

- **Azure OpenAI:** LLM for conversations
  - Azure subscription required
  - Endpoint + API key + deployment name
  - Docs: https://learn.microsoft.com/azure/ai-services/openai/

- **ElevenLabs:** TTS for Greek voice
  - API Key required
  - Voice ID for Greek speaker
  - Docs: https://elevenlabs.io/docs

#### 6.2.2 Telephony
- **Twilio:**
  - Account SID + Auth Token
  - Phone number purchase (~$1-5/month)
  - Pricing: $0.0085/min inbound, $0.0140/min outbound
  - SMS: $0.0075/message
  - Docs: https://www.twilio.com/docs

#### 6.2.3 Database
- **Upstash Redis:**
  - Account creation: https://upstash.com
  - Free tier: 10K commands/day
  - Pricing: Pay-as-you-go after free tier
  - Global replication support
  - Docs: https://upstash.com/docs/redis

### 6.3 Development Tools

#### Required Tools
- **UV:** Python package manager
- **Docker:** For containerization
- **Redis CLI:** For database management
- **Postman/Insomnia:** API testing
- **ngrok:** For local webhook testing

#### Monitoring & Logging
- **Sentry:** Error tracking
- **Grafana Cloud:** Metrics visualization
- **Twilio Console:** Call logs and debugging

---

## 7. Security & Privacy

### 7.1 Data Protection
- **GDPR Compliance:** Required for EU users
- **Data encryption:** At rest and in transit
- **Access controls:** Role-based for care circle
- **Audit logging:** All data access logged
- **Data retention:** Configurable per user

### 7.2 Authentication & Authorization
- **Phone number verification:** Primary authentication
- **Care circle access:** Token-based API access
- **API keys:** Secure storage (environment variables)
- **Webhook security:** Signature verification

### 7.3 Privacy Considerations
- **Call recordings:** Optional, with explicit consent
- **Data sharing:** Only with authorized care circle
- **Right to deletion:** User can request data removal
- **Anonymization:** Analytics use anonymized data

---

## 8. Success Metrics

### 8.1 User Engagement
- Daily call completion rate > 90%
- Average call duration: 2-5 minutes
- User satisfaction score > 4.5/5
- Emergency response time < 30 seconds

### 8.2 Health Outcomes
- Medication adherence rate > 85%
- Appointment attendance improvement > 20%
- Reduction in emergency incidents
- User-reported loneliness scores

### 8.3 Technical Performance
- Call connection success rate > 95%
- STT accuracy for Greek > 90%
- System uptime > 99.5%
- Emergency alert delivery < 10 seconds

---

## 9. Risks & Mitigations

### 9.1 Technical Risks
| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| STT accuracy issues | High | Medium | Use Soniox (Greek-optimized), fallback prompts |
| Call quality problems | High | Medium | Use high-quality telephony provider, test network |
| Redis connection failure | Critical | Low | Implement retry logic, use Redis cluster |
| Emergency alert failure | Critical | Low | Multiple notification channels, monitoring |

### 9.2 User Adoption Risks
| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Technology fear | High | High | Simple onboarding, family support |
| Language barriers | High | Low | Greek-only interface, clear pronunciation |
| Privacy concerns | Medium | Medium | Transparent data policy, opt-in features |

---

## 10. Future Enhancements

### Phase 6+ (Post-Launch)
- Multi-language support (English, German)
- Integration with medical devices (BP monitors, glucose meters)
- Video call support
- Family portal mobile app
- AI-powered mood analysis
- Integration with local healthcare systems
- Voice biometric authentication
- Predictive health alerts
- Social features (connect users with similar interests)

---

## 11. Documentation Requirements

### 11.1 Technical Documentation
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Redis schema documentation
- [ ] Deployment guide
- [ ] Monitoring and alerting setup
- [ ] Disaster recovery procedures

### 11.2 User Documentation
- [ ] User guide (Greek)
- [ ] Care circle guide (Greek)
- [ ] Onboarding video
- [ ] FAQ document
- [ ] Privacy policy (Greek + English)

---

## 12. Testing Strategy

### 12.1 Unit Testing
- Redis operations
- User identification logic
- Emergency phrase detection
- Medication reminder scheduling

### 12.2 Integration Testing
- Twilio webhook handling
- End-to-end call flow
- Emergency alert workflow
- Scheduler triggers

### 12.3 User Acceptance Testing
- Greek language accuracy
- Elderly user usability
- Care circle interface
- Emergency scenarios

---

## Appendix A: Context7 MCP Documentation Sources

### Required Documentation Searches

Use Context7 MCP to retrieve documentation for:

1. **Upstash Redis:**
   ```
   /upstash/redis - Python client usage
   ```

2. **Twilio Python SDK:**
   ```
   /twilio/twilio-python - Voice calls, SMS, webhooks
   ```

3. **Pipecat Framework:**
   ```
   /pipecat-ai/pipecat - Transport integration, context management
   ```

4. **FastAPI:**
   ```
   /tiangolo/fastapi - Async endpoints, webhooks
   ```

5. **Celery:**
   ```
   /celery/celery - Task scheduling, Redis backend
   ```

---

## Appendix B: Environment Variables

```bash
# Voice AI Services
SONIOX_API_KEY=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_DEPLOYMENT=
OPENAI_API_VERSION=
ELEVEN_API_KEY=
ELEVENLABS_VOICE_ID=
ELEVENLABS_MODEL=

# Telephony
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# Database
UPSTASH_REDIS_URL=
UPSTASH_REDIS_TOKEN=

# Application
APP_ENV=development
LOG_LEVEL=INFO
SENTRY_DSN=

# Scheduler
SCHEDULER_TIMEZONE=Europe/Athens
```

---

## Appendix C: Redis Commands Reference

```bash
# User lookup by phone
GET niniko:phone:+306912345678:user_id

# Get user profile
HGETALL niniko:user:{user_id}:profile

# Get medications
GET niniko:user:{user_id}:medications

# Get recent calls
ZREVRANGE niniko:user:{user_id}:calls 0 9

# Check active emergencies
SMEMBERS niniko:active_emergencies

# Get emergency details
GET niniko:emergency:{emergency_id}:event
```

---

**Document Status:** Ready for Review  
**Next Steps:** Review with stakeholders, begin Phase 1 implementation
