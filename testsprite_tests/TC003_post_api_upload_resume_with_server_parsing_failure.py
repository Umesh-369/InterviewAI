import requests

def test_post_api_upload_resume_with_invalid_payload():
    url = "http://localhost:8000/api/upload"
    files = {
        "resume": ("fail_resume.pdf", b"%PDF-1.4 fake corrupted content that triggers server parsing failure", "application/pdf")
    }
    data = {
        "job_title": "Software Engineer"
    }
    try:
        response = requests.post(url, files=files, data=data, timeout=30)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"

    # Check the presence of validation error message
    try:
        json_resp = response.json()
    except ValueError:
        assert False, "Expected JSON response with validation error"
    else:
        detail = json_resp.get("detail")
        assert detail is not None, "Expected 'detail' field in validation error response"

    
test_post_api_upload_resume_with_invalid_payload()
