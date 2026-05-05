import requests
import time

BASE_URL = "http://localhost:8000"
UPLOAD_ENDPOINT = f"{BASE_URL}/api/upload"
CHAT_ENDPOINT = f"{BASE_URL}/api/chat"
REPORT_ENDPOINT_TEMPLATE = f"{BASE_URL}/api/report/{{session_id}}"

def test_get_api_report_for_completed_interview():
    timeout = 30
    session_id = None
    try:
        # Step 1: Upload a valid PDF resume to start a session
        with open("sample_resume.pdf", "rb") as resume_file:
            files = {"resume": ("sample_resume.pdf", resume_file, "application/pdf")}
            data = {"job_title": "Software Engineer"}
            upload_response = requests.post(UPLOAD_ENDPOINT, files=files, data=data, timeout=timeout)
        assert upload_response.status_code == 200, f"Unexpected upload status: {upload_response.status_code}"
        upload_json = upload_response.json()
        session_id = upload_json.get("session_id")
        assert session_id, "session_id missing in upload response"

        # Step 2: Complete the interview by sending answers until interview_complete is True
        interview_complete = False
        answer = "Yes, I am ready."
        current_session_id = session_id
        while not interview_complete:
            chat_payload = {"session_id": current_session_id, "answer": answer}
            chat_response = requests.post(CHAT_ENDPOINT, json=chat_payload, timeout=timeout)
            assert chat_response.status_code == 200, f"Unexpected chat status: {chat_response.status_code}"
            chat_json = chat_response.json()
            interview_complete = chat_json.get("interview_complete", False)
            if not interview_complete:
                # Prepare next dummy answer to continue interview
                answer = "This is my answer to the next question."
        
        # Step 3: Poll /api/report/{session_id} endpoint until report is ready (status 200)
        report_url = REPORT_ENDPOINT_TEMPLATE.format(session_id=session_id)
        max_poll_attempts = 10
        poll_interval_sec = 3
        for _ in range(max_poll_attempts):
            report_response = requests.get(report_url, timeout=timeout)
            if report_response.status_code == 200:
                break
            elif report_response.status_code == 202:
                time.sleep(poll_interval_sec)
            else:
                assert False, f"Unexpected report status: {report_response.status_code}"
        else:
            assert False, "Report was not ready within polling attempts"

        # Step 4: Validate the report contents
        report_json = report_response.json()
        assert isinstance(report_json, dict), "Report response is not a dict"
        assert "scores" in report_json, "Report missing 'scores'"
        assert "strengths" in report_json, "Report missing 'strengths'"
        assert "weaknesses" in report_json, "Report missing 'weaknesses'"
        assert "recommendations" in report_json, "Report missing 'recommendations'"

    finally:
        # Cleanup: Delete interview session if API supported it (not specified in PRD). Skipping since no delete endpoint.
        pass

test_get_api_report_for_completed_interview()