import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def test_post_api_chat_with_missing_or_malformed_data():
    url = f"{BASE_URL}/api/chat"
    test_payloads = [
        {},  # Completely missing both fields
        {"session_id": ""},  # Missing answer
        {"answer": ""},  # Missing session_id
        {"session_id": None, "answer": "answer"},  # session_id None
        {"session_id": "validsession", "answer": None},  # answer None
        {"session_id": 12345, "answer": "some answer"},  # session_id malformed type
        {"session_id": "validsession", "answer": 67890},  # answer malformed type
        {"session_id": "   ", "answer": "valid answer"},  # session_id empty string whitespace
        {"session_id": "validsession", "answer": "   "},  # answer empty string whitespace
    ]

    headers = {"Content-Type": "application/json"}

    for payload in test_payloads:
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        except requests.RequestException as e:
            assert False, f"Request failed with exception: {e}"

        assert response.status_code == 400, (
            f"Expected status code 400 for payload {payload}, got {response.status_code}"
        )
        try:
            error_data = response.json()
        except ValueError:
            assert False, "Response is not valid JSON."

        assert (
            isinstance(error_data, dict) and "detail" in error_data and isinstance(error_data["detail"], list)
        ), f"Response JSON should indicate a validation error, got: {error_data}"


test_post_api_chat_with_missing_or_malformed_data()
