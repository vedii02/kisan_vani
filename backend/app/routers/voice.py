from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas, crud
from ..services.llm import kisan_chat
from ..services.tts import text_to_speech
from ..services.stt import speech_to_text
from pydantic import BaseModel

router = APIRouter(prefix="/voice", tags=["Voice Chat Bot"])


class ChatRequest(BaseModel):
    message: str
    language: str = "hi-IN"
    farmer_id: str = "farmer_123"
    farmer_name: str = "Anonymous Farmer"


class ChatResponse(BaseModel):
    response: str
    audio: str  # Always include audio
    farmer_id: str
    saved: bool


class TTSRequest(BaseModel):
    text: str
    language: str = "hi-IN"


class TTSResponse(BaseModel):
    audio: str


class STTRequest(BaseModel):
    audio: str
    language: str = "hi-IN"


class STTResponse(BaseModel):
    text: str


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """Chat endpoint with audio response"""
    
    print(f"💬 Chat: '{request.message}' | Lang: {request.language}")
    
    try:
        # Get AI response
        ai_response = await kisan_chat(request.message, request.language)
        print(f"✅ AI: {ai_response[:80]}...")

        # Generate audio
        audio_base64 = await text_to_speech(ai_response, request.language)

        # Save to database
        saved = False
        try:
            chat_data = schemas.ChatHistoryCreate(
                farmer_id=request.farmer_id,
                farmer_name=request.farmer_name,
                question=request.message,
                answer=ai_response,
                language=request.language
            )
            crud.create_chat(db, chat_data)
            saved = True
            print("✅ Saved to database")
        except Exception as e:
            print(f"⚠️ DB save failed: {e}")
        
        return ChatResponse(
            response=ai_response,
            audio=audio_base64,
            farmer_id=request.farmer_id,
            saved=saved
        )
    
    except Exception as e:
        print(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stt", response_model=STTResponse)
async def stt_endpoint(request: STTRequest):
    """Speech-to-Text endpoint"""
    
    print(f"🎤 STT endpoint called | Audio length: {len(request.audio)}")
    
    try:
        result = await speech_to_text(request.audio, request.language)
        return STTResponse(text=result.get("text", ""))
    except Exception as e:
        print(f"❌ STT endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tts", response_model=TTSResponse)
async def tts_endpoint(request: TTSRequest):
    """Text-to-Speech endpoint"""
    
    try:
        audio_base64 = await text_to_speech(request.text, request.language)
        return TTSResponse(audio=audio_base64)
    except Exception as e:
        print(f"❌ TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{farmer_id}")
def get_farmer_history(farmer_id: str, db: Session = Depends(get_db)):
    return crud.get_chats_by_farmer(db, farmer_id)
