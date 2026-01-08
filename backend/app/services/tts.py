import os
import httpx
from fastapi import HTTPException

GOOGLE_TTS_KEY = os.getenv("GOOGLE_TTS_API_KEY")


async def text_to_speech(text: str, language: str) -> str:
    """Convert text to speech using Google Cloud TTS"""
    
    if not GOOGLE_TTS_KEY:
        raise HTTPException(status_code=500, detail="GOOGLE_TTS_API_KEY not configured")
    
    print(f"🔊 TTS: {text[:50]}... | Lang: {language}")
    
    # Complete voice mapping for ALL Indian languages
    voice_mapping = {
        'hi-IN': {'languageCode': 'hi-IN', 'name': 'hi-IN-Wavenet-D'},
        'en-US': {'languageCode': 'en-US', 'name': 'en-US-Wavenet-D'},
        'en-IN': {'languageCode': 'en-IN', 'name': 'en-IN-Wavenet-D'},
        'mr-IN': {'languageCode': 'mr-IN', 'name': 'mr-IN-Wavenet-A'},
        'gu-IN': {'languageCode': 'gu-IN', 'name': 'gu-IN-Wavenet-A'},
        'bn-IN': {'languageCode': 'bn-IN', 'name': 'bn-IN-Wavenet-A'},
        'te-IN': {'languageCode': 'te-IN', 'name': 'te-IN-Standard-A'},
        'ta-IN': {'languageCode': 'ta-IN', 'name': 'ta-IN-Wavenet-A'},
        'kn-IN': {'languageCode': 'kn-IN', 'name': 'kn-IN-Wavenet-A'},
        'ml-IN': {'languageCode': 'ml-IN', 'name': 'ml-IN-Wavenet-A'},
        'pa-IN': {'languageCode': 'pa-IN', 'name': 'pa-IN-Wavenet-A'}
    }
    
    voice = voice_mapping.get(language, voice_mapping['en-US'])
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_TTS_KEY}",
                json={
                    "input": {"text": text},
                    "voice": voice,
                    "audioConfig": {
                        "audioEncoding": "MP3",
                        "speakingRate": 0.9,
                        "pitch": 0.0
                    }
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail=f"TTS error: {response.text}")
            
            data = response.json()
            print("✅ TTS Success")
            return data["audioContent"]
    
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))