from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class Email(BaseModel):
    id: str
    sender: str
    subject: str
    body: str
    timestamp: str
    category: Optional[str] = None
    action_items: Optional[List[str]] = Field(default_factory=list)
    read: bool = False

class PromptConfig(BaseModel):
    categorization: str
    action_extraction: str
    auto_reply: str

class Draft(BaseModel):
    email_id: str
    subject: str
    body: str
    notes: Optional[str] = None
