# Recurrence Relation Solver 🧮

A complete, responsive web application built with Python Flask, HTML5, CSS3, Vanilla JavaScript, and MathJax to solve recurrence relations step-by-step using the **Substitution Method**.

Built specifically for students learning **Design and Analysis of Algorithms (DAA)**.

---

## 🌟 Key Features

- **Step-by-Step Substitution Method:** Shows how equations expand substitution by substitution ($k$-th pattern, base case derivation, exact closed form, and asymptotic $\Theta$ complexity).
- **Beautiful Mathematical Rendering:** Uses MathJax v3 to render LaTeX equations cleanly.
- **Interactive Quick Presets:** Click example buttons ($T(n) = T(n-1)+5$, $T(n) = T(n/2)+1$, $T(n) = 2T(n/2)+n$, $T(n) = 2T(n-1)+1$) to auto-fill the form.
- **Dark / Light Theme:** Seamless toggle with `localStorage` memory.
- **Educational Context:** Explains asymptotic bounds without making false assumptions about best/average/worst cases for deterministic recurrence relations.
- **Printable Solution:** Includes `@media print` layout styles and a dedicated Print button.
- **No External JS Frameworks:** Built cleanly with native HTML5, vanilla CSS3, and JavaScript.

---

## 🛠️ Project Structure

```
recurrence-relation-solver/
│
├── app.py                     # Flask application entrypoint & routing
├── requirements.txt           # Dependency specifications
├── README.md                  # Project documentation
│
├── solver/                    # Core mathematical engine
│   ├── __init__.py
│   └── substitution.py        # Symbolic parser & substitution solver
│
├── templates/                 # Jinja2 HTML5 templates
│   ├── base.html              # Base layout & MathJax CDN setup
│   ├── index.html             # Hero section & solver input form
│   ├── solution.html          # Step-by-step solution breakdown
│   └── about.html             # Educational guide to recurrences
│
├── static/                    # Frontend static assets
│   ├── css/
│   │   └── style.css          # Theme system & UI styling
│   └── js/
│       └── script.js          # Theme toggle, form validation, presets
│
└── tests/                     # Test suite
    └── test_solver.py         # Unit tests for the substitution solver engine
```

---

## 🚀 How to Run Locally

### 1. Prerequisites
Ensure you have Python 3.9+ installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Unit Tests
```bash
python -m unittest discover -s tests
```

### 4. Start the Application
```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 💡 Supported Recurrence Types

1. **Linear Decrement Additive:**
   - Format: $T(n) = T(n-1) + c$
   - Example: `T(n) = T(n-1) + 5` $\implies \Theta(n)$

2. **Exponential Decrement Multiplicative:**
   - Format: $T(n) = a T(n-1) + c$
   - Example: `T(n) = 2T(n-1) + 1` $\implies \Theta(2^n)$

3. **Logarithmic Divide-and-Conquer:**
   - Format: $T(n) = T(n/b) + c$
   - Example: `T(n) = T(n/2) + 1` $\implies \Theta(\log n)$

4. **Linear Divide-and-Conquer (MergeSort Type):**
   - Format: $T(n) = a T(n/b) + c n$
   - Example: `T(n) = 2T(n/2) + n` $\implies \Theta(n \log n)$

5. **Branching Constant Divide-and-Conquer:**
   - Format: $T(n) = a T(n/b) + c$
   - Example: `T(n) = 2T(n/2) + 1` $\implies \Theta(n)$

---

## 📖 How the Substitution Method Works

Given $T(n) = T(n-1) + 5$ with $T(1) = 1$:

1. **Given:** $T(n) = T(n-1) + 5$
2. **First substitution:** $T(n-1) = T(n-2) + 5 \implies T(n) = T(n-2) + 10$
3. **Second substitution:** $T(n) = T(n-3) + 15$
4. **General pattern ($k$-th step):** $T(n) = T(n-k) + 5k$
5. **Reach base case:** $n - k = 1 \implies k = n - 1$
6. **Substitute $k$:** $T(n) = T(1) + 5(n-1)$
7. **Apply base case:** $T(n) = 1 + 5(n-1) = 5n - 4$
8. **Final Complexity:** $\Theta(n)$

---

## 🚀 Future Enhancements

- Support for Master Theorem & Recursion Tree visualizer diagrams.
- Extended support for non-linear non-recursive functions $f(n) = n^2, \log n$.
- Interactive step step-through slider animation.

---

## 📜 License
Built for educational purposes in Design and Analysis of Algorithms (DAA).
