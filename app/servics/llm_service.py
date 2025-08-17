from groq import Groq
from fastapi import HTTPException
from typing import List, Dict, Any
from app.core.config import settings

class LLMService:
    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required")
        self.client = Groq(
            api_key=settings.GROQ_API_KEY,
            base_url=settings.GROQ_API_URL.replace("/openai/v1/chat/completions", "")
        )
    
    def generate_response(self, text: str, mode: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Generate response using Llama3 via Groq"""
        try:
            system_prompt = settings.SYSTEM_PROMPTS.get(mode, settings.SYSTEM_PROMPTS["general"])
            
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history[-settings.MAX_HISTORY_MESSAGES:])
            
            messages.append({"role": "user", "content": text})
            
            response = self.client.chat.completions.create(
                model=settings.LLAMA_MODEL,
                messages=messages,
                max_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

# Create service instance
llm_service = LLMService()