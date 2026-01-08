from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ChatHistoryCreate(BaseModel):
    farmer_id: str  # Changed from int to str
    farmer_name: Optional[str] = "Anonymous Farmer"  # NEW
    question: str
    answer: str
    language: str = "hi-IN"


class ChatHistoryResponse(BaseModel):
    id: int
    farmer_id: str  # Changed from int to str
    farmer_name: Optional[str]  # NEW
    question: str
    answer: str
    language: str
    created_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True