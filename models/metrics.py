from pydantic import BaseModel
from typing import Dict, Set, Optional
from datetime import datetime

class MonthlyMetrics(BaseModel):
    unique_users: Set[str] = set()
    transcriptions: int = 0
    llm_calls: Dict[str, int] = {"proofread": 0, "my": 0, "business": 0, "brief": 0}
    
    class Config:
        arbitrary_types_allowed = True

class MetricsEvent(BaseModel):
    user_id: str
    event_type: str  # "transcription" or "llm_call"
    event_subtype: Optional[str] = None  # style for LLM calls
    timestamp: datetime = datetime.now()