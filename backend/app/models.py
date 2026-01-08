from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from datetime import datetime
from .database import Base


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    farmer_id = Column(String(100), index=True, nullable=False)  # Index for faster queries
    farmer_name = Column(String(255), nullable=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    language = Column(String(10), default="hi-IN")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Add composite index for better query performance
    __table_args__ = (
        Index('idx_farmer_created', 'farmer_id', 'created_at'),
    )