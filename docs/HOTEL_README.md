# Hotel AI Receptionist - Quick Start Guide

## Overview
A fully-functional voice AI receptionist for hotels providing 24/7 support for information queries.

## Phase 1 Features ✅
- Hotel information (location, contact, awards)
- Check-in/check-out policies
- Room information and comparisons
- Facility details (restaurants, pool, gym, spa)

## Quick Setup

### 1. Configure Agent Type
Add to your `.env` file:
```ini
AGENT_TYPE=hotel
HOTEL_CONFIG_PATH=data/hotel_config.yaml
```

### 2. Customize Hotel Data (Optional)
Edit `data/hotel_config.yaml` with your hotel's information. The example configuration includes:
- The Grand Seaside Resort (5-star Miami Beach hotel)
- 4 room types
- 5 facilities
- Complete policies

### 3. Run the Bot
```bash
uv run bot.py
```

### 4. Test Queries
Try asking:
- "Tell me about your hotel"
- "What time is check-in?"
- "Can I check in early at 10 AM?"
- "What room types do you have?"
- "Do you have ocean view rooms?"
- "What's the difference between deluxe and standard rooms?"
- "Do you have a pool?"
- "What time does the gym open?"
- "Tell me about your restaurant"

## Architecture

### Data Flow
```
User Voice → STT → LLM + Functions → TTS → Voice Response
                        ↓
                Hotel Knowledge Base (YAML)
```

### Key Components
- **Data Models**: `src/hotel/models.py` - Pydantic models for type safety
- **Knowledge Base**: `src/hotel/hotel_knowledge.py` - YAML config loader
- **Functions**: `src/hotel/hotel_functions.py` - 4 function handlers
- **Config**: `data/hotel_config.yaml` - Hotel data
- **Prompt**: `prompts/hotel-receptionist.yaml` - AI personality

## Switching Between Agents

### Hotel Agent
```ini
AGENT_TYPE=hotel
```

### Dental Agent (Original)
```ini
AGENT_TYPE=dental
```

## Customization

### Add New Room Type
Edit `data/hotel_config.yaml`:
```yaml
rooms:
  - id: "rm_penthouse"
    name: "Penthouse Suite"
    category: "suite"
    # ... add details
```

### Add New Facility
```yaml
facilities:
  - id: "fac_business_center"
    name: "Business Center"
    category: "business"
    # ... add details
```

### Customize Voice & Tone
Edit `prompts/hotel-receptionist.yaml` to adjust:
- Greeting style
- Response patterns
- Tone (formal vs casual)
- Language

## Phase 2 Coming Soon
- Booking management (create, modify, cancel)
- Room service ordering
- Service requests
- Proactive reminders

## Troubleshooting

**Knowledge base not loading?**
- Check `HOTEL_CONFIG_PATH` in `.env`
- Verify YAML syntax in `hotel_config.yaml`

**Functions not being called?**
- Ensure `AGENT_TYPE=hotel` is set
- Check logs for function registration messages

**Wrong agent loading?**
- Verify `.env` file has `AGENT_TYPE=hotel`
- Restart the bot after changing `.env`

## Support
See `implementation_plan.md` and `walkthrough.md` in artifacts for detailed technical information.
