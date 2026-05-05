You are a senior full-stack engineer and UI/UX architect. Build a complete,
production-ready AI Interview Platform. Deliver EVERY file fully implemented —
no TODOs, no placeholders, no "implement this yourself" comments.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏗️  SYSTEM OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

An AI-powered mock interview platform where:
1. The candidate lands on a stunning landing page and clicks "Start Interview"
2. They upload their resume (PDF) and enter their target job title
3. The backend parses the resume using pdfplumber and constructs a
   personalized interview session using llama3.2:3b via Ollama (local LLM)
4. The AI conducts a DYNAMIC, ADAPTIVE, CONVERSATIONAL interview — asking
   questions derived ONLY from resume content, relevant to the job title
5. The AI decides when it has gathered enough signal (8–14 questions)
6. A structured performance analysis report is generated with:
   - Overall fit score (0–100%)
   - Category breakdowns with visual scores
   - Strengths, weaknesses, improvement areas
   - Final hire recommendation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧱  TECH STACK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Frontend : Pure HTML5 + CSS3 + Vanilla JavaScript (3 separate HTML pages)
           Zero frameworks. Zero build tools. Direct file serving.
Backend  : FastAPI (Python 3.11+)
LLM      : llama3.2:3b via Ollama (http://localhost:11434)
PDF Parse: pdfplumber (NOT PyPDF2 — it is deprecated and abandoned)
State    : In-memory Python dict keyed by session_id UUID
Fonts    : Google Fonts CDN (Plus Jakarta Sans + DM Serif Display)
Icons    : Lucide Icons CDN (unpkg)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁  PROJECT STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

interview-platform/
├── backend/
│   ├── main.py
│   ├── routes/
│   │   ├── upload.py
│   │   ├── chat.py
│   │   └── report.py
│   ├── services/
│   │   ├── resume_parser.py
│   │   ├── ollama_client.py
│   │   ├── session_store.py
│   │   └── prompt_builder.py
│   └── requirements.txt
├── frontend/
│   ├── index.html          ← Landing page
│   ├── interview.html      ← Upload + Chat interface
│   ├── report.html         ← Performance report
│   └── assets/
│       ├── styles/
│       │   ├── landing.css
│       │   ├── interview.css
│       │   └── report.css
│       └── js/
│           ├── landing.js
│           ├── interview.js
│           └── report.js
└── README.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔌  API CONTRACT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

POST /upload
  Body: multipart/form-data { resume: File (PDF), job_title: string }
  Response: {
    session_id: string,
    first_question: string
  }

POST /chat
  Body: JSON { session_id: string, answer: string }
  Response: {
    question: string | null,
    interview_complete: boolean,
    turn_number: int
  }

GET /report/{session_id}
  Response: {
    overall_score: int,
    recommendation: "Selected" | "Not Selected" | "On Hold",
    summary: string,
    strengths: string[],
    weaknesses: string[],
    improvements: string[],
    category_scores: {
      technical_depth: int,
      communication: int,
      relevance_to_role: int,
      problem_solving: int,
      resume_accuracy: int
    }
  }
  Returns 202 { status: "generating" } if report not yet ready.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠  SESSION STATE SCHEMA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

sessions[session_id] = {
  "job_title": str,
  "resume_text": str,
  "resume_sections": {
    "skills": str,
    "experience": str,
    "projects": str,
    "education": str,
    "certifications": str
  },
  "conversation_history": [
    {"role": "system", "content": "..."},
    {"role": "assistant", "content": "<first question>"},
    {"role": "user", "content": "<answer>"},
    ...
  ],
  "turn_count": int,
  "interview_complete": bool,
  "report": dict | None,
  "created_at": float   ← time.time() for TTL cleanup
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖  INTERVIEW SYSTEM PROMPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Build this in prompt_builder.py → build_interview_system_prompt():

"""
You are a professional technical interviewer conducting a real job interview
for the position of: {job_title}.

You have been given the candidate's resume as your ONLY information source.
Do NOT invent, assume, or reference anything outside the resume.

CANDIDATE RESUME:
{resume_text}

STRICT INTERVIEW RULES — NEVER VIOLATE THESE:
1. Ask exactly ONE question per response. Never combine questions.
2. Every question must reference something explicitly in the resume above.
3. Dynamically adapt based on answer quality:
   - Vague or shallow answer → probe deeper on same topic
   - Strong, detailed answer → advance to next resume area
   - Answer contradicts resume → challenge it professionally
4. Cover these areas in this priority order:
   a) Projects: technical choices, your role, challenges, outcomes
   b) Skills: practical usage scenarios, not textbook definitions
   c) Experience/Internships: responsibilities, impact, what you learned
   d) Education/Certifications: how you applied the knowledge
5. Ask between 8 and 14 questions total. You decide when you have
   sufficient signal to evaluate. Do NOT stop before 8 questions.
6. When you have enough information (never before question 8),
   output ONLY this exact JSON on its own line, nothing else:
   {"interview_complete": true}
7. Do NOT provide feedback, hints, scores, or encouragement mid-interview.
8. Do NOT reveal you are an AI. Maintain interviewer persona throughout.
9. Never repeat a question you have already asked.
10. Be concise. Questions should be 1-2 sentences maximum.
"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊  REPORT GENERATION PROMPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Build this in prompt_builder.py → build_report_prompt():
(This is a SEPARATE Ollama call after interview ends)

"""
You are a senior hiring manager evaluating a completed job interview.

ROLE APPLIED FOR: {job_title}

CANDIDATE RESUME:
{resume_text}

COMPLETE INTERVIEW TRANSCRIPT:
{formatted_transcript}

Your task: Evaluate the candidate objectively and return a JSON report.

RESPOND WITH ONLY VALID JSON — NO markdown fences, NO preamble, NO explanation.
Start your response with {{ and end with }}.

Required JSON structure:
{{
  "overall_score": <integer 0-100>,
  "recommendation": "<Selected|Not Selected|On Hold>",
  "summary": "<3-4 sentence honest assessment of the candidate>",
  "strengths": ["<specific strength from interview>", "<strength 2>", "<strength 3>"],
  "weaknesses": ["<specific weakness observed>", "<weakness 2>"],
  "improvements": [
    "<concrete actionable step to improve>",
    "<improvement 2>",
    "<improvement 3>"
  ],
  "category_scores": {{
    "technical_depth": <integer 0-100>,
    "communication": <integer 0-100>,
    "relevance_to_role": <integer 0-100>,
    "problem_solving": <integer 0-100>,
    "resume_accuracy": <integer 0-100>
  }}
}}

SCORING RULES:
- overall_score 80–100 → recommendation must be "Selected"
- overall_score 60–79  → recommendation must be "On Hold"
- overall_score 0–59   → recommendation must be "Not Selected"
- resume_accuracy: measures if answers matched resume claims (penalize exaggeration)
- Be honest and critical. Do not inflate scores to be kind.
- Base ALL evaluation strictly on what was said in the interview transcript.
"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚙️  BACKEND IMPLEMENTATION DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

resume_parser.py:
- Use pdfplumber exclusively (pip install pdfplumber)
- Extract all text with page.extract_text() across all pages
- Section detection using regex on common headers:
  skills|technical skills, experience|work history|internship,
  projects|personal projects, education|academic, certifications|courses
- Return: { full_text: str, sections: dict }
- If a section is not found, store empty string (never crash)
- Strip excessive whitespace, normalize line endings

ollama_client.py:
- Endpoint: POST http://localhost:11434/api/chat
- Model: llama3.2:3b
- Payload: { model, messages, stream: false, options: { temperature: 0.7, num_ctx: 4096 } }
- Parse response: data["message"]["content"]
- Detect interview_complete: check if '{"interview_complete": true}' in response text
- If detected: strip the JSON from response, return (None, True)
- Else: return (cleaned_question_text, False)
- Timeout: 120s, retry once on timeout with logged warning

chat.py route logic:
1. Validate session_id exists → 404 if not
2. Validate answer is non-empty string → 400 if empty
3. Append {"role": "user", "content": answer} to history
4. Call ollama_client.chat(conversation_history)
5. If interview_complete:
   - Set session["interview_complete"] = True
   - Launch report generation in background thread (threading.Thread)
   - Return: { question: null, interview_complete: true, turn_number: turn_count }
6. If question returned:
   - Append {"role": "assistant", "content": question} to history
   - Increment turn_count
   - Return: { question: question, interview_complete: false, turn_number: turn_count }

report.py route logic:
- GET /report/{session_id}
- If session not found → 404
- If report is None and interview_complete is False → 400 "Interview not complete"
- If report is None and interview_complete is True → 202 { status: "generating" }
- If report exists → 200 with full report dict
- JSON parse safety: strip markdown fences before json.loads()
- On parse failure: retry report generation once with stricter prompt

session_store.py:
- sessions: Dict[str, dict] = {}
- Auto-cleanup: background thread removes sessions older than 7200 seconds
- Thread-safe with threading.Lock()

main.py:
- CORS: allow origins ["http://localhost:5500", "http://127.0.0.1:5500",
  "http://localhost:3000", "null"] — null for file:// protocol
- Mount /frontend as StaticFiles if needed
- Include all routers with /api prefix

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎨  FRONTEND — PAGE 1: index.html (Landing Page)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AESTHETIC: Warm light theme. Soft cream/white base (#FAFAF7).
Animated 3D gradient mesh background with floating orbs in coral,
sky blue, and warm amber. Premium editorial feel.
Fonts: 'DM Serif Display' for headings, 'Plus Jakarta Sans' for body.

BACKGROUND ANIMATION — implement fully in CSS:
- 3 large radial gradient orbs (coral #FF6B6B, sky #74C0FC, amber #FFD43B)
- Each orb animates independently: float up/down + slow rotation
- Use CSS @keyframes: translateY(-30px) + scale(1.1) alternating
- Slight blur (filter: blur(80px)) on orbs for soft glow effect
- Orbs are absolutely positioned, z-index: 0
- Content sits on z-index: 1 above the orbs
- Add subtle CSS noise texture overlay via SVG filter for depth

SECTIONS TO BUILD:
1. Navbar:
   - Left: Logo "InterviewAI" in DM Serif Display
   - Right: "How it Works" anchor link + "Start Interview" CTA button
   - Glassmorphism style: background rgba(255,255,255,0.7), backdrop-filter blur(12px)
   - Sticky on scroll with box-shadow appearing on scroll

2. Hero Section:
   - Large badge pill: "🚀 Powered by Llama 3.2" with subtle border
   - H1: "Ace Your Next Interview" — large, DM Serif Display, ~72px
   - Subheading: "Upload your resume. Our AI interviews you based on YOUR
     experience and gives you an honest performance report."
   - Two CTAs: "Start Interview →" (filled coral) + "See How It Works" (ghost)
   - Below CTAs: Three trust badges inline: "✓ Resume-Based Questions"
     "✓ Adaptive AI" "✓ Instant Report"
   - Hero visual: Floating mock chat window card (CSS-only) showing a
     sample Q&A exchange, gently floating with animation

3. How It Works Section:
   - Section title: "Three Steps to Interview Mastery"
   - Three cards in a row, each with:
     - Large emoji icon in a colored circle
     - Step number
     - Title + 2-line description
   - Cards: Upload Resume → AI Interviews You → Get Your Report
   - Cards have hover lift effect (translateY(-8px) + shadow)

4. Features Section:
   - Asymmetric grid layout (not a boring 3-column)
   - Feature highlights: Adaptive Questioning, Resume-Grounded, Honest Scoring,
     Instant Feedback, No Data Stored, Free & Local
   - Mix of large and small cards (CSS grid with different span sizes)

5. CTA Banner:
   - Full-width coral gradient section
   - "Ready to find out if you're interview-ready?"
   - Large white "Start Your Interview Now" button

6. Footer:
   - Minimal: Logo + "Built with Llama 3.2 & FastAPI" + current year

ANIMATIONS:
- Page load: Elements fade-in + slide-up with staggered animation-delay
- Scroll reveal: Use IntersectionObserver in landing.js to add 'visible' class
- Navbar: Smooth shadow transition on scroll
- All buttons: Subtle scale(1.03) on hover with transition

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎨  FRONTEND — PAGE 2: interview.html (Upload + Chat)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AESTHETIC: Clean, focused light mode. White panels, soft gray background
(#F4F4F0). Coral accents. Like a premium SaaS product interview room.
No distractions. Full focus on the conversation.

LAYOUT: Two-phase on a single page, toggled by JS:

PHASE 1 — Upload Panel (shown on page load):
- Centered card (max-width 520px) with soft shadow
- App logo + "Let's set up your interview" title
- Drag-and-drop PDF zone:
  - Dashed border, rounded corners
  - Center icon (upload cloud from Lucide) + "Drop your resume here"
  - On file select: show filename + size + green checkmark
  - Click-to-browse fallback
  - Validate: PDF only, max 5MB — show inline error if violated
- Text input: "Target Job Title" with placeholder "e.g. Software Engineer"
- "Begin Interview →" button (coral, full width, disabled until both fields filled)
- Loading state on button: spinner + "Analyzing your resume..."

PHASE 2 — Chat Interface (shown after upload succeeds):
- Two-column layout on desktop, single column on mobile:

  LEFT PANEL (280px, fixed):
  - Candidate info card: Name (from resume if extractable, else "You"),
    job title badge, resume filename
  - Interview progress:
    - Circular progress ring (SVG) showing question count
    - Label: "Question 4 of ~10"
  - Interview tips accordion (collapsed by default):
    - "Be specific", "Use examples", "Be concise"
  - Status indicator: green pulsing dot "Interview in progress"

  RIGHT PANEL (flex-grow, scrollable):
  - Top bar: "Technical Interview" title + interviewer avatar (AI icon)
  - Chat messages area:
    - AI messages: left-aligned, soft gray bubble (#F0F0EB),
      AI avatar circle, interviewer label
    - User messages: right-aligned, coral bubble, white text, "You" label
    - Timestamps on each message
    - Smooth scroll to bottom on new message
  - TypingIndicator: Three dots bouncing animation (CSS keyframes)
    shown while waiting for AI response
  - Input area (sticky bottom):
    - Multi-line textarea (auto-expand up to 5 lines)
    - Character counter (bottom right of textarea)
    - Send button (coral, arrow icon) — disabled while AI thinking
    - Keyboard: Ctrl+Enter to send
    - Placeholder: "Type your answer here..."
  - On interview_complete:
    - Overlay appears: "Interview Complete! 🎉"
    - Subtext: "Generating your performance report..."
    - Animated loading bar
    - Auto-redirect to report.html?session={session_id} after report ready
    - Poll GET /report/{session_id} every 2 seconds until 200 response

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎨  FRONTEND — PAGE 3: report.html (Performance Report)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AESTHETIC: Clean light dashboard. White cards on warm gray (#F4F4F0).
Coral, green, and amber as semantic colors. Feels like a premium HR tool.

LAYOUT SECTIONS:

1. Header Bar:
   - Logo left, "Interview Report" title center
   - "Start New Interview" button right (ghost style)

2. Hero Score Section:
   - Large animated SVG circular progress ring (stroke-dashoffset animation)
   - Score number counts up from 0 to final value (requestAnimationFrame)
   - Color: green if ≥80, amber if 60-79, coral/red if <60
   - Below ring: Recommendation badge
     - "✅ SELECTED" (green pill)
     - "⏸ ON HOLD" (amber pill)
     - "❌ NOT SELECTED" (red pill)
   - Candidate name + Job title subtitle

3. Summary Card:
   - Quote-styled card with left border accent
   - AI-generated summary paragraph

4. Category Scores Section:
   - 5 animated horizontal progress bars
   - Each bar: label left, animated fill, score % right
   - Colors: green ≥75, amber 50-74, red <50
   - Bars animate from 0 to value on scroll-into-view using IntersectionObserver
   - Categories: Technical Depth, Communication, Role Relevance,
     Problem Solving, Resume Accuracy

5. Three-Column Analysis:
   - Column 1 "Strengths" — green left border cards with ✓ icon
   - Column 2 "Weaknesses" — amber left border cards with ⚠ icon
   - Column 3 "Improvements" — blue left border cards with → icon
   - Each item is a card with subtle hover state

6. Action Footer:
   - Two buttons: "Download Report (PDF)" — triggers browser print dialog
     with print-specific CSS hiding nav/buttons
   - "Try Again" — navigates to interview.html
   - Share section: copy link button (copies URL with session_id)

PRINT CSS:
- @media print: hide nav, buttons, background colors show as-is
- Page break before section 4 if content is long

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦  DEPENDENCIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

backend/requirements.txt:
  fastapi==0.111.0
  uvicorn==0.29.0
  python-multipart==0.0.9
  pdfplumber==0.10.4
  httpx==0.27.0
  pydantic==2.7.1

Frontend CDN links (in HTML <head>):
  Google Fonts: DM Serif Display + Plus Jakarta Sans
  Lucide Icons: https://unpkg.com/lucide@latest/dist/umd/lucide.js

No npm. No build step. No webpack. Pure browser.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀  SETUP & RUN (generate README.md)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Prerequisites:
1. Install Ollama: https://ollama.com/download
2. Pull model: ollama pull llama3.2:3b
3. Ensure Ollama is running: ollama serve
4. Python 3.11+ installed

Backend:
  cd backend
  pip install -r requirements.txt
  uvicorn main:app --reload --port 8000

Frontend:
  Option A: Open frontend/index.html directly in browser
  Option B (recommended): Use VS Code Live Server on port 5500
  Option C: python -m http.server 5500 from the frontend/ directory

API Base URL in JS files: const API_BASE = 'http://localhost:8000'

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅  QUALITY GATES — ALL MUST BE MET
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Backend:
[ ] Every route has try/except with meaningful HTTP error responses
[ ] Ollama timeout handled gracefully (show user-friendly error)
[ ] JSON parse failure on report retried once with stricter prompt
[ ] Session not found → clear 404 with message
[ ] PDF parse failure → 400 with "Could not read resume PDF"
[ ] All sessions auto-expire after 2 hours

Frontend:
[ ] All three pages are fully responsive (mobile 375px to desktop 1440px)
[ ] No layout breaks at any viewport width
[ ] Loading states on every async action
[ ] Error states shown inline (not just console.log)
[ ] session_id persisted in localStorage between pages
[ ] Empty answer submission blocked client-side
[ ] PDF validation (type + size) before upload attempt
[ ] report.html reads session_id from URL ?session= param
[ ] All CSS animations use will-change and prefers-reduced-motion fallback

CSS:
[ ] All colors defined as CSS custom properties (variables)
[ ] Consistent spacing scale (4px base unit)
[ ] No inline styles except JS-driven dynamic values

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋  DELIVERY ORDER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Generate files in this exact order, each file complete:

1. backend/requirements.txt
2. backend/services/session_store.py
3. backend/services/resume_parser.py
4. backend/services/prompt_builder.py
5. backend/services/ollama_client.py
6. backend/routes/upload.py
7. backend/routes/chat.py
8. backend/routes/report.py
9. backend/main.py
10. frontend/assets/styles/landing.css
11. frontend/index.html
12. frontend/assets/js/landing.js
13. frontend/assets/styles/interview.css
14. frontend/interview.html
15. frontend/assets/js/interview.js
16. frontend/assets/styles/report.css
17. frontend/report.html
18. frontend/assets/js/report.js
19. README.md

Every file must be production-complete. Do NOT skip any file.
Do NOT abbreviate any CSS or JS. Write every line.