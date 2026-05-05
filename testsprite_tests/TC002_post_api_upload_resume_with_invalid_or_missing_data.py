import requests

BASE_URL = "http://localhost:8000"
UPLOAD_ENDPOINT = "/api/upload"
TIMEOUT = 30


def test_post_api_upload_resume_with_invalid_or_missing_data():
    url = f"{BASE_URL}{UPLOAD_ENDPOINT}"

    # Case 1: Missing resume file but with job_title
    files = None
    data = {"job_title": "Software Engineer"}
    response = requests.post(url, files=files, data=data, timeout=TIMEOUT)
    assert response.status_code == 400

    # Case 2: Resume file present but missing job_title
    files = {"resume": ("resume.pdf", b"%PDF-1.4 fake pdf content", "application/pdf")}
    data = {}
    response = requests.post(url, files=files, data=data, timeout=TIMEOUT)
    assert response.status_code == 400

    # Case 3: Invalid resume file type with job_title
    files = {"resume": ("resume.txt", b"not a valid pdf content", "text/plain")}
    data = {"job_title": "Software Engineer"}
    response = requests.post(url, files=files, data=data, timeout=TIMEOUT)
    assert response.status_code == 400

    # Case 4: Empty form data entirely
    response = requests.post(url, files={}, data={}, timeout=TIMEOUT)
    assert response.status_code == 400


test_post_api_upload_resume_with_invalid_or_missing_data()