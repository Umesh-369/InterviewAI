import requests

BASE_URL = "http://localhost:8000"
UPLOAD_ENDPOINT = f"{BASE_URL}/api/upload"
CHAT_ENDPOINT = f"{BASE_URL}/api/chat"
TIMEOUT = 30

def test_post_api_chat_with_final_answer_completing_interview():
    session_id = None
    try:
        # Step 1: Upload a valid resume to start an interview session
        files = {
            "resume": ("sample_resume.pdf", b"%PDF-1.4\n%EOF\n", "application/pdf")
        }
        data = {
            "job_title": "Software Engineer"
        }
        upload_response = requests.post(UPLOAD_ENDPOINT, files=files, data=data, timeout=TIMEOUT)
        assert upload_response.status_code == 200, f"Upload failed with status {upload_response.status_code}"
        upload_json = upload_response.json()
        assert "session_id" in upload_json and "first_question" in upload_json
        session_id = upload_json["session_id"]

        # Step 2: Conduct a chat turn to answer with the final answer completing the interview
        final_answer_payload = {
            "session_id": session_id,
            "answer": "This is my final answer completing the interview."
        }
        chat_response = requests.post(CHAT_ENDPOINT, json=final_answer_payload, timeout=TIMEOUT)
        assert chat_response.status_code == 200, f"Chat failed with status {chat_response.status_code}"
        chat_json = chat_response.json()
        assert "interview_complete" in chat_json, "Response missing interview_complete flag"
        assert chat_json["interview_complete"] == True, "Interview complete flag is not true"
    finally:
        # Cleanup: If session_id exists, attempt to delete or cleanup if API supports it
        # The PRD does not specify a delete endpoint so no cleanup action here
        pass

test_post_api_chat_with_final_answer_completing_interview()
