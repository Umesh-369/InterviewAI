import requests
import io

def test_post_api_upload_resume_with_valid_data():
    base_url = "http://localhost:8000"
    upload_url = f"{base_url}/api/upload"
    headers = {}
    timeout = 30

    # Minimal valid PDF content (empty PDF structure)
    pdf_content = b"%PDF-1.4\n%EOF\n"
    files = {
        "resume": ("test_resume.pdf", io.BytesIO(pdf_content), "application/pdf")
    }
    data = {
        "job_title": "Software Engineer"
    }

    try:
        response = requests.post(upload_url, files=files, data=data, headers=headers, timeout=timeout)
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        json_response = response.json()
        assert "session_id" in json_response and isinstance(json_response["session_id"], str) and json_response["session_id"], "Missing or invalid session_id in response"
        assert "first_question" in json_response and isinstance(json_response["first_question"], str) and json_response["first_question"], "Missing or invalid first_question in response"
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

test_post_api_upload_resume_with_valid_data()