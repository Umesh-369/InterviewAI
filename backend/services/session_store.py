import time
import threading
from typing import Dict, Any

class SessionStore:
    def __init__(self):
        self.sessions: Dict[str, dict] = {}
        self.lock = threading.Lock()
        self.ttl = 7200  # 2 hours
        
        # Start background cleanup thread
        self.cleanup_thread = threading.Thread(target=self._auto_cleanup, daemon=True)
        self.cleanup_thread.start()

    def _auto_cleanup(self):
        while True:
            time.sleep(600)  # Check every 10 minutes
            self.cleanup()

    def cleanup(self):
        with self.lock:
            current_time = time.time()
            expired_keys = [
                session_id for session_id, session_data in self.sessions.items()
                if current_time - session_data.get("created_at", 0) > self.ttl
            ]
            for session_id in expired_keys:
                del self.sessions[session_id]

    def create_session(self, session_id: str, data: dict):
        with self.lock:
            data["created_at"] = time.time()
            self.sessions[session_id] = data

    def get_session(self, session_id: str) -> dict | None:
        with self.lock:
            return self.sessions.get(session_id)

    def update_session(self, session_id: str, updates: dict):
        with self.lock:
            if session_id in self.sessions:
                self.sessions[session_id].update(updates)

    def delete_session(self, session_id: str):
        with self.lock:
            if session_id in self.sessions:
                del self.sessions[session_id]

# Singleton instance
store = SessionStore()
