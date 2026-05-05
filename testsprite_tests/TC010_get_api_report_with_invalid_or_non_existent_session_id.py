import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def test_get_api_report_with_invalid_or_nonexistent_session_id():
    invalid_session_id = "!!!invalid_format###"
    non_existent_session_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

    headers = {
        "Accept": "application/json"
    }

    # Test invalid session_id format - expect 400
    url_invalid = f"{BASE_URL}/api/report/{invalid_session_id}"
    try:
        response_invalid = requests.get(url_invalid, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request failed for invalid session_id format: {e}"
    else:
        assert response_invalid.status_code == 400, (
            f"Expected status 400 for invalid session_id format, got {response_invalid.status_code}"
        )
        # Expect JSON error message or validation error text
        try:
            data = response_invalid.json()
            assert (
                "error" in data or "detail" in data
            ), f"Response JSON missing error/detail field: {data}"
        except ValueError:
            # Response not JSON, acceptable if validation text present
            assert len(response_invalid.text) > 0, "Empty response for invalid session_id format"

    # Test non-existent session_id - expect 404
    url_nonexistent = f"{BASE_URL}/api/report/{non_existent_session_id}"
    try:
        response_nonexistent = requests.get(url_nonexistent, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request failed for non-existent session_id: {e}"
    else:
        assert response_nonexistent.status_code == 404, (
            f"Expected status 404 for non-existent session_id, got {response_nonexistent.status_code}"
        )
        try:
            data = response_nonexistent.json()
            assert (
                "error" in data or "detail" in data
            ), f"Response JSON missing error/detail field: {data}"
        except ValueError:
            # Response not JSON, acceptable if message present
            assert len(response_nonexistent.text) > 0, "Empty response for non-existent session_id"


test_get_api_report_with_invalid_or_nonexistent_session_id()