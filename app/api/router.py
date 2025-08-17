from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse
import os
import io
from datetime import datetime

from app.schemas.request import (
    ChatMode, TextQuery, TTSRequest,
    ChatResponse, ModeResponse, CurrentModeResponse,
    VoiceToTextResponse, VoiceChatResponse,
    ConversationHistoryResponse, ClearHistoryResponse,
    HealthResponse
)
from app.servics.llm_service import llm_service
from app.servics.speech_service import speech_service
from app.servics.session_service import session_service

router = APIRouter()

@router.post("/set-mode", response_model=ModeResponse)
async def set_chat_mode(mode_data: ChatMode, user_id: str = "default"):
    """Set the chat mode for the user session"""
    session_service.set_user_mode(user_id, mode_data.mode)
    
    return ModeResponse(
        message=f"Chat mode set to {mode_data.mode}",
        mode=mode_data.mode,
        user_id=user_id
    )

@router.get("/get-mode", response_model=CurrentModeResponse)
async def get_chat_mode(user_id: str = "default"):
    """Get current chat mode for user"""
    current_mode = session_service.get_user_mode(user_id)
    
    return CurrentModeResponse(
        current_mode=current_mode,
        user_id=user_id
    )

@router.post("/chat-text", response_model=ChatResponse)
async def chat_with_text(query: TextQuery):
    """Send text query and get text response based on selected mode"""
    user_id = query.user_id or "default"
    
    # Use mode from request or session
    current_mode = query.mode if query.mode else session_service.get_user_mode(user_id)
    session_service.set_user_mode(user_id, current_mode)
    
    # Get conversation history
    conversation_history = session_service.get_conversation_history(user_id)
    
    # Generate response
    response_text = llm_service.generate_response(
        query.text, 
        current_mode, 
        conversation_history
    )
    
    # Update conversation history
    session_service.add_to_conversation(user_id, query.text, response_text)
    
    return ChatResponse(
        response=response_text,
        mode=current_mode,
        timestamp=datetime.now().isoformat()
    )

@router.post("/voice-to-text", response_model=VoiceToTextResponse)
async def convert_voice_to_text(audio: UploadFile = File(...)):
    """Convert uploaded voice file to text using Whisper"""
    if not audio.content_type.startswith('audio/'):
        raise HTTPException(status_code=400, detail="File must be an audio file")
    
    try:
        # Read audio file
        audio_content = await audio.read()
        audio_file = io.BytesIO(audio_content)
        audio_file.name = audio.filename
        
        # Convert to text
        transcribed_text = speech_service.speech_to_text(audio_file)
        
        return VoiceToTextResponse(
            transcribed_text=transcribed_text,
            filename=audio.filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

@router.post("/voice-chat", response_model=VoiceChatResponse)
async def voice_chat(
    audio: UploadFile = File(...),
    mode: str = Form("general"),
    user_id: str = Form("default")
):
    """Complete voice interaction: voice to text, process with LLM, text to speech"""
    if not audio.content_type.startswith('audio/'):
        raise HTTPException(status_code=400, detail="File must be an audio file")
    
    try:
        # Step 1: Convert voice to text
        audio_content = await audio.read()
        audio_file = io.BytesIO(audio_content)
        audio_file.name = audio.filename
        
        transcribed_text = speech_service.speech_to_text(audio_file)
        
        # Step 2: Set mode and get conversation history
        session_service.set_user_mode(user_id, mode)
        conversation_history = session_service.get_conversation_history(user_id)
        
        # Step 3: Generate response with LLM
        response_text = llm_service.generate_response(
            transcribed_text, 
            mode, 
            conversation_history
        )
        
        # Step 4: Update conversation history
        session_service.add_to_conversation(user_id, transcribed_text, response_text)
        
        # Step 5: Convert response to speech
        audio_file_path = speech_service.text_to_speech(response_text)
        
        return VoiceChatResponse(
            transcribed_text=transcribed_text,
            response_text=response_text,
            mode=mode,
            audio_response_path=audio_file_path,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in voice chat: {str(e)}")

@router.post("/text-to-speech")
async def convert_text_to_speech(text: str = Form(...)):
    """Convert text to speech and return audio file"""
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        audio_file_path = speech_service.text_to_speech(text)
        return FileResponse(
            audio_file_path,
            media_type="audio/mpeg",
            filename="response.mp3"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting text to speech: {str(e)}")

@router.get("/download-audio/{filename}")
async def download_audio(filename: str):
    """Download generated audio file"""
    from app.core.config import settings
    file_path = os.path.join(settings.AUDIO_RESPONSE_PATH, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(
        file_path,
        media_type="audio/mpeg",
        filename=filename
    )

@router.get("/conversation-history", response_model=ConversationHistoryResponse)
async def get_conversation_history(user_id: str = "default"):
    """Get conversation history for a user"""
    current_mode = session_service.get_user_mode(user_id)
    conversation_history = session_service.get_conversation_history(user_id)
    
    return ConversationHistoryResponse(
        user_id=user_id,
        current_mode=current_mode,
        conversation_history=conversation_history
    )

@router.delete("/clear-history", response_model=ClearHistoryResponse)
async def clear_conversation_history(user_id: str = "default"):
    """Clear conversation history for a user"""
    session_service.clear_conversation_history(user_id)
    
    return ClearHistoryResponse(
        message="Conversation history cleared",
        user_id=user_id
    )

@router.get("/list-audio-files")
async def list_audio_files():
    """List all saved audio response files"""
    from app.core.config import settings
    
    try:
        if not os.path.exists(settings.AUDIO_RESPONSE_PATH):
            return {"audio_files": [], "message": "Audio response directory not found"}
        
        audio_files = []
        for filename in os.listdir(settings.AUDIO_RESPONSE_PATH):
            if filename.endswith('.mp3'):
                file_path = os.path.join(settings.AUDIO_RESPONSE_PATH, filename)
                file_stats = os.stat(file_path)
                audio_files.append({
                    "filename": filename,
                    "size_bytes": file_stats.st_size,
                    "created_at": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                    "download_url": f"/download-audio/{filename}"
                })
        
        return {
            "audio_files": audio_files,
            "total_files": len(audio_files),
            "audio_response_path": settings.AUDIO_RESPONSE_PATH
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing audio files: {str(e)}")

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        available_modes=["todo", "jobfind", "general"]
    )