import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_post_api_chat_with_unknown_session_id():
    url = f"{BASE_URL}/api/chat"
    unknown_session_id = "nonexistent-session-id-123456"
    payload = {
        "session_id": unknown_session_id,
        "answer": "This is a test answer"
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    assert response.status_code == 404, f"Expected status 404, got {response.status_code}"

    try:
        _ = response.json()
    except ValueError:
        assert False, "Response is not valid JSON."


test_post_api_chat_with_unknown_session_id()