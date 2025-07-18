from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NoteCreate(BaseModel):
    text: str

class NoteUpdate(BaseModel):
    text: Optional[str] = None

class NoteOut(BaseModel):
    id: int
    text: str
    created_at: datetime
    owner_id: int

    class Config:
        orm_mode = True 