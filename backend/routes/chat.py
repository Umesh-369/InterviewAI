from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.session_store import store
from services.ollama_client import chat as ollama_chat, generate_report
from services.prompt_builder import build_report_prompt
import threading
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    session_id: str
    answer: str

def generate_and_store_report(session_id: str, session_data: dict):
    """Background task to generate report after interview completion."""
    try:
        # Format transcript
        history = session_data["conversation_history"]
        transcript_lines = []
        for msg in history:
            if msg["role"] == "assistant":
                transcript_lines.append(f"Interviewer: {msg['content']}")
            elif msg["role"] == "user":
                transcript_lines.append(f"Candidate: {msg['content']}")
        
        formatted_transcript = "\n\n".join(transcript_lines)
        
        prompt = build_report_prompt(
            job_title=session_data["job_title"],
            resume_text=session_data["resume_text"],
            formatted_transcript=formatted_transcript
        )
        
        # Call ollama to generate report
        report_text = generate_report(prompt)
        
        # Clean up possible markdown fences
        clean_text = report_text.replace("```json", "").replace("```", "").strip()
        
        report_data = None
        try:
            report_data = json.loads(clean_text)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON report. Retrying with stricter prompt.")
            # Retry once with stricter prompt
            report_text = generate_report(prompt, retry_strict=True)
            clean_text = report_text.replace("```json", "").replace("```", "").strip()
            report_data = json.loads(clean_text)
            
        store.update_session(session_id, {"report": report_data})
        logger.info(f"Report generated successfully for session {session_id}")
        
    except Exception as e:
        logger.error(f"Error generating report for session {session_id}: {e}")
        # Store an error state in report so frontend doesn't hang forever
        store.update_session(session_id, {"report": {"error": "Failed to generate report"}})

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    session_data = store.get_session(request.session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if not request.answer.strip():
        raise HTTPException(status_code=400, detail="Answer cannot be empty")
        
    if session_data.get("interview_complete"):
        raise HTTPException(status_code=400, detail="Interview is already complete")
        
    # Append user answer
    session_data["conversation_history"].append({"role": "user", "content": request.answer})
    
    try:
        question, interview_complete = ollama_chat(session_data["conversation_history"])
        
        if interview_complete:
            session_data["interview_complete"] = True
            store.update_session(request.session_id, session_data)
            
            # Launch report generation in background thread
            threading.Thread(
                target=generate_and_store_report, 
                args=(request.session_id, session_data),
                daemon=True
            ).start()
            
            return {
                "question": None,
                "interview_complete": True,
                "turn_number": session_data["turn_count"]
            }
        
        if question:
            session_data["conversation_history"].append({"role": "assistant", "content": question})
            session_data["turn_count"] += 1
            store.update_session(request.session_id, session_data)
            
            return {
                "question": question,
                "interview_complete": False,
                "turn_number": session_data["turn_count"]
            }
            
        raise HTTPException(status_code=500, detail="Unexpected response from AI service")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
