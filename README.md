<div align="center">

# 🎯 InterviewAI

### _AI-Powered Technical Interview Simulator_

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Ollama](https://img.shields.io/badge/Ollama-Llama_3.2-000000?style=for-the-badge&logo=meta&logoColor=white)](https://ollama.com)
[![License](https://img.shields.io/badge/License-MIT-F59E0B?style=for-the-badge)](LICENSE)

**A fully local, privacy-first AI interview platform that evaluates candidates based on their actual resume — no cloud APIs, no data leaks.**

[Getting Started](#-getting-started) · [Features](#-features) · [Architecture](#-architecture) · [API Reference](#-api-reference) · [Contributing](#-contributing)

---

</div>

## ✨ Features

<table>
<tr>
<td width="50%">

### 🧠 Intelligent Questioning
Questions are **dynamically generated** from the candidate's uploaded resume — covering real projects, skills, and experience. No generic trivia.

</td>
<td width="50%">

### 💬 Adaptive Conversations
Powered by **Llama 3.2 (3B)** running locally via Ollama, the AI conducts fluid, multi-turn technical interviews that adapt based on responses.

</td>
</tr>
<tr>
<td width="50%">

### 📊 Comprehensive Reports
After the interview, a detailed performance report is generated with **scores, strengths, weaknesses**, and a hire/no-hire recommendation.

</td>
<td width="50%">

### 🔒 100% Local & Private
Everything runs on your machine. Your resume data **never leaves your device** — no external API calls, no cloud storage, no tracking.

</td>
</tr>
<tr>
<td width="50%">

### ⚡ Background Processing
Report generation runs in a **background thread** so the UI stays responsive — no frozen screens or loading spinners blocking the experience.

</td>
<td width="50%">

### 🎨 Premium UI Design
Handcrafted with **glassmorphism, mesh gradients, micro-animations**, and modern typography — zero CSS frameworks, pure craftsmanship.

</td>
</tr>
</table>

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|:------|:-----------|:--------|
| **Backend** | Python 3.11+, FastAPI, Uvicorn | REST API, CORS, static file serving |
| **PDF Parsing** | pdfplumber | Resume text extraction from PDF |
| **HTTP Client** | httpx | Async communication with Ollama |
| **Validation** | Pydantic v2 | Request/response data validation |
| **AI Engine** | Ollama + Llama 3.2:3b | Local LLM inference |
| **Frontend** | HTML5, CSS3, Vanilla JS | Zero-dependency UI |
| **Icons** | Lucide Icons (CDN) | Modern icon set |
| **Typography** | Google Fonts (DM Serif Display, Plus Jakarta Sans) | Premium typefaces |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      BROWSER CLIENT                         │
│  ┌──────────┐   ┌───────────────┐   ┌──────────────────┐   │
│  │ Landing   │──▶│  Interview    │──▶│  Report          │   │
│  │ Page      │   │  Chat UI      │   │  Dashboard       │   │
│  └──────────┘   └───────────────┘   └──────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP (REST)
┌──────────────────────────▼──────────────────────────────────┐
│                    FASTAPI SERVER (:8000)                    │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐     │
│  │ /api/upload  │  │ /api/chat   │  │ /api/report     │     │
│  │   resume     │  │   message   │  │   generation    │     │
│  └──────┬──────┘  └──────┬──────┘  └───────┬─────────┘     │
│         │                │                  │               │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌───────▼─────────┐     │
│  │ Resume      │  │ Prompt      │  │ Session         │     │
│  │ Parser      │  │ Builder     │  │ Store (TTL)     │     │
│  └─────────────┘  └──────┬──────┘  └─────────────────┘     │
│                          │                                  │
│                   ┌──────▼──────┐                            │
│                   │ Ollama      │                            │
│                   │ Client      │                            │
│                   └──────┬──────┘                            │
└──────────────────────────┼──────────────────────────────────┘
                           │ HTTP (:11434)
                   ┌───────▼───────┐
                   │    OLLAMA     │
                   │  llama3.2:3b  │
                   └───────────────┘
```

---

## 📁 Project Structure

```
ResumeInterview/
│
├── 📂 backend/                     # FastAPI application
│   ├── main.py                     # App entry point, CORS & static mount
│   ├── requirements.txt            # Python dependencies
│   ├── 📂 routes/                  # API endpoint handlers
│   │   ├── __init__.py
│   │   ├── upload.py               # POST /api/upload — resume upload
│   │   ├── chat.py                 # POST /api/chat   — interview Q&A
│   │   └── report.py              # GET  /api/report  — fetch report
│   └── 📂 services/                # Business logic layer
│       ├── __init__.py
│       ├── resume_parser.py        # PDF text extraction
│       ├── prompt_builder.py       # LLM prompt construction
│       ├── ollama_client.py        # Ollama HTTP client
│       └── session_store.py        # In-memory session management
│
├── 📂 frontend/                    # Static frontend (served by FastAPI)
│   ├── index.html                  # Landing page
│   ├── interview.html              # Interview chat interface
│   ├── report.html                 # Report dashboard
│   └── 📂 assets/
│       ├── 📂 js/                  # Page-specific JavaScript
│       │   ├── landing.js
│       │   ├── interview.js
│       │   └── report.js
│       └── 📂 styles/             # Page-specific stylesheets
│           ├── landing.css
│           ├── interview.css
│           └── report.css
│
├── 📂 testsprite_tests/            # Automated API test suite
│   ├── TC001–TC010                 # 10 end-to-end test cases
│   └── testsprite-mcp-test-report  # Test execution reports
│
└── README.md                       # ← You are here
```

---

## 🚀 Getting Started

### Prerequisites

| Requirement | Version | Download |
|:------------|:--------|:---------|
| Python | 3.11+ | [python.org](https://python.org/downloads) |
| Ollama | Latest | [ollama.com](https://ollama.com/download) |
| Git | Latest | [git-scm.com](https://git-scm.com) |

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/ResumeInterview.git
cd ResumeInterview
```

### 2️⃣ Set Up the AI Model

```bash
# Download the Llama 3.2 model (~2GB)
ollama pull llama3.2:3b

# Verify Ollama is running (default: http://localhost:11434)
ollama serve
```

### 3️⃣ Install Backend Dependencies

```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4️⃣ Launch the Server

```bash
uvicorn main:app --reload --port 8000
```

### 5️⃣ Open the App

```
🌐  http://localhost:8000
```

> [!TIP]
> The backend serves the frontend as static files — no separate frontend server needed!
> For frontend-only development, use VS Code Live Server on port `5500`. API calls target `http://localhost:8000/api`.

---

## 🚦 Usage Workflow

```
  ┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌──────────────────┐
  │   LANDING    │────▶│   UPLOAD RESUME   │────▶│   AI INTERVIEW  │────▶│   VIEW REPORT    │
  │   PAGE       │     │   + Job Title     │     │   (~10 turns)   │     │   Dashboard      │
  └──────────────┘     └──────────────────┘     └─────────────────┘     └──────────────────┘
```

| Step | Action | Details |
|:----:|:-------|:-------|
| **1** | **Explore** | Browse the landing page to learn about the platform |
| **2** | **Upload** | Drag & drop your PDF resume and enter a target job title |
| **3** | **Interview** | Answer AI-generated questions in a real-time chat interface |
| **4** | **Report** | View your comprehensive performance dashboard with scores & recommendations |

---

## 📡 API Reference

### `POST` /api/upload

Upload a PDF resume and start a new interview session.

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `file` | `File` | PDF resume file (multipart form) |
| `job_title` | `string` | Target job position |

**Response** `200 OK`
```json
{
  "session_id": "uuid-string",
  "message": "Resume uploaded successfully",
  "first_question": "Based on your experience with..."
}
```

---

### `POST` /api/chat

Send a candidate's answer and receive the next interview question.

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `session_id` | `string` | Active session identifier |
| `answer` | `string` | Candidate's response |

**Response** `200 OK`
```json
{
  "question": "Can you elaborate on...",
  "is_complete": false,
  "turn": 3
}
```

---

### `GET` /api/report/{session_id}

Retrieve the generated interview performance report.

**Response** `200 OK`
```json
{
  "status": "completed",
  "report": {
    "overall_score": 78,
    "strengths": ["..."],
    "weaknesses": ["..."],
    "recommendation": "Hire"
  }
}
```

---

## 🧪 Testing

The project includes **10 automated API test cases** powered by [TestSprite](https://testsprite.com):

| Test ID | Description |
|:--------|:------------|
| TC001 | Upload resume with valid data |
| TC002 | Upload resume with invalid/missing data |
| TC003 | Upload resume with server parsing failure |
| TC004 | Chat with valid session and answer |
| TC005 | Chat with final answer completing interview |
| TC006 | Chat with missing or malformed data |
| TC007 | Chat with unknown session ID |
| TC008 | Get report for completed interview |
| TC009 | Get report while report is generating |
| TC010 | Get report with invalid/non-existent session ID |

```bash
# Run all tests
cd testsprite_tests
python -m pytest TC*.py -v
```

---

## 🗺️ Roadmap

- [ ] 🔐 Authentication & user accounts
- [ ] 💾 Persistent database storage (PostgreSQL / SQLite)
- [ ] 📄 Support for DOCX and TXT resume formats
- [ ] 🌍 Multi-language interview support
- [ ] 📈 Historical performance tracking & analytics
- [ ] 🎙️ Voice-based interview mode
- [ ] 🐳 Docker containerization
- [ ] ☁️ One-click cloud deployment

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

> [!IMPORTANT]
> Please ensure your code follows the existing project conventions and includes appropriate tests.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ using FastAPI, Ollama & Vanilla JS**

_If this project helped you, consider giving it a ⭐_

</div>
