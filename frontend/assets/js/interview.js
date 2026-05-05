document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    
    const API_BASE = window.location.protocol === 'file:' 
        ? 'http://127.0.0.1:8000/api' 
        : '/api';
    let sessionId = localStorage.getItem('session_id');

    // DOM Elements Phase 1
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const fileNameDisplay = document.getElementById('fileName');
    const fileError = document.getElementById('fileError');
    const jobTitleInput = document.getElementById('jobTitle');
    const startBtn = document.getElementById('startBtn');
    const startBtnText = document.getElementById('startBtnText');
    const setupForm = document.getElementById('setupForm');
    const uploadError = document.getElementById('uploadError');

    // DOM Elements Phase 2
    const uploadPhase = document.getElementById('uploadPhase');
    const chatPhase = document.getElementById('chatPhase');
    const chatMessages = document.getElementById('chatMessages');
    const answerInput = document.getElementById('answerInput');
    const sendBtn = document.getElementById('sendBtn');
    const typingIndicator = document.getElementById('typingIndicator');
    const chatError = document.getElementById('chatError');
    const charCounter = document.getElementById('charCounter');
    
    const sidebarFileName = document.getElementById('sidebarFileName');
    const sidebarJobTitle = document.getElementById('sidebarJobTitle');
    const currentQDisplay = document.getElementById('currentQ');
    const progressCount = document.getElementById('progressCount');
    const progressBar = document.getElementById('progressBar');
    const tipsHeader = document.getElementById('tipsHeader');
    const tipsContent = document.getElementById('tipsContent');
    const tipsIcon = document.getElementById('tipsIcon');

    let currentFile = null;

    // --- PHASE 1 LOGIC ---

    // Drag and drop events
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFile(e.target.files[0]);
        }
    });

    jobTitleInput.addEventListener('input', validateForm);

    function handleFile(file) {
        fileError.textContent = '';
        if (file.type !== 'application/pdf') {
            fileError.textContent = 'Please upload a PDF file.';
            resetFile();
            return;
        }
        if (file.size > 5 * 1024 * 1024) {
            fileError.textContent = 'File exceeds 5MB limit.';
            resetFile();
            return;
        }

        currentFile = file;
        fileNameDisplay.textContent = file.name;
        dropZone.classList.add('hidden');
        fileInfo.classList.remove('hidden');
        validateForm();
    }

    function resetFile() {
        currentFile = null;
        fileInput.value = '';
        dropZone.classList.remove('hidden');
        fileInfo.classList.add('hidden');
        validateForm();
    }

    function validateForm() {
        if (currentFile && jobTitleInput.value.trim().length > 0) {
            startBtn.disabled = false;
        } else {
            startBtn.disabled = true;
        }
    }

    setupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!currentFile || !jobTitleInput.value.trim()) return;

        startBtn.disabled = true;
        startBtnText.innerHTML = '<i data-lucide="loader" class="spinner"></i> Analyzing your resume...';
        lucide.createIcons();
        uploadError.textContent = '';

        const formData = new FormData();
        formData.append('resume', currentFile);
        formData.append('job_title', jobTitleInput.value.trim());

        try {
            const response = await fetch(`${API_BASE}/upload`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Failed to start interview');
            }

            sessionId = data.session_id;
            localStorage.setItem('session_id', sessionId);
            
            // Set sidebar info
            sidebarFileName.textContent = currentFile.name;
            sidebarJobTitle.textContent = jobTitleInput.value.trim();

            switchToChatPhase();
            addMessage('ai', data.first_question);
            updateProgress(1);

        } catch (error) {
            uploadError.textContent = error.message;
            startBtn.disabled = false;
            startBtnText.innerHTML = 'Begin Interview <i data-lucide="arrow-right"></i>';
            lucide.createIcons();
        }
    });

    // --- PHASE 2 LOGIC ---

    function switchToChatPhase() {
        uploadPhase.classList.add('hidden');
        chatPhase.classList.remove('hidden');
        answerInput.focus();
    }

    // Tips accordion
    tipsHeader.addEventListener('click', () => {
        tipsContent.classList.toggle('open');
        tipsIcon.style.transform = tipsContent.classList.contains('open') ? 'rotate(180deg)' : 'rotate(0)';
    });

    // Textarea auto-resize and counter
    answerInput.addEventListener('input', () => {
        answerInput.style.height = 'auto';
        answerInput.style.height = Math.min(answerInput.scrollHeight, 120) + 'px';
        
        const len = answerInput.value.trim().length;
        charCounter.textContent = len;
        
        sendBtn.disabled = len === 0;
    });

    answerInput.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            sendAnswer();
        }
    });

    sendBtn.addEventListener('click', sendAnswer);

    function formatTime() {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    function addMessage(role, text) {
        const wrapper = document.createElement('div');
        wrapper.className = `message-wrapper ${role}`;
        
        const content = document.createElement('div');
        content.className = 'message-content';
        
        const sender = document.createElement('div');
        sender.className = 'message-sender';
        sender.textContent = role === 'ai' ? 'Lyra' : 'You';
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        if (role === 'ai') {
            bubble.innerHTML = marked.parse(text);
        } else {
            bubble.textContent = text;
        }
        
        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = formatTime();
        
        content.appendChild(sender);
        content.appendChild(bubble);
        content.appendChild(time);
        wrapper.appendChild(content);
        
        chatMessages.appendChild(wrapper);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function updateProgress(turn) {
        currentQDisplay.textContent = turn;
        progressCount.textContent = turn;
        // SVG circle logic: 2 * pi * r = ~314
        // Assume ~10 questions max for visual progress
        const maxQ = 10;
        const offset = 314 - ((turn / maxQ) * 314);
        progressBar.style.strokeDashoffset = Math.max(0, offset);
    }

    async function sendAnswer() {
        const text = answerInput.value.trim();
        if (!text) return;

        addMessage('user', text);
        answerInput.value = '';
        answerInput.style.height = 'auto';
        charCounter.textContent = '0';
        sendBtn.disabled = true;
        chatError.textContent = '';
        answerInput.disabled = true;

        typingIndicator.classList.add('active');
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const response = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    answer: text
                })
            });

            const data = await response.json();
            
            typingIndicator.classList.remove('active');

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to send answer');
            }

            if (data.interview_complete) {
                handleCompletion();
            } else {
                addMessage('ai', data.question);
                updateProgress(data.turn_number);
                answerInput.disabled = false;
                answerInput.focus();
            }

        } catch (error) {
            typingIndicator.classList.remove('active');
            chatError.textContent = error.message;
            answerInput.disabled = false;
        }
    }

    function handleCompletion() {
        const overlay = document.getElementById('completionOverlay');
        const overlayError = document.getElementById('overlayError');
        overlay.classList.remove('hidden');
        
        // Poll for report
        const pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`${API_BASE}/report/${sessionId}`);
                
                if (response.status === 200) {
                    clearInterval(pollInterval);
                    window.location.href = `report.html?session=${sessionId}`;
                } else if (response.status === 202) {
                    // Still generating
                } else {
                    const data = await response.json();
                    throw new Error(data.detail || 'Failed to fetch report');
                }
            } catch (error) {
                clearInterval(pollInterval);
                overlayError.textContent = error.message;
            }
        }, 2000);
    }
});
