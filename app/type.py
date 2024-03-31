from pydantic import BaseModel
from typing import List

class WaybillItem(BaseModel):
    content: str
    category: str

class EventItem(BaseModel):
    event_type: str
    details: dict

class MarketReportRequest(BaseModel):
    industry: str
    keywords: List[str]

class ChatbotMessage(BaseModel):
    message: str
    context: dict
