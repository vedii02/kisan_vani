from sqlalchemy.orm import Session
from . import models, schemas


def create_chat(db: Session, chat: schemas.ChatHistoryCreate):
    # FIXED: Changed VoiceChat to ChatHistory
    db_chat = models.ChatHistory(**chat.model_dump())
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat


def get_chats_by_farmer(db: Session, farmer_id: str):
    # FIXED: Changed VoiceChat to ChatHistory
    return (
        db.query(models.ChatHistory)
        .filter(models.ChatHistory.farmer_id == farmer_id)
        .order_by(models.ChatHistory.created_at.desc())
        .all()
    )


def get_all_chats(db: Session, skip: int = 0, limit: int = 100):
    """Get all chat history with pagination"""
    return (
        db.query(models.ChatHistory)
        .order_by(models.ChatHistory.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )