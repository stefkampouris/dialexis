import os
import json
from dotenv import load_dotenv

load_dotenv()

secrets = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "ELEVEN_API_KEY": os.getenv("ELEVEN_API_KEY"),
    "SONIOX_API_KEY": os.getenv("SONIOX_API_KEY"),
    "CARTESIA_API_KEY": os.getenv("CARTESIA_API_KEY"),
    "GOOGLE_APPLICATION_CREDENTIALS_JSON": os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON"),
    "AGENT_TYPE": "hotel",
    "HOTEL_CONFIG_PATH": "data/hotel_config.yaml"
}

# Filter out None values
secrets = {k: v for k, v in secrets.items() if v is not None}

with open("secrets.json", "w") as f:
    json.dump(secrets, f, indent=2)

print("✅ secrets.json created successfully from .env")
