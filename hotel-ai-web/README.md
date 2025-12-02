# Hotel Messaria Mobile Web Client

A premium, mobile-friendly web interface for the Hotel AI Receptionist.

## Setup

1. **Ensure the Bot is Running**
   The bot must be running on `localhost:7860`.
   ```bash
   cd ..
   uv run bot.py
   ```

2. **Serve the Web Client**
   You need a simple HTTP server to serve this folder.
   
   Using Python:
   ```bash
   python -m http.server 8000
   ```
   
   Using Node/npx:
   ```bash
   npx serve
   ```

3. **Open on Mobile/Desktop**
   - Go to `http://localhost:8000` (or whatever port your server uses).
   - Click the microphone button to call.

## Features
- **Premium Design**: Glassmorphism, animations, and responsive layout.
- **Bilingual Support**: UI indicates EN/EL support.
- **Visual Feedback**: Connection status and audio visualization.
- **Direct Connection**: Connects directly to the running Pipecat bot via WebRTC.

## Troubleshooting
- **CORS Errors**: The bot is configured to allow CORS from `*`, so it should work from any origin.
- **Connection Failed**: Ensure `bot.py` is running and accessible at `http://localhost:7860`.
- **Microphone Permission**: Allow microphone access when prompted.
