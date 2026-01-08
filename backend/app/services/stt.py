import os
import httpx
from fastapi import HTTPException
import base64

GOOGLE_STT_KEY = os.getenv("GOOGLE_STT_API_KEY")


async def speech_to_text(audio_base64: str, language: str) -> dict:
    """Convert speech to text using Google Cloud STT"""
    
    if not GOOGLE_STT_KEY:
        raise HTTPException(status_code=500, detail="GOOGLE_STT_API_KEY not configured")
    
    print(f"🎤 STT Request | Language: {language} | Audio length: {len(audio_base64)} chars")
    
    try:
        # Remove data URL prefix if present
        if ',' in audio_base64:
            audio_base64 = audio_base64.split(',')[1]
        
        # Validate base64
        try:
            audio_bytes = base64.b64decode(audio_base64)
            print(f"📊 Decoded audio size: {len(audio_bytes)} bytes")
        except Exception as e:
            print(f"❌ Base64 decode error: {e}")
            raise HTTPException(status_code=400, detail="Invalid audio encoding")
        
        # Check minimum size
        if len(audio_bytes) < 4000:
            print("⚠️ Audio too small - likely no speech")
            return {"text": "", "confidence": 0.0}
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Try with enhanced model first
            response = await client.post(
                f"https://speech.googleapis.com/v1/speech:recognize?key={GOOGLE_STT_KEY}",
                json={
                    "config": {
                        "encoding": "WEBM_OPUS",
                        "audioChannelCount": 1,
                        "languageCode": language,
                        "enableAutomaticPunctuation": True,
                        "model": "latest_long",  # Better for longer audio
                        "useEnhanced": True,
                        "enableWordTimeOffsets": False,
                        "enableWordConfidence": True,
                        "maxAlternatives": 1
                    },
                    "audio": {"content": audio_base64}
                }
            )
            
            if response.status_code != 200:
                error = response.text
                print(f"❌ Google STT Error ({response.status_code}): {error}")
                
                # Try without enhanced model
                print("🔄 Retrying with default model...")
                response = await client.post(
                    f"https://speech.googleapis.com/v1/speech:recognize?key={GOOGLE_STT_KEY}",
                    json={
                        "config": {
                            "encoding": "WEBM_OPUS",
                            "audioChannelCount": 1,
                            "languageCode": language,
                            "enableAutomaticPunctuation": True,
                            "model": "default"
                        },
                        "audio": {"content": audio_base64}
                    }
                )
                
                if response.status_code != 200:
                    raise HTTPException(status_code=500, detail=f"STT error: {response.text}")
            
            result = response.json()
            print(f"📥 STT Response: {result}")
            
            if "results" in result and len(result["results"]) > 0:
                transcript = result["results"][0]["alternatives"][0]["transcript"]
                confidence = result["results"][0]["alternatives"][0].get("confidence", 0)
                print(f"✅ STT Success: '{transcript}' (confidence: {confidence:.2f})")
                return {"text": transcript, "confidence": confidence}
            
            print("🔇 No speech detected in audio")
            print("💡 Tips: Speak louder, closer to mic, reduce background noise")
            return {"text": "", "confidence": 0.0}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ STT Error: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"STT processing failed: {str(e)}")