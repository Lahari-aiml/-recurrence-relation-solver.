"""
AI DAA Tutor & Recurrence Relation Assistant.
Specialized for Design and Analysis of Algorithms (DAA) and the Substitution Method.
Supports full context-awareness of the active recurrence, base-case, derivation steps, and Big-Theta bounds.
"""

import re
import os
import json
import urllib.request
from solver.substitution import solve_recurrence, parse_recurrence, parse_base_case


SYSTEM_PROMPT = """You are a friendly DAA (Design and Analysis of Algorithms) professor and recurrence-relation tutor.
Your main purpose is to teach undergraduate B.Tech CSE/AIML students the substitution method for solving recurrence relations.
Explain concepts in simple, clear, B.Tech-level language.

When discussing a recurrence:
- Identify the recurrence form.
- Explain the base case.
- Show algebraic substitution clearly step-by-step.
- Explain the general k-th pattern.
- Explain how k is calculated to reach the base case.
- Explain the final closed form and Big-Theta complexity.
- Never skip important algebra.
- If the student asks why a specific step happened, explain that exact step with its algebraic justification.
- Do not confuse the substitution method with the Master Theorem.
- Keep equations properly formatted in LaTeX math notation ($...$ or $$...$$).
- Act like an encouraging, patient university lecturer helping a student prepare for a DAA viva or exam."""


# Knowledge base of core DAA & Substitution concepts
CONCEPT_KNOWLEDGE = {
    "substitution_method": {
        "title": "The Substitution (Iterative Expansion) Method",
        "content": r"""The **Substitution Method** (also called the *Unrolling* or *Iterative Expansion* method) solves recurrence relations through systematic algebraic steps:

1. **Repeated Expansion:** Substitute the recursive definition into itself for steps $1, 2, 3\dots$ to observe the emerging algebraic structure.
2. **General Pattern ($k$-th step):** Express $T(n)$ as a function of an arbitrary substitution step $k$, involving $T(n-k)$ or $T(n/b^k)$ along with the accumulated cost series.
3. **Base Case Reduction:** Set the subproblem size equal to the base case condition (e.g. $n - k = 1 \implies k = n - 1$, or $n/b^k = 1 \implies k = \log_b n$).
4. **Closed Form & Asymptotic Bound:** Substitute $k$ back into the $k$-th pattern formula, substitute the base case value $T(1)$, and determine the dominant $\Theta(\cdot)$ growth term."""
    },
    "base_case": {
        "title": "Role of the Base Case in Recurrence Relations",
        "content": r"""The **Base Case** (such as $T(1) = 1$ or $T(0) = c$) represents the stopping condition of the recursive algorithm:

- In the substitution method, we expand $T(n)$ until the inner argument reaches the base case index $n_0$.
- Setting the argument to the base case (e.g., $n - k = n_0$ or $n/b^k = n_0$) gives us the exact number of substitution steps $k$.
- Without a base case, recursion would continue indefinitely, and an exact closed-form equation cannot be evaluated."""
    },
    "big_theta": {
        "title": r"Big-Theta ($\Theta$) and Asymptotic Notations in DAA",
        "content": r"""In DAA, asymptotic notations describe how algorithm running time scales with input size $n$:

- **Big-Theta ($\Theta$):** Tight Bound. $f(n) = \Theta(g(n))$ means $f(n)$ is asymptotically bounded both from above and below by $c_1 g(n) \le f(n) \le c_2 g(n)$ for large $n$.
- **Big-O ($O$):** Asymptotic Upper Bound ($f(n) \le c \cdot g(n)$). Represents worst-case upper limit.
- **Big-Omega ($\Omega$):** Asymptotic Lower Bound ($f(n) \ge c \cdot g(n)$). Represents best-case lower limit.

In recurrence solving, because $T(n)$ is a deterministic mathematical equation, we state the exact tight growth rate using **$\Theta$**."""
    },
    "mathematical_induction": {
        "title": "Verifying Substitution with Mathematical Induction",
        "content": r"""Once a guess or closed-form is derived via iterative substitution, we can formally prove it using **Mathematical Induction**:

1. **Base Step:** Prove the formula holds for $n = n_0$ (e.g. $T(1) = 1$).
2. **Inductive Hypothesis:** Assume the formula holds for all values smaller than $n$ (e.g. $T(n-1)$ or $T(n/2)$).
3. **Inductive Step:** Substitute the inductive hypothesis into the original recurrence relation $T(n)$ and verify that it simplifies to the exact target formula."""
    }
}


def extract_recurrence_equation(text: str) -> str | None:
    """Extracts a recurrence relation expression like T(n) = ... from text."""
    pattern = r"[T|t]\(n\)\s*=\s*[^\n,;\?!]+"
    match = re.search(pattern, text)
    if match:
        return match.group(0).strip()
    
    simple_pattern = r"\b\d*\*?[T|t]\(n[/\-]\d+\)\s*[\+\-]\s*[\w\^\*]*"
    match_simple = re.search(simple_pattern, text)
    if match_simple:
        return f"T(n) = {match_simple.group(0).strip()}"
        
    return None


def generate_context_aware_explanation(user_msg: str, context: dict) -> str | None:
    """
    Generates intelligent pedagogical explanations using the current solved recurrence context.
    """
    if not context or not context.get("recurrence"):
        return None

    rec = context.get("recurrence", "")
    base = context.get("base_case", "T(1) = 1")
    exact = context.get("exact_solution", "")
    complexity = context.get("complexity", "")
    type_name = context.get("type_name", "")
    steps = context.get("steps", [])
    
    msg_low = user_msg.lower()

    # 1. Question: Why k = n-1 or how did we get k?
    if any(q in msg_low for q in ["why is k", "how did we get k", "how we got k", "why k =", "value of k", "what is k"]):
        if "n-" in rec or "-" in rec:
            return f"""Great question! Here is how we derived $k$ for **${rec}$**:

### 🎯 How $k$ is Calculated:
In the substitution method, each substitution step decreases the input size by 1:
- Step 1: $T(n-1)$
- Step 2: $T(n-2)$
- Step $k$: $T(n-k)$

To stop the recursive unrolling and evaluate the equation, the inner term must reach the base case argument **${base}$** (where input is $1$):
$$n - k = 1$$

Rearranging this algebraically gives:
$$k = n - 1$$

This means it takes exactly **$n - 1$ steps** of substitution to reduce problem size $n$ down to the base case $T(1)$!"""
        elif "n/" in rec or "/" in rec:
            return f"""Great question! Here is how we derived $k$ for **${rec}$**:

### 🎯 How $k$ is Calculated:
In divide-and-conquer recurrences, each substitution divides the problem size by $b$:
- Step 1: $T(n/b)$
- Step 2: $T(n/b^2)$
- Step $k$: $T(n/b^k)$

To evaluate the equation at the base case **${base}$** (where input size is $1$):
$$\\frac{{n}}{{b^k}} = 1 \\implies b^k = n$$

Taking the logarithm on both sides:
$$k = \\log_b n$$

This represents the depth of the recursion tree—it takes exactly **$\\log_b n$ levels** of division to reach base size 1."""

    # 2. Question: Why did we substitute n-1 or n/2?
    if any(q in msg_low for q in ["why did we substitute", "why substitute", "why n-1", "why n/2", "how substitution works"]):
        return f"""### 🔍 Why We Substitute in ${rec}$:

In the **Substitution Method**, the recurrence definition defines $T(n)$ in terms of smaller subproblems.

1. **Original Equation:** $${rec}$$
2. **Finding the Subproblem:** To find out what $T(n-1)$ or $T(n/b)$ equals, we replace $n$ everywhere in the formula with that smaller argument.
3. **Plugging Back In:** We substitute that expanded definition back into our equation for $T(n)$.

This unrolls the recurrence step-by-step so we can observe the mathematical pattern and eliminate the recursive $T(\\cdot)$ function completely!"""

    # 3. Question: Why is the complexity / answer Theta(...)
    if any(q in msg_low for q in ["why is the answer", "why theta", "why is complexity", "explain complexity", "why the complexity"]):
        return f"""### 📊 Complexity Analysis for ${rec}$:

- **Calculated Closed Form:** $${exact}$$
- **Final Asymptotic Bound:** **${complexity}$**

### 💡 Why this is the result:
1. In the closed-form expression $${exact}$$, we inspect the highest-order (fastest growing) term as $n \\to \\infty$.
2. Constant multipliers and lower-order terms become negligible compared to the dominant term.
3. Therefore, the tight asymptotic upper and lower bound is **${complexity}$**."""

    # 4. Question: Explain this recurrence simply / summarize
    if any(q in msg_low for q in ["explain this recurrence", "explain simply", "summary", "explain problem", "how to solve"]):
        return f"""### 🎓 Step-by-Step Overview of ${rec}$:

- **Recurrence:** ${rec}$
- **Base Case:** ${base}$
- **Classification:** {type_name}
- **Closed Form:** $${exact}$$
- **Complexity:** **${complexity}$**

### 📝 Key Takeaways for DAA Exam / Viva:
1. **Unrolling:** Each recursive step adds work while reducing problem size.
2. **Base Step:** After $k$ iterations, we hit the base condition ${base}$.
3. **Algebraic Sum:** Summing the work across all $k$ steps yields the closed form $${exact}$$, giving a tight bound of **${complexity}$**."""

    # 5. Question: What is the base case?
    if any(q in msg_low for q in ["base case", "what is base case", "what is the base"]):
        return f"""For your current problem **${rec}$**, the base case is **${base}$**.

### 💡 Why it matters:
- The base case provides the stopping condition where recursion terminates.
- When $n$ reduces to the base argument, $T(\\dots)$ is replaced by the constant value in ${base}$, allowing us to solve the algebraic equation."""

    return None


def get_ai_chat_response(user_message: str, history: list = None, context: dict = None) -> dict:
    """
    Processes student query with deep DAA and Substitution Method expertise.
    Incorporates active recurrence context and safely integrates external LLMs or internal knowledge engine.
    """
    user_msg_clean = user_message.strip() if user_message else ""
    if not user_msg_clean:
        return {
            "response": "Hello! I am your **DAA Recurrence AI Tutor**. Ask me any question about your recurrence relation or the substitution method.",
            "equation_solved": False
        }

    # 1. Context-aware question resolution if user has solved a recurrence on page
    if context and context.get("recurrence"):
        contextual_answer = generate_context_aware_explanation(user_msg_clean, context)
        if contextual_answer:
            return {
                "response": contextual_answer,
                "equation_solved": False,
                "context_used": True
            }

    # 2. Check if user typed a recurrence relation to solve directly in chat
    rec_eq = extract_recurrence_equation(user_msg_clean)
    if rec_eq:
        try:
            parsed = parse_recurrence(rec_eq)
            if parsed.get("type") not in ["INVALID", "UNSUPPORTED"]:
                sol = solve_recurrence(rec_eq, "T(1) = 1")
                if sol.get("supported"):
                    steps_preview = ""
                    for s in sol["steps"][:4]:
                        steps_preview += f"\n- **Step {s['number']}: {s['title']}**\n  $${s['equation']}$$\n  *{s['explanation']}*\n"
                    
                    response_text = f"""Here is the step-by-step substitution derivation for **${rec_eq}$**:

### 🎯 Substitution Result:
- **Tight Bound:** **${sol['complexity_latex']}$**
- **Exact Closed Form:** $${sol['exact_solution']}$$
- **Pattern Type:** {sol['type_name']}

---
### 📝 Expansion Steps Overview:
{steps_preview}
*(Full step-by-step proof with all cards is loaded in the main solver!)*"""
                    return {
                        "response": response_text,
                        "equation_solved": True,
                        "recurrence": rec_eq,
                        "complexity": sol["complexity"],
                        "exact_solution": sol["exact_solution"]
                    }
        except Exception:
            pass

    # 3. External LLM via Gemini API if key is available in environment
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            context_str = ""
            if context and context.get("recurrence"):
                context_str = f"Current active problem context: Recurrence: {context.get('recurrence')}, Base Case: {context.get('base_case')}, Exact Solution: {context.get('exact_solution')}, Complexity: {context.get('complexity')}."
            
            prompt = f"{SYSTEM_PROMPT}\n\n{context_str}\n\nStudent Question: {user_msg_clean}"
            payload = json.dumps({
                "contents": [{"parts": [{"text": prompt}]}]
            }).encode('utf-8')
            
            req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=7) as res:
                res_data = json.loads(res.read().decode('utf-8'))
                text_out = res_data['candidates'][0]['content']['parts'][0]['text']
                if text_out:
                    return {
                        "response": text_out,
                        "equation_solved": False
                    }
        except Exception:
            pass

    # 4. External LLM via OpenAI API if key is available in environment
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            context_str = ""
            if context and context.get("recurrence"):
                context_str = f"Current active problem context: Recurrence: {context.get('recurrence')}, Base Case: {context.get('base_case')}, Exact Solution: {context.get('exact_solution')}, Complexity: {context.get('complexity')}."

            messages = [
                {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{context_str}"}
            ]
            if history:
                for h in history[-4:]:
                    messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
            messages.append({"role": "user", "content": user_msg_clean})

            payload = json.dumps({
                "model": "gpt-4o-mini",
                "messages": messages,
                "temperature": 0.4
            }).encode('utf-8')

            req = urllib.request.Request(url, data=payload, headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {openai_key}'
            })
            with urllib.request.urlopen(req, timeout=7) as res:
                res_data = json.loads(res.read().decode('utf-8'))
                text_out = res_data['choices'][0]['message']['content']
                if text_out:
                    return {
                        "response": text_out,
                        "equation_solved": False
                    }
        except Exception:
            pass

    # 5. Core Concept Knowledge Base Fallback
    msg_low = user_msg_clean.lower()
    
    if any(k in msg_low for k in ["substitution method", "substitution", "how substitution works", "unrolling", "iterative method"]):
        return {
            "response": f"### {CONCEPT_KNOWLEDGE['substitution_method']['title']}\n\n{CONCEPT_KNOWLEDGE['substitution_method']['content']}",
            "equation_solved": False
        }

    if any(k in msg_low for k in ["base case", "t(1)", "t(0)", "stopping condition"]):
        return {
            "response": f"### {CONCEPT_KNOWLEDGE['base_case']['title']}\n\n{CONCEPT_KNOWLEDGE['base_case']['content']}",
            "equation_solved": False
        }

    if any(k in msg_low for k in ["big theta", "big o", "big omega", "asymptotic", "theta", "complexity", "notation"]):
        return {
            "response": f"### {CONCEPT_KNOWLEDGE['big_theta']['title']}\n\n{CONCEPT_KNOWLEDGE['big_theta']['content']}",
            "equation_solved": False
        }

    if any(k in msg_low for k in ["induction", "mathematical induction", "prove", "proof"]):
        return {
            "response": f"### {CONCEPT_KNOWLEDGE['mathematical_induction']['title']}\n\n{CONCEPT_KNOWLEDGE['mathematical_induction']['content']}",
            "equation_solved": False
        }

    if any(k in msg_low for k in ["example", "show example", "give example", "another example"]):
        return {
            "response": r"""Here are classic recurrence relation examples solved via the **Substitution Method**:

1. **Linear Decrement (Additive):**
   - $T(n) = T(n-1) + 5 \implies \Theta(n)$
2. **Divide and Conquer (Logarithmic):**
   - $T(n) = T(n/2) + 1 \implies \Theta(\log n)$ (Binary Search)
3. **Balanced Divide & Conquer (Linearithmic):**
   - $T(n) = 2T(n/2) + n \implies \Theta(n \log n)$ (MergeSort)
4. **Exponential Decrement:**
   - $T(n) = 2T(n-1) + 1 \implies \Theta(2^n)$ (Tower of Hanoi)
5. **Linear Growth Decrement:**
   - $T(n) = T(n-1) + n \implies \Theta(n^2)$ (Selection / Insertion Sort)

Click any example on the Home Page to load its complete step-by-step proof!""",
            "equation_solved": False
        }

    # Greeting / General Help
    if any(g in msg_low for g in ["hi", "hello", "hey", "who are you", "help", "what can you do", "tutor"]):
        return {
            "response": """Hello! 👋 I am your **DAA Recurrence AI Tutor**.

I'm here to help you master the **Substitution Method** for Design & Analysis of Algorithms:
- 💡 **Ask about any step:** *"Why did we substitute n-1?"*, *"How did we get k?"*, *"Why is the answer $\\Theta(n)$?"*
- ⚡ **Solve any recurrence:** Type an equation like `T(n) = 2T(n/2) + n` or `T(n) = T(n-1) + 5`.
- 📚 **Learn DAA concepts:** Ask about base cases, Big-Theta, geometric series, or induction proofs!

How can I help you with your algorithm analysis today?""",
            "equation_solved": False
        }

    return {
        "response": f"""I analyzed your question: *"{user_message}"*.

### 💡 Recurrence & Substitution Quick Help:
- **Solve a Recurrence:** Enter any equation in `T(n) = ...` format (e.g., `T(n) = 2T(n/2) + n`).
- **Understand Steps:** Ask *"Why is $k = n-1$?"* or *"Explain how substitution works"*.
- **DAA Viva Prep:** Ask *"What does Big-Theta mean?"* or *"What is the purpose of the base case?"*.""",
        "equation_solved": False
    }
