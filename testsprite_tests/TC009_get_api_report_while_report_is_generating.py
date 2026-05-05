import requests
import time

BASE_URL = "http://localhost:8000"
UPLOAD_ENDPOINT = f"{BASE_URL}/api/upload"
CHAT_ENDPOINT = f"{BASE_URL}/api/chat"
REPORT_ENDPOINT = f"{BASE_URL}/api/report"

def test_get_api_report_while_report_is_generating():
    session_id = None
    try:
        # Step 1: Upload a resume to create a session
        with open("sample_resume.pdf", "rb") as resume_file:
            files = {"resume": ("sample_resume.pdf", resume_file, "application/pdf")}
            data = {"job_title": "Software Engineer"}
            response = requests.post(UPLOAD_ENDPOINT, files=files, data=data, timeout=30)
        assert response.status_code == 200, f"Upload failed: {response.text}"
        resp_json = response.json()
        session_id = resp_json.get("session_id")
        assert session_id is not None, "session_id missing in upload response"

        # Step 2: Complete the interview by submitting answers until interview_complete=True
        interview_complete = False
        while not interview_complete:
            answer_payload = {
                "session_id": session_id,
                "answer": "Test answer"
            }
            chat_resp = requests.post(CHAT_ENDPOINT, json=answer_payload, timeout=30)
            assert chat_resp.status_code == 200, f"Chat request failed: {chat_resp.text}"
            chat_json = chat_resp.json()
            interview_complete = chat_json.get("interview_complete", False)

        # Step 3: Immediately request the report, expecting 202 status (processing)
        report_resp = requests.get(f"{REPORT_ENDPOINT}/{session_id}", timeout=30)
        assert report_resp.status_code == 202, f"Expected 202 status when report is generating, got {report_resp.status_code}"

    finally:
        if session_id:
            # Cleanup: No direct delete endpoint specified; if exists, delete here
            pass


test_get_api_report_while_report_is_generating()