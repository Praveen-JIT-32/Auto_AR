import os
from dotenv import load_dotenv
from twilio.rest import Client

# Load .env file
load_dotenv()

# Read environment variables
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
TO_NUMBER = os.getenv("TO_NUMBER")
NGROK_URL = os.getenv("NGROK_URL")

TWIML_URL = f"https://{NGROK_URL}/voice"

print("="*60)
print("📞 Initiating Call")
print(f"To: {TO_NUMBER}")
print(f"URL: {TWIML_URL}")
print("="*60)

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

try:
    call = client.calls.create(
        to=TO_NUMBER,
        from_=TWILIO_PHONE_NUMBER,
        url=TWIML_URL
    )
    print(f"✅ Call SID: {call.sid}")
except Exception as e:
    print(f"❌ Error: {e}")
