from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import after loading .env
from .database import Base, engine
from .routers import voice

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="🚜 Kisan AI Voice Backend",
    description="Voice-powered agricultural assistant API",
    version="1.0.0"
)

# FIXED: Better CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include routers
app.include_router(voice.router)


@app.get("/")
def root():
    return {
        "message": "🚜 Kisan AI Voice Backend Running",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "chat": "/voice/chat",
            "tts": "/voice/tts",
            "stt": "/voice/stt",
            "history": "/voice/history/{farmer_id}",
            "all_history": "/voice/history"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "api_keys": {
            "google_tts": bool(os.getenv("GOOGLE_TTS_API_KEY")),
            "google_stt": bool(os.getenv("GOOGLE_STT_API_KEY"))
        }
    }