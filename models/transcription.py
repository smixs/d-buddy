from pydantic import BaseModel
from typing import List, Optional, Dict

class Word(BaseModel):
    word: str
    start: float
    end: float
    confidence: float
    speaker: Optional[int] = None  # ID говорящего для диаризации

class Paragraph(BaseModel):
    text: str
    start: float
    end: float
    words: List[Word]
    speaker: Optional[int] = None

class TranscriptionResult(BaseModel):
    text: str
    confidence: float
    words: List[Word]
    language: Optional[str] = None
    paragraphs: Optional[List[Paragraph]] = None  # Разделение на параграфы
    speakers_count: Optional[int] = None  # Количество говорящих
    metadata: Optional[Dict] = None  # Дополнительные метаданные
