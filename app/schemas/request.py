from pydantic import BaseModel
from typing import Optional, Literal, List, Dict, Any
from datetime import datetime

# Request Models
class ChatMode(BaseModel):
    mode: Literal["todo", "jobfind", "general"]

class TextQuery(BaseModel):
    text: str
    mode: Literal["todo", "jobfind", "general"]
    user_id: Optional[str] = None

class TTSRequest(BaseModel):
    text: str

# Response Models
class ChatResponse(BaseModel):
    response: str
    mode: str
    timestamp: str

class ModeResponse(BaseModel):
    message: str
    mode: str
    user_id: str

class CurrentModeResponse(BaseModel):
    current_mode: str
    user_id: str

class VoiceToTextResponse(BaseModel):
    transcribed_text: str
    filename: str

class VoiceChatResponse(BaseModel):
    transcribed_text: str
    response_text: str
    mode: str
    audio_response_path: str
    timestamp: str

class ConversationHistoryResponse(BaseModel):
    user_id: str
    current_mode: str
    conversation_history: List[Dict[str, str]]

class ClearHistoryResponse(BaseModel):
    message: str
    user_id: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    available_modes: List[str]

class ErrorResponse(BaseModel):
    detail: str