from groq import Groq
from gtts import gTTS
from fastapi import HTTPException
import os
import tempfile
import uuid
import io
from app.core.config import settings

class SpeechService:
    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required")
        self.client = Groq(
            api_key=settings.GROQ_API_KEY,
            base_url=settings.GROQ_API_URL.replace("/openai/v1/chat/completions", "")
        )
    
    def speech_to_text(self, audio_file) -> str:
        """Convert speech to text using Whisper via Groq"""
        try:
            transcription = self.client.audio.transcriptions.create(
                file=audio_file,
                model=settings.WHISPER_MODEL
            )
            return transcription.text
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in speech recognition: {str(e)}")
    
    def text_to_speech(self, text: str) -> str:
        """Convert text to speech and return file path"""
        try:
            # Ensure audio response directory exists
            os.makedirs(settings.AUDIO_RESPONSE_PATH, exist_ok=True)
            
            tts = gTTS(text=text, lang=settings.TTS_LANGUAGE)
            filename = f"response_{uuid.uuid4()}.mp3"
            filepath = os.path.join(settings.AUDIO_RESPONSE_PATH, filename)
            tts.save(filepath)
            return filepath
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in text-to-speech: {str(e)}")

# Create service instance
speech_service = SpeechService()