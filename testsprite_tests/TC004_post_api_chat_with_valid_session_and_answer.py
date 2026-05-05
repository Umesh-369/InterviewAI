import requests

BASE_URL = "http://localhost:8000"
UPLOAD_ENDPOINT = f"{BASE_URL}/api/upload"
CHAT_ENDPOINT = f"{BASE_URL}/api/chat"
TIMEOUT = 30

def test_post_api_chat_with_valid_session_and_answer():
    session_id = None
    try:
        # Step 1: Upload a resume to create a new session
        files = {
            'resume': ('test_resume.pdf', b'%PDF-1.4\n1 0 obj\n<< >>\nendobj\ntrailer\n<< >>\n%%EOF', 'application/pdf')
        }
        data = {
            'job_title': 'Software Engineer'
        }
        upload_response = requests.post(UPLOAD_ENDPOINT, files=files, data=data, timeout=TIMEOUT)
        assert upload_response.status_code == 200, f"Upload failed with status {upload_response.status_code}"
        upload_json = upload_response.json()
        assert 'session_id' in upload_json and 'first_question' in upload_json
        session_id = upload_json['session_id']
        first_question = upload_json['first_question']

        # Step 2: Submit an answer to /api/chat with the valid session_id and an answer
        chat_payload = {
            "session_id": session_id,
            "answer": "This is a candidate's answer to the first question."
        }
        chat_response = requests.post(CHAT_ENDPOINT, json=chat_payload, timeout=TIMEOUT)
        assert chat_response.status_code == 200, f"Chat API failed with status {chat_response.status_code}"
        chat_json = chat_response.json()

        # Validate the response contains the next question, turn_number, and interview_complete is False
        assert 'question' in chat_json, "Response missing 'question'"
        assert 'turn_number' in chat_json, "Response missing 'turn_number'"
        assert 'interview_complete' in chat_json, "Response missing 'interview_complete'"
        assert isinstance(chat_json['question'], str), "'question' should be a string"
        assert isinstance(chat_json['turn_number'], int), "'turn_number' should be an integer"
        assert chat_json['interview_complete'] is False, "'interview_complete' should be False to continue the interview"

    finally:
        pass

test_post_api_chat_with_valid_session_and_answer()
