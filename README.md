# Recurrence Relation Solver — AI-Powered Substitution Method Tutor 🧮

A modern, educational web application built for B.Tech CSE / AIML students studying **Design and Analysis of Algorithms (DAA)** to master solving recurrence relations using the **Step-by-Step Substitution Method**.

---

## 🌟 Key Features

- **Strict Focus on Substitution Method:** Pure algebraic iterative expansion / unrolling derivations with mathematical accuracy.
- **Academic Theme:** Warm dark graphite/charcoal study desk theme (`#171717`, `#292722`, `#F5F0E6`, `#D6A84F`) with subtle floating mathematical background particles.
- **Multi-Form Recurrence Parser & Solver:** Dynamically handles linear decrements ($T(n-1)+c$, $T(n-1)+n$, $T(n-1)+n^2$), arbitrary step decrements ($T(n-k)+c$), exponential decrements ($aT(n-1)+c$), and divide-and-conquer recurrences ($aT(n/b)+c$, $aT(n/b)+f(n)$).
- **True Step-by-Step Mathematical Derivations:**
  1. Given Recurrence & Base Case
  2. First Substitution
  3. Second / Third Substitution
  4. General $k$-th Pattern
  5. Base-Case Condition ($k = n - 1$ or $k = \log_b n$)
  6. Closed-Form Evaluation
  7. Big-Theta ($\Theta$) Tight Bound
- **AI DAA Tutor Assistant:**
  - Context-aware chatbot that understands the current active recurrence and step derivations.
  - Answers B.Tech student questions such as *"Why is k = n-1?"*, *"Why did we substitute n-1?"*, and *"Why is the complexity $\Theta(n)$?"*.
  - Safe backend routing with fallback knowledge base and optional `GEMINI_API_KEY` / `OPENAI_API_KEY` integration.
- **Categorized Examples & Quick Matrix:**
  - Basic ($T(n-1)+1$, $T(n-1)+5$)
  - Divide & Conquer ($T(n/2)+1$, $2T(n/2)+n$, $4T(n/2)+n$, $3T(n/2)+n$)
  - Linear Growth ($T(n-1)+n$, $T(n-2)+3$)
  - Exponential ($2T(n-1)+1$)
- **KaTeX & MathJax Equation Typesetting:** Crystal-clear mathematical notation.
- **Student Actions:** Copy Equation, Copy Solution, Print Friendly Stylesheet (`@media print`), and keyboard-friendly shortcuts (Enter to solve).

---

## 🛠️ Project Structure

```
recurrence-relation-solver/
│
├── app.py                     # Flask application entrypoint & API routes (/solve, /api/chat, /api/solve)
├── requirements.txt           # Dependency specifications
├── vercel.json                # Vercel serverless deployment config
├── render.yaml                # Render deployment configuration
├── README.md                  # Project documentation
│
├── solver/                    # Core Mathematical & AI Tutor Engine
│   ├── __init__.py
│   ├── substitution.py        # Generalized substitution solver & pattern parser
│   └── ai_chatbot.py          # Context-aware AI DAA Tutor with knowledge base
│
├── templates/                 # Jinja2 HTML5 Templates
│   ├── base.html              # Academic dark layout, canvas, KaTeX CDN & AI Tutor modal
│   ├── index.html             # Hero, solver card, categorized examples, 6-step guide, matrix table
│   ├── solution.html          # Step-by-Step solution cards & final result summary
│   └── about.html             # B.Tech DAA study notes on substitution method
│
├── static/                    # Frontend Static Assets
│   ├── css/
│   │   └── style.css          # Warm academic dark theme, glassmorphism cards & responsive rules
│   └── js/
│       └── script.js          # Math canvas animation, preset loaders, KaTeX render, AI tutor client
│
└── tests/                     # Automated Test Suite
    ├── test_solver.py         # Unit tests for substitution solver engine
    └── test_chatbot.py        # Unit tests for AI Tutor and API endpoints
```

---

## 🚀 How to Run Locally

### 1. Prerequisites
Python 3.9 or higher.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Automated Tests
```bash
python -m unittest discover tests
```

### 4. Start the Application
```bash
python app.py
```
Open your browser at `http://127.0.0.1:5000`.

---

## 📜 License
Built for educational purposes in Design and Analysis of Algorithms (DAA).
