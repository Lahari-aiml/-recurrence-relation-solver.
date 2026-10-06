/**
 * Recurrence Relation Solver & AI DAA Tutor
 * Client-Side Interactive Engine
 */

let chatHistory = [];
let activeProblemContext = null;

document.addEventListener('DOMContentLoaded', () => {
    initMathBackground();
    initMobileNav();
    initSolverForm();
    initPresetLoaders();
    initSolutionActions();
    initAITutor();
    initKaTeXAutoRender();
});

/**
 * Mathematical Background Canvas: Rich multi-layer floating math formulas,
 * dynamic sinusoidal wave motion, glowing golden constellation connections,
 * animated grid, and interactive cursor ripple. (Strictly Zero Blue)
 */
function initMathBackground() {
    const canvas = document.getElementById('mathCanvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    let mouse = { x: -1000, y: -1000, radius: 180 };
    let time = 0;

    window.addEventListener('resize', () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });

    window.addEventListener('mousemove', (e) => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    });

    window.addEventListener('mouseleave', () => {
        mouse.x = -1000;
        mouse.y = -1000;
    });

    const mathFormulas = [
        'T(n) = 2T(n/2) + n',
        'T(n) = T(n-1) + 5',
        'Θ(n log n)',
        'k = log₂ n',
        'k = n - 1',
        'T(n/bᵏ) = 1',
        'Θ(n²)',
        'T(n) = 2T(n-1) + 1',
        'Θ(2ⁿ)',
        '∑ᵢ₌₀ᵏ⁻¹ aⁱ',
        'T(1) = 1',
        'Θ(log n)',
        'T(n/2) + 1',
        'O(n)',
        'Ω(1)',
        'f(n) = Θ(g(n))',
        'T(n - k) + ck',
        'aᵏ T(n/bᵏ)',
        '2^k T(n/2^k)',
        'log₂ (n/n₀)',
        'T(n) = Θ(n)'
    ];

    const colors = [
        'rgba(214, 168, 79, ',  // Warm Amber / Gold
        'rgba(245, 240, 230, ', // Parchment Cream
        'rgba(229, 185, 98, ',  // Bright Golden Yellow
        'rgba(127, 166, 123, ', // Sage Green Accent
        'rgba(201, 154, 61, '   // Deep Ochre
    ];

    // Create Mathematical Formula Particles
    const formulas = [];
    const formulaCount = Math.min(32, Math.floor(width / 42));
    for (let i = 0; i < formulaCount; i++) {
        const colorPrefix = colors[Math.floor(Math.random() * colors.length)];
        formulas.push({
            x: Math.random() * width,
            y: Math.random() * height,
            baseX: Math.random() * width,
            text: mathFormulas[Math.floor(Math.random() * mathFormulas.length)],
            fontSize: Math.random() * 5 + 13,
            colorPrefix: colorPrefix,
            opacity: Math.random() * 0.28 + 0.16,
            speedY: Math.random() * 0.45 + 0.22,
            waveFreq: Math.random() * 0.02 + 0.008,
            waveAmp: Math.random() * 25 + 15,
            phase: Math.random() * Math.PI * 2,
            angle: (Math.random() - 0.5) * 0.14,
            rotSpeed: (Math.random() - 0.5) * 0.002
        });
    }

    // Create Constellation Nodes
    const nodes = [];
    const nodeCount = Math.min(52, Math.floor(width / 24));
    for (let i = 0; i < nodeCount; i++) {
        nodes.push({
            x: Math.random() * width,
            y: Math.random() * height,
            radius: Math.random() * 2.2 + 1.2,
            speedX: (Math.random() - 0.5) * 0.55,
            speedY: (Math.random() - 0.5) * 0.55,
            baseOpacity: Math.random() * 0.35 + 0.15,
            pulseOffset: Math.random() * Math.PI * 2
        });
    }

    let gridOffset = 0;

    function animate() {
        ctx.clearRect(0, 0, width, height);
        time += 0.02;

        // 1. Draw animated graph grid with subtle gold drift
        gridOffset = (gridOffset + 0.12) % 50;
        ctx.strokeStyle = 'rgba(214, 168, 79, 0.035)';
        ctx.lineWidth = 1;
        const gridSize = 50;

        for (let x = (gridOffset % gridSize); x < width; x += gridSize) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, height);
            ctx.stroke();
        }
        for (let y = (gridOffset % gridSize); y < height; y += gridSize) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(width, y);
            ctx.stroke();
        }

        // 2. Update and Draw Constellation Nodes & Glowing Golden Lines
        for (let i = 0; i < nodes.length; i++) {
            const node = nodes[i];
            node.x += node.speedX;
            node.y += node.speedY;

            if (node.x < 0) node.x = width;
            if (node.x > width) node.x = 0;
            if (node.y < 0) node.y = height;
            if (node.y > height) node.y = 0;

            const pulseAlpha = node.baseOpacity + Math.sin(time * 2 + node.pulseOffset) * 0.08;

            // Draw Node with subtle glow
            ctx.beginPath();
            ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(214, 168, 79, ${Math.max(0.1, pulseAlpha)})`;
            ctx.fill();

            // Connect nearby nodes
            for (let j = i + 1; j < nodes.length; j++) {
                const node2 = nodes[j];
                const dx = node.x - node2.x;
                const dy = node.y - node2.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < 135) {
                    const lineAlpha = (1 - dist / 135) * 0.14;
                    ctx.beginPath();
                    ctx.moveTo(node.x, node.y);
                    ctx.lineTo(node2.x, node2.y);
                    ctx.strokeStyle = `rgba(214, 168, 79, ${lineAlpha})`;
                    ctx.lineWidth = 1;
                    ctx.stroke();
                }
            }

            // Interactive mouse proximity connection
            const mouseDx = node.x - mouse.x;
            const mouseDy = node.y - mouse.y;
            const mouseDist = Math.sqrt(mouseDx * mouseDx + mouseDy * mouseDy);
            if (mouseDist < mouse.radius) {
                const mouseAlpha = (1 - mouseDist / mouse.radius) * 0.32;
                ctx.beginPath();
                ctx.moveTo(node.x, node.y);
                ctx.lineTo(mouse.x, mouse.y);
                ctx.strokeStyle = `rgba(229, 185, 98, ${mouseAlpha})`;
                ctx.lineWidth = 1.3;
                ctx.stroke();
            }
        }

        // 3. Update and Draw Mathematical Formulas with Sinusoidal Wave Glide
        for (let f of formulas) {
            f.y -= f.speedY;
            f.x = f.baseX + Math.sin(time * f.waveFreq * 60 + f.phase) * f.waveAmp;
            f.angle += f.rotSpeed;

            // Mouse proximity highlight
            const dx = f.x - mouse.x;
            const dy = f.y - mouse.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            let currentOpacity = f.opacity;

            if (dist < 150) {
                currentOpacity = Math.min(0.65, f.opacity * 2.2);
            }

            ctx.save();
            ctx.translate(f.x, f.y);
            ctx.rotate(f.angle);
            ctx.font = `600 ${f.fontSize}px 'Fira Code', 'JetBrains Mono', monospace`;
            ctx.fillStyle = `${f.colorPrefix}${currentOpacity})`;
            ctx.fillText(f.text, 0, 0);
            ctx.restore();

            // Screen boundary wrap
            if (f.y < -50) {
                f.y = height + 30;
                f.baseX = Math.random() * width;
                f.text = mathFormulas[Math.floor(Math.random() * mathFormulas.length)];
            }
            if (f.x < -120) f.baseX = width + 60;
            if (f.x > width + 120) f.baseX = -60;
        }

        requestAnimationFrame(animate);
    }

    animate();
}

/**
 * Global helper to quick solve/load a recurrence into solver input
 */
function quickSolve(formula, baseCase = 'T(1) = 1') {
    // If not on home page, navigate to home with query parameters or redirect
    const recInput = document.getElementById('recurrence');
    const baseInput = document.getElementById('base_case');
    const solverCard = document.getElementById('solverCard');

    if (recInput && baseInput) {
        // Strip T(n) = prefix if provided
        let cleanFormula = formula;
        if (cleanFormula.startsWith('T(n) =') || cleanFormula.startsWith('T(n)=')) {
            cleanFormula = cleanFormula.replace(/^T\(n\)\s*=\s*/, '');
        }

        recInput.value = cleanFormula;
        baseInput.value = baseCase;

        if (solverCard) {
            solverCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
            recInput.focus();
        }
    } else {
        // Redirect to index page
        window.location.href = `/?rec=${encodeURIComponent(formula)}&base=${encodeURIComponent(baseCase)}`;
    }
}

/**
 * Preset loaders and URL query parameter detection
 */
function initPresetLoaders() {
    // Check URL parameters (e.g. ?rec=...&base=...)
    const params = new URLSearchParams(window.location.search);
    const recParam = params.get('rec');
    const baseParam = params.get('base');

    if (recParam) {
        const recInput = document.getElementById('recurrence');
        const baseInput = document.getElementById('base_case');
        if (recInput) {
            recInput.value = recParam.replace(/^T\(n\)\s*=\s*/, '');
            if (baseInput && baseParam) baseInput.value = baseParam;
            const solverCard = document.getElementById('solverCard');
            if (solverCard) {
                solverCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    }
}

/**
 * Mobile Navigation Hamburger Menu Toggle
 */
function initMobileNav() {
    const toggleBtn = document.getElementById('mobileNavToggle');
    const navLinks = document.getElementById('navLinks');

    if (toggleBtn && navLinks) {
        toggleBtn.addEventListener('click', () => {
            navLinks.classList.toggle('show');
        });
    }
}

/**
 * Main Solver Form Validation & Input Handling
 */
function initSolverForm() {
    const form = document.getElementById('mainSolverForm');
    const recInput = document.getElementById('recurrence');
    const clearBtn = document.getElementById('clearRecurrenceBtn');
    const resetBtn = document.getElementById('resetSolverBtn');
    const errorAlert = document.getElementById('clientErrorAlert');
    const errorMsg = document.getElementById('clientErrorMsg');

    if (clearBtn && recInput) {
        clearBtn.addEventListener('click', () => {
            recInput.value = '';
            recInput.focus();
        });
    }

    if (resetBtn && form) {
        resetBtn.addEventListener('click', () => {
            form.reset();
            if (recInput) recInput.focus();
            if (errorAlert) errorAlert.style.display = 'none';
        });
    }

    if (form && recInput) {
        form.addEventListener('submit', (e) => {
            const val = recInput.value.trim();
            if (!val) {
                e.preventDefault();
                if (errorAlert && errorMsg) {
                    errorMsg.textContent = 'Please enter a recurrence relation before solving.';
                    errorAlert.style.display = 'flex';
                }
                recInput.focus();
                return;
            }

            // Normalise formula: if user entered without T(n) = , keep clean
            if (errorAlert) errorAlert.style.display = 'none';
        });
    }
}

/**
 * Solution Page Actions: Copy, Print, Context Passing
 */
function initSolutionActions() {
    const copyEqBtn = document.getElementById('copyEquationBtn');
    const copySolBtn = document.getElementById('copySolutionBtn');
    const printBtn = document.getElementById('printSolutionBtn');
    const askTutorBtn = document.getElementById('solutionAskTutorBtn');

    // Extract active problem context from hidden JSON script tag if on solution page
    const contextScript = document.getElementById('currentSolutionData');
    if (contextScript) {
        try {
            activeProblemContext = JSON.parse(contextScript.textContent);
            updateAITutorContextBanner(activeProblemContext);
        } catch (e) {
            console.error('Could not parse solution context:', e);
        }
    }

    if (copyEqBtn) {
        copyEqBtn.addEventListener('click', () => {
            const eq = copyEqBtn.getAttribute('data-equation') || '';
            navigator.clipboard.writeText(eq).then(() => {
                const orig = copyEqBtn.innerHTML;
                copyEqBtn.innerHTML = '<span>✓</span> Copied!';
                setTimeout(() => { copyEqBtn.innerHTML = orig; }, 2000);
            });
        });
    }

    if (copySolBtn) {
        copySolBtn.addEventListener('click', () => {
            if (activeProblemContext) {
                const textToCopy = `Recurrence: ${activeProblemContext.recurrence}\nBase Case: ${activeProblemContext.base_case}\nExact Solution: ${activeProblemContext.exact_solution}\nComplexity: ${activeProblemContext.complexity}\nMethod: ${activeProblemContext.method}`;
                navigator.clipboard.writeText(textToCopy).then(() => {
                    const orig = copySolBtn.innerHTML;
                    copySolBtn.innerHTML = '<span>✓</span> Solution Copied!';
                    setTimeout(() => { copySolBtn.innerHTML = orig; }, 2000);
                });
            }
        });
    }

    if (printBtn) {
        printBtn.addEventListener('click', () => {
            window.print();
        });
    }

    if (askTutorBtn) {
        askTutorBtn.addEventListener('click', () => {
            openTutorWithCurrentContext();
        });
    }
}

/**
 * AI Tutor Controller (Modal & Context Integration)
 */
function initAITutor() {
    const toggleBtn = document.getElementById('floatingTutorToggleBtn');
    const navTutorBtn = document.getElementById('navAITutorBtn');
    const heroTutorBtn = document.getElementById('heroOpenTutorBtn');
    const closeBtn = document.getElementById('closeTutorPanelBtn');
    const tutorPanel = document.getElementById('aiTutorPanel');
    const form = document.getElementById('tutorInputForm');
    const input = document.getElementById('tutorInputText');
    const messages = document.getElementById('tutorChatMessages');
    const typing = document.getElementById('tutorTypingIndicator');
    const chips = document.querySelectorAll('.tutor-chip');

    function openPanel() {
        if (tutorPanel) {
            tutorPanel.classList.add('active');
            if (input) input.focus();
        }
    }

    function closePanel() {
        if (tutorPanel) {
            tutorPanel.classList.remove('active');
        }
    }

    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            if (tutorPanel.classList.contains('active')) {
                closePanel();
            } else {
                openPanel();
            }
        });
    }

    if (navTutorBtn) navTutorBtn.addEventListener('click', openPanel);
    if (heroTutorBtn) heroTutorBtn.addEventListener('click', openPanel);
    if (closeBtn) closeBtn.addEventListener('click', closePanel);

    // Question Suggestion Chips
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            const question = chip.getAttribute('data-question');
            if (question) {
                openPanel();
                sendQuestionToTutor(question, messages, typing);
            }
        });
    });

    // Form Submission
    if (form && input) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const text = input.value.trim();
            if (!text) return;
            input.value = '';
            sendQuestionToTutor(text, messages, typing);
        });
    }
}

/**
 * Opens AI Tutor and adds a welcome prompt about the active problem
 */
function openTutorWithCurrentContext() {
    const tutorPanel = document.getElementById('aiTutorPanel');
    const messages = document.getElementById('tutorChatMessages');
    if (tutorPanel) {
        tutorPanel.classList.add('active');
    }

    if (activeProblemContext && messages) {
        const welcomeId = 'ctx-welcome-bubble';
        if (!document.getElementById(welcomeId)) {
            const ctxDiv = document.createElement('div');
            ctxDiv.id = welcomeId;
            ctxDiv.className = 'chat-bubble tutor-bubble';
            ctxDiv.innerHTML = `
                <div class="bubble-avatar">🤖</div>
                <div class="bubble-body">
                    <div class="bubble-author">Recurrence AI Tutor</div>
                    <div class="bubble-text">
                        I see you're currently analyzing <strong>$${activeProblemContext.recurrence}$</strong> with <strong>$${activeProblemContext.base_case}$</strong>.
                        <br><br>
                        What would you like me to clarify about the substitution derivation or complexity bound <strong>$${activeProblemContext.complexity_latex}$</strong>?
                    </div>
                </div>`;
            messages.appendChild(ctxDiv);
            typesetMath(ctxDiv);
            scrollToBottom(messages);
        }
    }
}

/**
 * Updates the context banner inside the AI Tutor header
 */
function updateAITutorContextBanner(context) {
    const banner = document.getElementById('tutorContextBanner');
    const formulaEl = document.getElementById('tutorContextFormula');
    const compEl = document.getElementById('tutorContextComplexity');

    if (banner && formulaEl && compEl && context && context.recurrence) {
        formulaEl.textContent = context.recurrence;
        compEl.textContent = context.complexity || '';
        banner.style.display = 'flex';
    }
}

/**
 * Sends a message to the backend /api/chat endpoint
 */
async function sendQuestionToTutor(questionText, containerEl, typingEl) {
    if (!containerEl) return;

    // 1. Render User Message
    appendTutorMessage(containerEl, 'user', questionText);
    chatHistory.push({ role: 'user', content: questionText });

    // 2. Show Typing Indicator
    if (typingEl) typingEl.style.display = 'flex';
    scrollToBottom(containerEl);

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: questionText,
                history: chatHistory,
                context: activeProblemContext
            })
        });

        const data = await response.json();

        if (typingEl) typingEl.style.display = 'none';

        if (data && data.response) {
            appendTutorMessage(containerEl, 'tutor', data.response, data);
            chatHistory.push({ role: 'assistant', content: data.response });

            // If equation was solved directly in chat, offer load in solver button
            if (data.equation_solved && data.recurrence) {
                // optional quick action
            }
        } else {
            appendTutorMessage(containerEl, 'tutor', 'Sorry, I could not process that question. Please try asking again.');
        }
    } catch (err) {
        if (typingEl) typingEl.style.display = 'none';
        appendTutorMessage(containerEl, 'tutor', '⚠️ Network connection error. Please try again.');
    }

    scrollToBottom(containerEl);
}

/**
 * Appends a message bubble into the AI Tutor chat
 */
function appendTutorMessage(containerEl, sender, text, meta = null) {
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${sender === 'user' ? 'user-bubble' : 'tutor-bubble'}`;

    const avatar = sender === 'user' ? '👤' : '🤖';
    const author = sender === 'user' ? 'You' : 'Recurrence AI Tutor';
    const formattedHtml = formatChatMarkdown(text);

    let solveActionHtml = '';
    if (meta && meta.equation_solved && meta.recurrence) {
        solveActionHtml = `
            <div style="margin-top: 0.85rem;">
                <button type="button" class="btn-table-action" onclick="quickSolve('${meta.recurrence}', 'T(1) = 1')">
                    ⚡ Load ${meta.recurrence} in Solver
                </button>
            </div>`;
    }

    bubble.innerHTML = `
        <div class="bubble-avatar">${avatar}</div>
        <div class="bubble-body">
            <div class="bubble-author">${author}</div>
            <div class="bubble-text">${formattedHtml}${solveActionHtml}</div>
        </div>`;

    containerEl.appendChild(bubble);
    typesetMath(bubble);
}

/**
 * Formats basic Markdown and preserves LaTeX delimiters
 */
function formatChatMarkdown(raw) {
    if (!raw) return '';

    let text = raw
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    // Markdown Headers
    text = text.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    text = text.replace(/^## (.*$)/gim, '<h3>$1</h3>');

    // Bold
    text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

    // Inline Code
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Unordered lists
    text = text.replace(/^- (.*$)/gim, '• $1');

    // Line breaks
    text = text.replace(/\n/g, '<br>');

    return text;
}

/**
 * Typesets LaTeX mathematical expressions via KaTeX or MathJax
 */
function typesetMath(targetElement) {
    if (window.renderMathInElement) {
        try {
            window.renderMathInElement(targetElement, {
                delimiters: [
                    { left: '$$', right: '$$', display: true },
                    { left: '$', right: '$', display: false },
                    { left: '\\[', right: '\\]', display: true },
                    { left: '\\(', right: '\\)', display: false }
                ],
                throwOnError: false
            });
            return;
        } catch (e) {}
    }

    if (window.MathJax && window.MathJax.typesetPromise) {
        window.MathJax.typesetPromise([targetElement]).catch(() => {});
    }
}

/**
 * Auto-render on initial document load
 */
function initKaTeXAutoRender() {
    if (window.renderMathInElement) {
        try {
            window.renderMathInElement(document.body, {
                delimiters: [
                    { left: '$$', right: '$$', display: true },
                    { left: '$', right: '$', display: false },
                    { left: '\\[', right: '\\]', display: true },
                    { left: '\\(', right: '\\)', display: false }
                ],
                throwOnError: false
            });
        } catch (e) {}
    }
}

function scrollToBottom(el) {
    if (el) el.scrollTop = el.scrollHeight;
}
