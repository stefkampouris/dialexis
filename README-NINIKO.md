# Niniko - Elder Care Voice Companion

## Overview
Niniko is a kind and gentle AI voice companion designed for elderly people in Greece. The bot provides short, daily phone conversations for companionship, gentle health reminders, and emotional reassurance.

## Features

### 🗣️ Voice Services
- **Speech-to-Text**: Soniox (high-quality Greek language support)
- **LLM**: Azure OpenAI (gpt-5-mini) for natural Greek conversations
- **Text-to-Speech**: ElevenLabs (natural Greek voice synthesis)

### 💙 Core Capabilities
1. **Daily Communication & Companionship**
   - Warm Greek greetings and simple questions
   - Empathetic listening and responses
   - Natural, conversational tone

2. **Health & Medication Reminders**
   - Gentle reminders without medical advice
   - Polite encouragement for medication adherence
   - Appointment reminders

3. **Safety & Emergency**
   - Recognizes emergency phrases in Greek
   - Calm, reassuring responses
   - Emergency alert system

4. **Social Engagement**
   - Information about local activities (ΚΑΠΗ, church, etc.)
   - Encouragement for social participation
   - Personalized activity suggestions

5. **Emotional Support**
   - Warm, brief exchanges for comfort
   - Memory prompts and positive reinforcement
   - Suggestions to connect with family when needed

## Configuration

### Environment Variables (`.env`)
```bash
# Speech-to-Text
SONIOX_API_KEY=your_key_here

# Azure OpenAI (LLM)
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-5-mini
OPENAI_API_VERSION=2024-12-01-preview

# Text-to-Speech
ELEVEN_API_KEY=your_key_here
ELEVENLABS_VOICE_ID=aTP4J5SJLQl74WTSRXKW
ELEVENLABS_MODEL=eleven_turbo_v2_5
```

### Prompt Configuration
The system prompt is defined in `prompts/elder-help.yaml` and includes:
- Role definition as "Niniko"
- Core principles (Greek only, simple language, etc.)
- Behavioral guidelines for each capability
- Safety and privacy restrictions

## Running the Bot

### Start the bot:
```powershell
uv run bot.py
```

### Access the web interface:
Open http://localhost:7860/client in your browser

### For production deployment:
- Use appropriate transport (Daily, Twilio, etc.)
- Configure telephony integration
- Set up emergency contact system
- Implement call scheduling

## Customization

### Adjusting the Voice
Edit `.env` to change the ElevenLabs voice:
```bash
ELEVENLABS_VOICE_ID=different_voice_id_here
```

### Modifying Behavior
Edit `prompts/elder-help.yaml` to adjust:
- Greeting style
- Reminder frequency
- Emergency triggers
- Social activity suggestions
- Tone and language complexity

### Adding User Personalization
The prompt supports user-specific data:
- Name
- Interests
- Preferred call times
- Medical reminders
- Family contacts

## Safety Features

### Medical Disclaimer
- Never provides medical, legal, or financial advice
- Does not diagnose or evaluate health conditions
- Refers users to healthcare providers when appropriate

### Privacy
- Uses only provided user information
- Does not store sensitive data beyond current call
- Respects user dignity and privacy

### Emergency Handling
Recognizes phrases like:
- "Δεν νιώθω καλά" (I don't feel well)
- "Νινίκο, βοήθεια!" (Niniko, help!)
- "Έπεσα κάτω" (I fell down)
- "Δεν μπορώ να κουνηθώ" (I can't move)

## Technical Details

### Python Requirements
- Python 3.11+
- UV package manager

### Key Dependencies
- pipecat-ai (with soniox, azure, elevenlabs support)
- PyYAML (for prompt configuration)

### Architecture
```
User → WebRTC/Phone → Soniox STT → Azure OpenAI → ElevenLabs TTS → User
                           ↓
                    Niniko System Prompt
                    (elder-help.yaml)
```

## Support and Development

### Testing
Test the bot with Greek speech to ensure:
- Proper language recognition
- Natural Greek responses
- Appropriate tone and pacing
- Emergency phrase detection

### Monitoring
- Check logs for prompt loading
- Monitor LLM response times
- Verify TTS quality in Greek
- Test emergency triggers

### Future Enhancements
- Multi-user profile management
- Call scheduling system
- Family portal for monitoring
- Activity tracking and reporting
- Integration with health monitoring devices

## License
Check the main repository for license information.
