document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();

    const API_BASE = window.location.protocol === 'file:' 
        ? 'http://127.0.0.1:8000/api' 
        : '/api';
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session');

    const loadingState = document.getElementById('loadingState');
    const errorState = document.getElementById('errorState');
    const reportContainer = document.getElementById('reportContainer');
    const errorText = document.getElementById('errorText');

    if (!sessionId) {
        showError("No session ID found.");
        return;
    }

    fetchReport();

    async function fetchReport() {
        try {
            const response = await fetch(`${API_BASE}/report/${sessionId}`);
            
            if (response.status === 202) {
                // Still generating, poll again
                setTimeout(fetchReport, 2000);
                return;
            }

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Failed to fetch report');
            }

            const reportData = await response.json();
            renderReport(reportData);

        } catch (error) {
            showError(error.message);
        }
    }

    function showError(msg) {
        loadingState.style.display = 'none';
        reportContainer.style.display = 'none';
        errorState.style.display = 'flex';
        errorText.textContent = msg;
    }

    function renderReport(data) {
        loadingState.style.display = 'none';
        reportContainer.style.display = 'block';

        // Overall Score
        const scoreElement = document.getElementById('overallScore');
        const scoreRing = document.getElementById('scoreRing');
        const badge = document.getElementById('recommendationBadge');
        
        let targetScore = data.overall_score || 0;
        let color = 'var(--coral)'; // < 60
        if (targetScore >= 80) color = 'var(--green)';
        else if (targetScore >= 60) color = 'var(--amber)';
        
        scoreRing.style.stroke = color;
        
        // Animate score number
        animateValue(scoreElement, 0, targetScore, 1500);
        
        // Animate ring
        setTimeout(() => {
            const offset = 440 - ((targetScore / 100) * 440);
            scoreRing.style.strokeDashoffset = Math.max(0, offset);
        }, 100);

        // Recommendation Badge
        badge.textContent = data.recommendation;
        if (data.recommendation === 'Selected') {
            badge.className = 'recommendation-badge badge-selected';
            badge.innerHTML = '<i data-lucide="check-circle" width="16"></i> SELECTED';
        } else if (data.recommendation === 'On Hold') {
            badge.className = 'recommendation-badge badge-on-hold';
            badge.innerHTML = '<i data-lucide="clock" width="16"></i> ON HOLD';
        } else {
            badge.className = 'recommendation-badge badge-not-selected';
            badge.innerHTML = '<i data-lucide="x-circle" width="16"></i> NOT SELECTED';
        }

        // Summary
        document.getElementById('reportSummary').innerHTML = marked.parse(data.summary);

        // Categories
        const catContainer = document.getElementById('categoryBars');
        const labels = {
            technical_depth: 'Technical Depth',
            communication: 'Communication',
            relevance_to_role: 'Role Relevance',
            problem_solving: 'Problem Solving',
            resume_accuracy: 'Resume Accuracy'
        };

        if (data.category_scores) {
            for (const [key, value] of Object.entries(data.category_scores)) {
                let barColor = 'var(--coral)';
                if (value >= 75) barColor = 'var(--green)';
                else if (value >= 50) barColor = 'var(--amber)';

                const row = document.createElement('div');
                row.className = 'score-row';
                
                row.innerHTML = `
                    <div class="score-label">${labels[key] || key}</div>
                    <div class="score-bar-bg">
                        <div class="score-bar-fill" style="background-color: ${barColor};" data-width="${value}%"></div>
                    </div>
                    <div class="score-value">${value}%</div>
                `;
                catContainer.appendChild(row);
            }
        }

        // Setup Intersection Observer for bars
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const fill = entry.target.querySelector('.score-bar-fill');
                    if (fill) {
                        fill.style.width = fill.getAttribute('data-width');
                    }
                }
            });
        });

        document.querySelectorAll('.score-row').forEach(row => observer.observe(row));

        // Lists
        populateList('listStrengths', data.strengths);
        populateList('listWeaknesses', data.weaknesses);
        populateList('listImprovements', data.improvements);

        lucide.createIcons();
    }

    function populateList(containerId, items) {
        const container = document.getElementById(containerId);
        if (!items || !items.length) {
            container.innerHTML = '<p style="color: var(--text-muted); font-size: 14px;">No items reported.</p>';
            return;
        }
        
        items.forEach(item => {
            const el = document.createElement('div');
            el.className = 'analysis-card';
            el.innerHTML = marked.parse(item);
            container.appendChild(el);
        });
    }

    function animateValue(obj, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            obj.innerHTML = Math.floor(progress * (end - start) + start);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }

    // Share & Download
    document.getElementById('shareBtn').addEventListener('click', () => {
        const url = window.location.href;
        navigator.clipboard.writeText(url).then(() => {
            const btn = document.getElementById('shareBtn');
            const originalHtml = btn.innerHTML;
            btn.innerHTML = '<i data-lucide="check"></i> Copied!';
            lucide.createIcons();
            setTimeout(() => {
                btn.innerHTML = originalHtml;
                lucide.createIcons();
            }, 2000);
        });
    });

    document.getElementById('downloadBtn').addEventListener('click', () => {
        window.print();
    });
});
