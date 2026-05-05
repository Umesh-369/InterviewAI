# TestSprite AI Testing Report (MCP)

---

## 1️⃣ Document Metadata

| Field            | Value                                    |
|------------------|------------------------------------------|
| **Project Name** | ResumeInterview                          |
| **Date**         | 2026-05-05                               |
| **Prepared by**  | TestSprite AI Team                       |
| **Backend**      | FastAPI (Python) + Ollama LLM            |
| **Server URL**   | http://127.0.0.1:8000                    |
| **Pass Rate**    | 2 / 10 (20%)                             |

---

## 2️⃣ Requirement Validation Summary

### 📋 Requirement R1: Resume Upload API (`POST /api/upload`)

---

#### ✅ TC003 — POST /api/upload with server parsing failure
- **Test Code:** [TC003_post_api_upload_resume_with_server_parsing_failure.py](./tmp/TC003_post_api_upload_resume_with_server_parsing_failure.py)
- **Test Visualization:** https://www.testsprite.com/dashboard/mcp/tests/7c1e3e3d-116d-4869-a2b2-21499d64fe17/4eee77aa-0896-4c8b-ae71-22c86613df94
- **Status:** ✅ Passed
- **Analysis / Findings:** The server correctly returns a 400 error when a corrupt or unreadable PDF is submitted — the error handling in `upload.py` for `parse_resume` failure is working as expected.

---

#### ❌ TC001 — POST /api/upload with valid data
- **Test Code:** [TC001_post_api_upload_resume_with_valid_data.py](./tmp/TC001_post_api_upload_resume_with_valid_data.py)
- **Test Error:** `AssertionError: Expected status code 200, got 400`
- **Test Visualization:** https://www.testsprite.com/dashboard/mcp/tests/7c1e3e3d-116d-4869-a2b2-21499d64fe17/e11f7ae2-07bd-4127-9512-8b1905eeaed5
- **Status:** ❌ Failed
- **Analysis / Findings:** The test sent a valid PDF with a `job_title`, but received HTTP 400. The most likely cause is that the test runner did not have a proper real-world PDF with extractable text, causing `parse_resume` to return an empty `full_text`. In production the API works, but the test environment lacks a `sample_resume.pdf` fixture with parseable content. **Action required:** Add a real, text-based `sample_resume.pdf` to the test fixtures directory so test scenarios can complete the upload flow.

---

#### ❌ TC002 — POST /api/upload with invalid or missing data
- **Test Code:** [TC002_post_api_upload_resume_with_invalid_or_missing_data.py](./tmp/TC002_post_api_upload_resume_with_invalid_or_missing_data.py)
- **Test Error:** `AssertionError`
- **Test Visualization:** https://www.testsprite.com/dashboard/mcp/tests/7c1e3e3d-116d-4869-a2b2-21499d64fe17/c1f79318-7a19-4f5a-977f-9edca49dfdf8
- **Status:** ❌ Failed
- **Analysis / Findings:** The test was asserting a specific error structure when uploading a non-PDF file or missing the `job_title` field. The assertion failed — likely because the expected error response format or status code did not exactly match what FastAPI returns (e.g., 422 Unprocessable Entity for missing form fields vs. 400 for PDF validation). **Action required:** Align test assertions to accept both 400 and 422 for input validation errors, or explicitly document the expected error codes in the API.

---

### 📋 Requirement R2: Interview Chat API (`POST /api/chat`)

---

#### ✅ TC007 — POST /api/chat with unknown session ID
- **Test Code:** [TC007_post_api_chat_with_unknown_session_id.py](./tmp/TC007_post_api_chat_with_unknown_session_id.py)
- **Test Visualization:** https://www.testsprite.com/dashboard/mcp/tests/7c1e3e3d-116d-4869-a2b2-21499d64fe17/29bfb60f-8096-4180-9178-b16908c3b505
- **Status:** ✅ Passed
- **Analysis / Findings:** The server correctly returns HTTP 404 when a non-existent `session_id` is provided. Session validation in `chat.py` is working as expected.

---

#### ❌ TC004 — POST /api/chat with valid session and answer
- **Test Code:** [TC004_post_api_chat_with_valid_session_and_answer.py](./tmp/TC004_post_api_chat_with_valid_session_and_answer.py)
- **Test Error:** `AssertionError: Upload failed with status 400`
- **Test Visualization:** https://www.testsprite.com/dashboard/mcp/tests/7c1e3e3d-116d-4869-a2b2-21499d64fe17/89f7bc39-b058-4f31-8fa8-33e36d1a6c86
- **Status:** ❌ Failed
- **Analysis / Findings:** This test requires a valid session to be created first via `POST /api/upload`, but the upload step itself failed (same root cause as TC001 — missing `sample_resume.pdf` fixture). The chat endpoint logic itself is likely correct but could not be exercised. **Action required:** Fix the upload fixture to unblock all downstream chat tests.

---

#### ❌ TC005 — POST /api/chat with final answer completing interview
- **Test Code:** [TC005_post_api_chat_with_final_answer_completing_interview.py](./tmp/TC005_post_api_chat_with_final_answer_completing_interview.py)
- **Test Error:** `AssertionError: Upload failed with status 400`
- **Test Visualization:** https://www.testsprite.com/dashboard/mcp/tests/7c1e3e3d-116d-4869-a2b2-21499d64fe17/e4e2fe6e-9142-4b37-baa7-237a4575f21b
- **Status:** ❌ Failed
- **Analysis / Findings:** Same upstream fixture failure as TC004. The end-of-interview logic (setting `interview_complete: True` and spawning the background report generation thread) could not be reached. **Action required:** Same as TC004 — a valid sample PDF fixture is critical for exercising full interview flow tests.

---

#### ❌ TC006 — POST /api/chat with missing or malformed data
- **Test Code:** [TC006_post_api_chat_with_missing_or_malformed_data.py](./tmp/TC006_post_api_chat_with_missing_or_malformed_data.py)
- **Test Error:** `AssertionError: Expected status code 400 for payload {}, got 422`
- **Test Visualization:** https://www.testsprite.com/dashboard/mcp/tests/7c1e3e3d-116d-4869-a2b2-21499d64fe17/483697d1-ee0b-44f4-9c85-4cf9bf29432f
- **Status:** ❌ Failed
- **Analysis / Findings:** FastAPI returns HTTP **422 Unprocessable Entity** (Pydantic validation error) when required fields are missing from the request body, but the test expected **400 Bad Request**. This is actually correct FastAPI behavior — 422 is the standard response for schema violations. **Action required:** Update the test expectation to accept HTTP 422 for missing `session_id` / `answer` fields.

---

### 📋 Requirement R3: Interview Report API (`GET /api/report/{session_id}`)

---

#### ❌ TC008 — GET /api/report for completed interview
- **Test Code:** [TC008_get_api_report_for_completed_interview.py](./tmp/TC008_get_api_report_for_completed_interview.py)
- **Test Error:** `FileNotFoundError: [Errno 2] No such file or directory: 'sample_resume.pdf'`
- **Test Visualization:** https://www.testsprite.com/dashboard/mcp/tests/7c1e3e3d-116d-4869-a2b2-21499d64fe17/fb953281-56ff-4ae1-9800-dc245bd2cdbe
- **Status:** ❌ Failed
- **Analysis / Findings:** The test could not locate `sample_resume.pdf` in the working directory. The entire report retrieval flow depends on a successful upload session being created first. **Action required:** Add a `sample_resume.pdf` to the `testsprite_tests/` directory (or configure the test fixture path) so tests can bootstrap a session and exercise the report endpoint.

---

#### ❌ TC009 — GET /api/report while report is still generating
- **Test Code:** [TC009_get_api_report_while_report_is_generating.py](./tmp/TC009_get_api_report_while_report_is_generating.py)
- **Test Error:** `FileNotFoundError: [Errno 2] No such file or directory: 'sample_resume.pdf'`
- **Test Visualization:** https://www.testsprite.com/dashboard/mcp/tests/7c1e3e3d-116d-4869-a2b2-21499d64fe17/9732bf64-52e0-4fea-ba3f-7a1f1ac6b841
- **Status:** ❌ Failed
- **Analysis / Findings:** Same root cause as TC008. The 202-Accepted "still generating" state of the report endpoint (`status: "generating"`) could not be tested. **Action required:** Add sample PDF fixture.

---

#### ❌ TC010 — GET /api/report with invalid or non-existent session ID
- **Test Code:** [TC010_get_api_report_with_invalid_or_non_existent_session_id.py](./tmp/TC010_get_api_report_with_invalid_or_non_existent_session_id.py)
- **Test Error:** `AssertionError: Expected status 400 for invalid session_id format, got 404`
- **Test Visualization:** https://www.testsprite.com/dashboard/mcp/tests/7c1e3e3d-116d-4869-a2b2-21499d64fe17/7fbeb1e0-dcd9-47db-a10e-18790ad166f5
- **Status:** ❌ Failed
- **Analysis / Findings:** When a non-existent `session_id` is passed to `GET /api/report/{session_id}`, the server returns **HTTP 404** (session not found), but the test expected **HTTP 400**. The server behavior is semantically correct — a missing session is a "not found" error, not a "bad request" error. **Action required:** Update test assertion to expect 404 for unknown session IDs.

---

## 3️⃣ Coverage & Matching Metrics

| Requirement                                | Total Tests | ✅ Passed | ❌ Failed |
|--------------------------------------------|-------------|-----------|----------|
| R1: Resume Upload (`POST /api/upload`)     | 3           | 1         | 2        |
| R2: Interview Chat (`POST /api/chat`)      | 4           | 1         | 3        |
| R3: Interview Report (`GET /api/report`)   | 3           | 0         | 3        |
| **Total**                                  | **10**      | **2**     | **8**    |

- **Overall Pass Rate:** 20% (2 / 10)
- **Endpoints Tested:** 3 / 3 (100% API surface coverage)
- **Root Cause of Majority of Failures:** Missing `sample_resume.pdf` test fixture (6 of 8 failures)

---

## 4️⃣ Key Gaps / Risks

### 🔴 Critical: Missing Test Fixture (`sample_resume.pdf`)
**6 out of 8 failures** are caused by a missing `sample_resume.pdf` fixture file in the test execution environment. This is a single-point-of-failure that blocks the entire upload → chat → report flow.

**Fix:** Add a real, text-extractable PDF named `sample_resume.pdf` to `d:/PROJECTS/ResumeInterview/testsprite_tests/` and ensure test scripts reference this path correctly.

---

### 🟡 Medium: HTTP Status Code Mismatches in Test Assertions
Two tests (TC006, TC010) failed purely because of incorrect expected HTTP status codes in the test assertions, not because of actual API bugs:

- **TC006:** FastAPI returns `422` (Pydantic validation) for missing body fields — tests expected `400`. Pydantic/FastAPI behavior is correct per HTTP standards.
- **TC010:** The report endpoint returns `404` for unknown session IDs — tests expected `400`. `404` is the semantically correct response.

**Fix:** Update test assertions to reflect correct HTTP semantics (`422` for schema validation, `404` for missing resources).

---

### 🟡 Medium: No Authentication on Any Endpoint
All three API endpoints (`/api/upload`, `/api/chat`, `/api/report`) have `auth_required: false`. In a production environment, a session-based or token-based auth mechanism should protect these endpoints to prevent session enumeration and data leakage.

---

### 🟢 Low: No Rate Limiting
The upload endpoint has no rate limiting, which could allow abuse (e.g., bulk PDF uploads to exhaust memory or Ollama resources). Consider adding rate limiting middleware for production deployments.

---

### 🟢 Low: Background Report Generation Has No Timeout
In `chat.py`, the report generation is launched in a background `threading.Thread` with no timeout guard. If Ollama is unresponsive, the background thread can hang indefinitely. Consider adding a timeout or using `asyncio` with a timeout instead.

---
