from typing import Dict, List, Any

class SessionService:
    def __init__(self):
        # In-memory storage for user sessions (use database in production)
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
    
    def get_user_session(self, user_id: str) -> Dict[str, Any]:
        """Get or create user session"""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                "mode": "general",
                "conversation_history": []
            }
        return self.user_sessions[user_id]
    
    def set_user_mode(self, user_id: str, mode: str) -> None:
        """Set chat mode for user"""
        session = self.get_user_session(user_id)
        session["mode"] = mode
    
    def get_user_mode(self, user_id: str) -> str:
        """Get current chat mode for user"""
        session = self.get_user_session(user_id)
        return session["mode"]
    
    def add_to_conversation(self, user_id: str, user_message: str, assistant_message: str) -> None:
        """Add messages to conversation history"""
        session = self.get_user_session(user_id)
        session["conversation_history"].extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_message}
        ])
    
    def get_conversation_history(self, user_id: str) -> List[Dict[str, str]]:
        """Get conversation history for user"""
        session = self.get_user_session(user_id)
        return session["conversation_history"]
    
    def clear_conversation_history(self, user_id: str) -> None:
        """Clear conversation history for user"""
        session = self.get_user_session(user_id)
        session["conversation_history"] = []
    
    def get_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get all user sessions (for debugging/admin purposes)"""
        return self.user_sessions

# Create service instance
session_service = SessionService()