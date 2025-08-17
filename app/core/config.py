import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # App Configuration
    APP_NAME: str = "Voice Assistant ChatBot API"
    APP_DESCRIPTION: str = "A voice assistant with To-do, Job finding, and General chat capabilities"
    APP_VERSION: str = "1.0.0"
    
    # Groq Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_API_URL: str = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
    LLAMA_MODEL: str = "llama3-8b-8192"
    WHISPER_MODEL: str = "whisper-large-v3"
    
    # Model Configuration
    MAX_TOKENS: int = 1024
    TEMPERATURE: float = 0.7
    MAX_HISTORY_MESSAGES: int = 10
    
    # System Prompts for different modes
    SYSTEM_PROMPTS: Dict[str, str] = {
        " FIX ANY TRANSCRIPTION ERRORS IN THE INPUT TEXT, That is the first step before generating a response"

        "todo": """You are a helpful To-Do assistant. Help users manage their tasks, create to-do lists, 
        set reminders, prioritize tasks, and organize their daily activities. Be concise and actionable. when i select to-do only  you can answer to type questions related to to-do tasks, do not answer to other questions""",
        
        "jobfind": """You are a job search assistant. Help users with job hunting, when ask questions related to job finding, otherwise do not answer any other questions.,
        interview preparation, career guidance, and job market insights. Provide practical and professional advice.""",
        
        "general": """You are a helpful general assistant. Answer questions on various topics, 
        provide information, and assist with general inquiries in a friendly and informative manner."""
    }
    
    # Audio Configuration
    TTS_LANGUAGE: str = "en"
    TEMP_DIR: str = "C:\\Users\\Bleh\\Documents\\Willmo_voice\\temp"
    AUDIO_RESPONSE_PATH: str = "C:\\Users\\Bleh\\Documents\\Willmo_voice\\audio_response_path"
    
    # Validation
    def __post_init__(self):
        if not self.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY environment variable is required")

# Create settings instance
settings = Settings()