"""
AI Recurrence Relation & Substitution Method Tutor.
Dedicated exclusively to teaching and explaining Recurrence Relations and the Step-by-Step Substitution Method.
Provides full context-awareness of the active recurrence, base-case, derivation steps, recursion depth, and asymptotic bounds.
"""

import re
import os
import json
import urllib.request
from solver.substitution import solve_recurrence, parse_recurrence, parse_base_case


SYSTEM_PROMPT = """You are a dedicated AI Tutor specializing strictly in Recurrence Relations and the Substitution Method.
Your role is to help students understand:
- Recurrence relations
- The Substitution Method (iterative unrolling and repeated expansion)
- Step-by-step mathematical substitution
- Base cases and stopping conditions
- Recursion depth and levels (k)
- Closed-form algebraic derivation
- Time complexity: Big-O (O), Big-Theta (Θ), and Big-Omega (Ω)
- Why a particular substitution step was performed
- Mathematical clarification of each derivation step

Guidelines:
- Explain concepts clearly, accurately, and step-by-step.
- Always use the Substitution Method only. Do not refer to Master Theorem or other unrelated methods.
- If an active recurrence problem context is provided, tailor your explanations directly to that specific recurrence relation and its substitution steps.
- If the user asks about a specific step (e.g. "Explain step 3" or "Why did 2 become 4?"), explain that exact algebraic transformation with complete mathematical reasoning.
- Format all mathematical equations properly in LaTeX ($...$ or $$...$$).
- Keep your tone friendly, encouraging, clear, and mathematically rigorous.
- Do NOT include exam preparation, GATE preparation, mock tests, or unrelated DSA topics."""


# Knowledge base of core Substitution Method concepts
CONCEPT_KNOWLEDGE = {
    "substitution_method": {
        "title": "The Substitution (Iterative Expansion) Method",
        "content": r"""The **Substitution Method** (also called *iterative expansion* or *unrolling*) solves recurrence relations through systematic algebraic steps:

1. **Step 1 — Write Original Recurrence:** State the recurrence relation $T(n)$ along with the base case $T(n_0) = b_0$.
2. **Step 2 — First Substitution:** Replace $T(n/b)$ or $T(n-c)$ with its recursive definition and substitute into $T(n)$.
3. **Step 3 — Expand Again:** Repeat the substitution for the next subproblem to establish the emerging algebraic pattern.
4. **Step 4 — General Pattern ($k$-th step):** Express $T(n)$ after an arbitrary $k$ substitutions as a function of $T(n/b^k)$ or $T(n-kc)$ plus the accumulated work series.
5. **Step 5 — Stopping Condition:** Set the subproblem argument equal to the base case index ($n/b^k = 1 \implies k = \log_b n$ or $n - kc = n_0 \implies k = \frac{n-n_0}{c}$).
6. **Step 6 — Substitute $k$ & Simplify:** Substitute $k$ and the base case value $T(n_0)$ back into the formula and evaluate the summation.
7. **Step 7 — Time Complexity:** Determine the tight asymptotic bound $\Theta(\cdot)$, Big-O ($O$), and Big-Omega ($\Omega$) from the closed-form expression."""
    },
    "base_case": {
        "title": "Base Cases and Stopping Conditions",
        "content": r"""The **Base Case** (such as $T(1) = 1$ or $T(0) = 1$) provides the termination boundary for the recursive process:

- In the substitution method, we expand $T(n)$ until the inner subproblem reaches the base case argument $n_0$.
- Setting the inner argument equal to $n_0$ (e.g. $n/b^k = n_0 \implies k = \log_b(n/n_0)$ or $n - kc = n_0 \implies k = \frac{n-n_0}{c}$) determines the total recursion depth $k$.
- Once $k$ is determined, replacing $T(n_0)$ with its known constant value allows us to convert the recurrence into a closed-form algebraic equation."""
    },
    "asymptotic_bounds": {
        "title": r"Time Complexity: Big-O, Big-Theta, and Big-Omega",
        "content": r"""Asymptotic notations characterize the growth rate of algorithm running time $T(n)$:

- **Big-Theta ($\Theta$):** Tight Bound. $T(n) = \Theta(g(n))$ means $T(n)$ is bounded both from above and below by $c_1 g(n) \le T(n) \le c_2 g(n)$ for large $n$.
- **Big-O ($O$):** Asymptotic Upper Bound ($T(n) \le c \cdot g(n)$).
- **Big-Omega ($\Omega$):** Asymptotic Lower Bound ($T(n) \ge c \cdot g(n)$).

In recurrence solving via the substitution method, because $T(n)$ is evaluated to an exact closed-form equation, we state the exact tight growth rate using **$\Theta$**."""
    }
}


def extract_recurrence_equation(text: str) -> str | None:
    """Extracts a recurrence relation expression like T(n) = ... from user text."""
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
    Generates intelligent explanations using the currently solved recurrence relation context.
    Handles specific step queries, coefficient explanations, stopping conditions, and complexity rationale.
    """
    if not context or not context.get("recurrence"):
        return None

    rec = context.get("recurrence", "")
    base = context.get("base_case", "T(1) = 1")
    exact = context.get("exact_solution", "")
    complexity = context.get("complexity", "")
    complexity_latex = context.get("complexity_latex", complexity)
    type_name = context.get("type_name", "")
    steps = context.get("steps", [])
    num_levels = context.get("num_levels", "")
    complexity_exp = context.get("complexity_explanation", "")

    msg_low = user_msg.lower()

    # 1. Question: Explain Step X (e.g., "Explain step 3", "step 2", "what happened in step 4")
    m_step = re.search(r"(?:explain|what (?:happened|is|about)|tell me about)\s*(?:in\s*)?step\s*(\d+)", msg_low)
    if not m_step:
        m_step = re.search(r"step\s*(\d+)", msg_low)
    if m_step:
        step_num = int(m_step.group(1))
        matching_step = next((s for s in steps if s.get("number") == step_num), None)
        if matching_step:
            return f"""### 🔍 Explanation of Step {matching_step['number']}: {matching_step['title']}

**For Recurrence:** $${rec}$$

**Equation in Step {step_num}:**
$${matching_step['equation']}$$

**Explanation:**
{matching_step['explanation']}

---
💡 **Why this step was done:**
In the Substitution Method, each step either unrolls a recursive term by substituting its definition, establishes the generalized $k$-th pattern, solves for the stopping condition ($k$), or evaluates the final summation to determine the closed-form complexity."""

    # 2. Question: Why did 2 become 4? / Why did coefficient multiply?
    if any(q in msg_low for q in ["why did 2 become 4", "why 2 became 4", "why 4", "why 8", "coefficient multiply", "why did it double", "why subproblems double"]):
        return f"""### 💡 Why the Coefficient Multiplies in ${rec}$:

When substituting a recursive subproblem back into the equation:
1. **Original equation:** $${rec}$$
2. In the first step, there is an outer coefficient (for example, $2$).
3. When we substitute the definition of the subproblem (e.g. $T(n/2) = 2T(n/4) + \\dots$), that inner term ALSO has a factor of $2$.
4. Distributing the outer $2$ across the bracket gives:
$$2 \\times [2T(n/4) + \\dots] = 4T(n/4) + \\dots$$
5. In the next substitution, $2 \\times 4 = 8$, yielding $8T(n/8)$, and after $k$ steps it becomes $2^k T(n/2^k)$.

Each substitution level multiplies the number of subproblems by the branching factor!"""

    # 3. Question: Why did we substitute n/2 or n-1?
    if any(q in msg_low for q in ["why did you substitute", "why did we substitute", "why substitute", "why n/2", "why n-1", "why n/3", "why substitute n/2", "why substitute n-1"]):
        return f"""### 🔍 Why We Substitute in ${rec}$:

In the **Substitution Method**, the relation defines $T(n)$ in terms of smaller subproblems.

1. **Original Equation:** $${rec}$$
2. **Finding the Subproblem Value:** To determine what the inner recursive call equals, we replace $n$ everywhere in the original definition with the smaller input size (such as $n/2$ or $n-1$).
3. **Plugging Back In:** We substitute that algebraic formula back into $T(n)$.

This repeated unrolling eliminates the recursive $T(\\cdot)$ terms and converts the recurrence into an algebraic summation that we can solve directly."""

    # 4. Question: How did we get k / Why is k = ... / Stopping condition
    if any(q in msg_low for q in ["why is k", "how did we get k", "how we got k", "why k =", "value of k", "what is k", "stopping condition", "recursion depth", "levels"]):
        if "/" in rec or "div" in type_name.lower():
            return f"""### 🎯 How $k$ is Calculated for ${rec}$:

In divide-and-conquer recurrences, each substitution divides the problem size by $b$:
- Step 1: $T(n/b)$
- Step 2: $T(n/b^2)$
- Step $k$: $T(n/b^k)$

To reach the base case **${base}$** (where input size is $1$):
$$\\frac{{n}}{{b^k}} = 1 \\implies b^k = n$$

Taking the logarithm with base $b$ on both sides:
$$k = \\log_b n$$

This gives the total recursion depth—it takes exactly **$\\log_b n$ levels** of division to reach the base case."""
        else:
            return f"""### 🎯 How $k$ is Calculated for ${rec}$:

In decrement recurrences, each substitution decreases the problem size by the step size:
- Step 1: $T(n-1)$
- Step 2: $T(n-2)$
- Step $k$: $T(n-k)$

To stop the recursive unrolling at the base case **${base}$** (where input is $1$):
$$n - k = 1 \\implies k = n - 1$$

This means it takes exactly **$n - 1$ substitutions** to reduce the problem size from $n$ down to base case $T(1)$."""

    # 5. Question: Why is the answer ... / Why complexity ...
    if any(q in msg_low for q in ["why is the answer", "why theta", "why is complexity", "explain complexity", "why the complexity", "why n log n", "why n^2", "why log n"]):
        exp_text = complexity_exp if complexity_exp else f"The dominant term in the closed form $${exact}$$ is **${complexity_latex}$**."
        return f"""### 📊 Time Complexity Explanation for ${rec}$:

- **Calculated Closed Form:** $${exact}$$
- **Tight Asymptotic Bound:** **${complexity_latex}$**
- **Number of Levels:** ${num_levels}$

### 💡 Why this complexity is obtained:
{exp_text}"""

    # 6. Question: Explain this recurrence simply / summarize
    if any(q in msg_low for q in ["explain this recurrence", "explain simply", "summary", "explain problem", "overview", "walk me through"]):
        return f"""### 🎓 Overview of ${rec}$:

- **Recurrence:** $${rec}$$
- **Base Case:** $${base}$$
- **Number of Levels:** ${num_levels}$
- **Exact Closed Form:** $${exact}$$
- **Time Complexity:** **${complexity_latex}$**

### 📝 Step-by-Step Summary:
1. **Unrolling:** Each substitution replaces the inner recursive call with its definition.
2. **General Form:** After $k$ steps, the formula is expressed in terms of $k$ and the base subproblem.
3. **Base Case:** Reaching the base case gives the substitution depth $k$.
4. **Closed Form:** Substituting $k$ and evaluating the work across all levels gives the exact closed form $${exact}$$, which simplifies to **${complexity_latex}$**."""

    # 7. Question: What is the base case?
    if any(q in msg_low for q in ["what is base case", "what is the base case", "base case role", "why base case"]):
        return f"""For your current problem **${rec}$**, the base case is **${base}$**.

### 💡 Importance of the Base Case:
- The base case specifies the stopping condition where recursion terminates.
- Setting the subproblem argument equal to the base index allows us to calculate the exact recursion depth $k$.
- Substituting the base case constant value eliminates the recursive $T(\\cdot)$ term and produces the exact closed form."""

    return None


def get_ai_chat_response(user_message: str, history: list = None, context: dict = None) -> dict:
    """
    Processes user queries with dedicated Recurrence Relation & Substitution Method expertise.
    Incorporates active recurrence context and safely integrates external LLMs or internal knowledge engine.
    """
    user_msg_clean = user_message.strip() if user_message else ""
    if not user_msg_clean:
        return {
            "response": "Hello! I am your **Recurrence Relation & Substitution Method Tutor**. Ask me any question about your recurrence relation or substitution steps.",
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
- **Number of Levels:** ${sol['num_levels']}$
- **Applied Method:** Substitution Method

---
### 📝 Expansion Steps:
{steps_preview}
*(You can load the full step-by-step solution cards into the main solver!)*"""
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
                context_str = f"Current active problem context: Recurrence: {context.get('recurrence')}, Base Case: {context.get('base_case')}, Exact Solution: {context.get('exact_solution')}, Complexity: {context.get('complexity')}, Steps: {json.dumps(context.get('steps', []))}."

            prompt = f"{SYSTEM_PROMPT}\n\n{context_str}\n\nUser Question: {user_msg_clean}"
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
                context_str = f"Current active problem context: Recurrence: {context.get('recurrence')}, Base Case: {context.get('base_case')}, Exact Solution: {context.get('exact_solution')}, Complexity: {context.get('complexity')}, Steps: {json.dumps(context.get('steps', []))}."

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
                "temperature": 0.3
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

    if any(k in msg_low for k in ["base case", "t(1)", "t(0)", "stopping condition", "boundary"]):
        return {
            "response": f"### {CONCEPT_KNOWLEDGE['base_case']['title']}\n\n{CONCEPT_KNOWLEDGE['base_case']['content']}",
            "equation_solved": False
        }

    if any(k in msg_low for k in ["big theta", "big o", "big omega", "asymptotic", "theta", "complexity", "notation"]):
        return {
            "response": f"### {CONCEPT_KNOWLEDGE['asymptotic_bounds']['title']}\n\n{CONCEPT_KNOWLEDGE['asymptotic_bounds']['content']}",
            "equation_solved": False
        }

    if any(k in msg_low for k in ["example", "show example", "give example", "another example"]):
        return {
            "response": r"""Here are classic recurrence relations solved via the **Substitution Method**:

1. **Linear Decrement:**
   - $T(n) = T(n-1) + 1 \implies \Theta(n)$
2. **Divide and Conquer (Logarithmic):**
   - $T(n) = T(n/2) + 1 \implies \Theta(\log n)$
3. **Balanced Divide & Conquer (Linearithmic):**
   - $T(n) = 2T(n/2) + n \implies \Theta(n \log n)$
4. **Exponential Decrement:**
   - $T(n) = 2T(n-1) + 1 \implies \Theta(2^n)$
5. **Linear Growth Decrement:**
   - $T(n) = T(n-1) + n \implies \Theta(n^2)$
6. **Linearithmic Divide & Conquer:**
   - $T(n) = 2T(n/2) + n \log n \implies \Theta(n \log^2 n)$

Click any example on the Home Page to view its full step-by-step substitution proof!""",
            "equation_solved": False
        }

    # Greeting / General Help
    if any(g in msg_low for g in ["hi", "hello", "hey", "who are you", "help", "what can you do", "tutor"]):
        return {
            "response": """Hello! 👋 I am your **Recurrence AI Tutor**.

I specialize in the **Substitution Method** for solving recurrence relations:
- 💡 **Ask about any step:** *"Why did we substitute n/2?"*, *"Explain step 3"*, *"Why did 2 become 4?"*, *"How did we get k?"*
- ⚡ **Solve any recurrence:** Type an equation like `T(n) = 2T(n/2) + n` or `T(n) = T(n-1) + 1`.
- 📚 **Learn substitution concepts:** Ask about base cases, stopping conditions, geometric series unrolling, or Big-Theta bounds!

How can I help you with your recurrence relation today?""",
            "equation_solved": False
        }

    return {
        "response": f"""I analyzed your question: *"{user_message}"*.

### 💡 Recurrence & Substitution Quick Help:
- **Solve a Recurrence:** Enter any equation in `T(n) = ...` format (e.g., `T(n) = 2T(n/2) + n`).
- **Understand Steps:** Ask *"Why did we substitute n/2?"*, *"Explain step 2"*, or *"Why is the answer $\\Theta(n \\log n)$?"*.
- **Concepts:** Ask *"What is the stopping condition?"* or *"What is Big-Theta?"*.""",
        "equation_solved": False
    }
