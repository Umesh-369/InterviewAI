from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from services.session_store import store

router = APIRouter()

@router.get("/report/{session_id}")
async def get_report(session_id: str):
    session_data = store.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if not session_data.get("interview_complete"):
        raise HTTPException(status_code=400, detail="Interview not complete")
        
    report = session_data.get("report")
    
    if report is None:
        return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content={"status": "generating"})
        
    if isinstance(report, dict) and "error" in report:
        raise HTTPException(status_code=500, detail=report["error"])
        
    return report
