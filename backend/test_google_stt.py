import os
import httpx
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_STT_API_KEY")

print("=" * 60)
print("🔍 GOOGLE STT API TEST")
print("=" * 60)

if not api_key:
    print("❌ GOOGLE_STT_API_KEY not found!")
    print("\nGet key from: https://console.cloud.google.com")
    print("Enable: Cloud Speech-to-Text API")
    exit()

print(f"✅ API Key found: {api_key[:20]}...")

# Test with a simple request
url = f"https://speech.googleapis.com/v1/speech:recognize?key={api_key}"

# Minimal test audio (silence)
test_audio = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAAB9AAACABAAZGF0YQAAAAA="

data = {
    "config": {
        "encoding": "LINEAR16",
        "sampleRateHertz": 8000,  # Fixed to match WAV header
        "languageCode": "en-US"
    },
    "audio": {"content": test_audio}
}

try:
    response = httpx.post(url, json=data, timeout=30.0)
    
    if response.status_code == 200:
        print("✅ API KEY IS VALID!")
        print("Response:", response.json())
    else:
        print(f"❌ API Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Connection Error: {e}")

print("=" * 60)