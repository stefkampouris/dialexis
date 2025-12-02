# Install Google Calendar API dependencies
Write-Host "📦 Installing Google Calendar API Python packages..." -ForegroundColor Cyan

# Install the required packages using uv
uv add google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

Write-Host ""
Write-Host "✅ Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Follow the setup guide in docs/GOOGLE-CALENDAR-SETUP.md"
Write-Host "2. Create a Google Cloud project and enable Calendar API"
Write-Host "3. Download service account credentials"
Write-Host "4. Update your .env file with the credentials path"
Write-Host "5. Share your calendar with the service account email"
Write-Host ""
Write-Host "Run: uv run bot.py" -ForegroundColor Cyan
