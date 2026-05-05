from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from services.resume_parser import parse_resume
from services.session_store import store
from services.prompt_builder import build_interview_system_prompt
from services.ollama_client import chat
import uuid

router = APIRouter()

@router.post("/upload")
async def upload_resume(
    resume: UploadFile = File(...),
    job_title: str = Form(...)
):
    if not resume.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        pdf_bytes = await resume.read()
        parsed_data = parse_resume(pdf_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Could not read resume PDF")

    if not parsed_data["full_text"]:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    session_id = str(uuid.uuid4())
    system_prompt = build_interview_system_prompt(job_title, parsed_data["full_text"])
    
    conversation_history = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "I am ready. Please introduce yourself and ask your first question based on my resume."}
    ]
    
    try:
        # Get the first question from Ollama
        first_question, _ = chat(conversation_history)
        if not first_question:
            raise HTTPException(status_code=500, detail="Failed to generate initial question")
            
        conversation_history.append({"role": "assistant", "content": first_question})
        
        session_data = {
            "job_title": job_title,
            "resume_text": parsed_data["full_text"],
            "resume_sections": parsed_data["sections"],
            "conversation_history": conversation_history,
            "turn_count": 1,
            "interview_complete": False,
            "report": None
        }
        
        store.create_session(session_id, session_data)
        
        return {
            "session_id": session_id,
            "first_question": first_question
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
