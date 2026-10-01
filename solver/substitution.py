"""
Substitution Method Solver Engine for Recurrence Relations.
Designed for B.Tech CSE / AIML Algorithm Design and Analysis (DAA).
Supports step-by-step unrolling/substitution for common recurrence relation forms:
1. T(n) = T(n-1) + c
2. T(n) = T(n-1) + f(n) (e.g., + n, + n^2, + n^3)
3. T(n) = a*T(n-1) + c (e.g., 2T(n-1) + 1)
4. T(n) = a*T(n-1) + f(n) (e.g., 2T(n-1) + n)
5. T(n) = T(n-k) + c or + f(n) (e.g., T(n-2) + 3)
6. T(n) = T(n/b) + c (e.g., T(n/2) + 1)
7. T(n) = a*T(n/b) + c (e.g., 2T(n/2) + 1)
8. T(n) = a*T(n/b) + f(n) (e.g., 2T(n/2) + n, 3T(n/2) + n, 4T(n/2) + n, T(n/2) + n, 2T(n/2) + n^2, etc.)
"""

import re
import math


def parse_base_case(base_str: str) -> tuple[int, int]:
    """
    Parses base case string like 'T(1) = 1', 'T(0) = 0', 'T(1) = 5'.
    Returns (n0, T_n0). Defaults to (1, 1).
    """
    if not base_str or not base_str.strip():
        return (1, 1)

    cleaned = base_str.replace(" ", "")
    # Pattern: T(n0) = b0
    match = re.search(r"[T|t]\((\d+)\)\=(\-?\d+)", cleaned)
    if match:
        return (int(match.group(1)), int(match.group(2)))

    # Just a single integer
    if cleaned.lstrip("-").isdigit():
        return (1, int(cleaned))

    return (1, 1)


def parse_fn_term(term_str: str) -> dict:
    """
    Parses non-recursive cost term f(n).
    Supports:
    - Constants: '5', '1', '0'
    - Linear: 'n', '2n', '5*n'
    - Polynomial: 'n^2', 'n^3', '2n^2', 'n**2'
    - Logarithmic: 'log n', 'logn', 'log2(n)', 'log(n)'
    - Linearithmic: 'n log n', 'nlogn', 'n*log(n)'
    """
    s = term_str.strip()
    if not s:
        return {"type": "const", "coeff": 0, "deg": 0, "raw": "0"}

    # Remove multiplication symbols like 2*n -> 2n
    s_norm = s.replace("*", "").replace(" ", "").lower()

    # Pure integer constant
    if s_norm.isdigit() or (s_norm.startswith("-") and s_norm[1:].isdigit()):
        return {"type": "const", "coeff": int(s_norm), "deg": 0, "raw": s}

    # Linearithmic n log n
    m_nlogn = re.fullmatch(r"(\d*)nlog(?:2)?(?:\(n\)|n)?", s_norm)
    if m_nlogn:
        c = int(m_nlogn.group(1)) if m_nlogn.group(1) else 1
        return {"type": "n_log_n", "coeff": c, "deg": 1, "raw": s}

    # Logarithmic log n
    m_logn = re.fullmatch(r"(\d*)log(?:2)?(?:\(n\)|n)?", s_norm)
    if m_logn:
        c = int(m_logn.group(1)) if m_logn.group(1) else 1
        return {"type": "log_n", "coeff": c, "deg": 0, "raw": s}

    # Polynomial / Linear: e.g. n, 2n, n^2, 3n^2, n^3, n**2
    m_poly = re.fullmatch(r"(\d*)n(?:\^|\*\*)?(\d*)", s_norm)
    if m_poly:
        c = int(m_poly.group(1)) if m_poly.group(1) else 1
        d = int(m_poly.group(2)) if m_poly.group(2) else 1
        return {"type": "poly", "coeff": c, "deg": d, "raw": s}

    return {"type": "custom", "coeff": 1, "deg": 1, "raw": s}


def parse_recurrence(rec_str: str) -> dict:
    """
    Parses a recurrence relation into structured mathematical components.
    Handles variations in spacing, casing, and operator notation.
    """
    if not rec_str or not rec_str.strip():
        return {"type": "INVALID", "error": "Please enter a recurrence relation."}

    # Normalize string: remove all spaces, normalize symbols
    s = rec_str.replace(" ", "").replace("*", "")
    if "=" in s:
        lhs, rhs = s.split("=", 1)
    else:
        rhs = s

    # Match recursive part and non-recursive part:
    # Form: a*T(subproblem) +/- f(n)
    # Examples:
    # 2T(n/2)+n
    # T(n-1)+5
    # T(n-1)+n
    # 2T(n-1)+1
    # 3T(n/2)+n^2
    # T(n-2)+3

    # Pattern for decrement: a*T(n-k) + rest
    m_dec = re.fullmatch(r"(\d*)[T|t]\(n\-(\d+)\)(?:([\+\-])(.+))?", rhs)
    if m_dec:
        a = int(m_dec.group(1)) if m_dec.group(1) else 1
        k_step = int(m_dec.group(2))
        sign = m_dec.group(3) or "+"
        rest = m_dec.group(4) if m_dec.group(4) else "0"
        
        fn = parse_fn_term(rest)
        if sign == "-":
            fn["coeff"] = -fn["coeff"]

        return {
            "type": "DECREMENT",
            "a": a,
            "k_step": k_step,
            "fn": fn,
            "raw_rhs": rhs
        }

    # Pattern for divide-and-conquer: a*T(n/b) + rest
    m_div = re.fullmatch(r"(\d*)[T|t]\(n\/(\d+)\)(?:([\+\-])(.+))?", rhs)
    if m_div:
        a = int(m_div.group(1)) if m_div.group(1) else 1
        b = int(m_div.group(2))
        sign = m_div.group(3) or "+"
        rest = m_div.group(4) if m_div.group(4) else "0"

        fn = parse_fn_term(rest)
        if sign == "-":
            fn["coeff"] = -fn["coeff"]

        return {
            "type": "DIVIDE",
            "a": a,
            "b": b,
            "fn": fn,
            "raw_rhs": rhs
        }

    return {
        "type": "UNSUPPORTED",
        "error": "Could not parse this recurrence. Please check syntax (e.g., T(n) = 2T(n/2) + n or T(n) = T(n-1) + 5)."
    }


def solve_recurrence(rec_str: str, base_str: str = "T(1) = 1") -> dict:
    """
    Main entry point for solving recurrence relations using the Substitution Method.
    Generates structured, mathematically accurate step-by-step substitution derivation.
    """
    if not rec_str or not rec_str.strip():
        return {
            "supported": False,
            "error_message": "Please enter a recurrence relation.",
            "suggested_examples": [
                "T(n) = T(n-1) + 5",
                "T(n) = T(n/2) + 1",
                "T(n) = 2T(n/2) + n",
                "T(n) = 2T(n-1) + 1",
                "T(n) = T(n-1) + n",
                "T(n) = 3T(n/2) + n"
            ]
        }

    parsed = parse_recurrence(rec_str)
    if parsed.get("type") in ["INVALID", "UNSUPPORTED"]:
        return {
            "supported": False,
            "error_message": parsed.get("error", "Unsupported recurrence relation format."),
            "suggested_examples": [
                "T(n) = T(n-1) + 5",
                "T(n) = T(n/2) + 1",
                "T(n) = 2T(n/2) + n",
                "T(n) = 2T(n-1) + 1",
                "T(n) = T(n-1) + n",
                "T(n) = 3T(n/2) + n"
            ]
        }

    n0, b0 = parse_base_case(base_str)
    rec_type = parsed["type"]

    if rec_type == "DECREMENT":
        return _solve_decrement(parsed["a"], parsed["k_step"], parsed["fn"], n0, b0, rec_str, base_str)
    elif rec_type == "DIVIDE":
        return _solve_divide(parsed["a"], parsed["b"], parsed["fn"], n0, b0, rec_str, base_str)

    return {
        "supported": False,
        "error_message": "This recurrence is outside the currently supported substitution patterns.",
        "suggested_examples": [
            "T(n) = T(n-1) + 5",
            "T(n) = T(n/2) + 1",
            "T(n) = 2T(n/2) + n",
            "T(n) = 2T(n-1) + 1",
            "T(n) = T(n-1) + n",
            "T(n) = 3T(n/2) + n"
        ]
    }


def _format_poly_term(coeff: int, deg: int) -> str:
    """Formats polynomial term coeff * n^deg for LaTeX."""
    if coeff == 0:
        return ""
    
    sign_str = " + " if coeff > 0 else " - "
    abs_c = abs(coeff)
    c_str = "" if (abs_c == 1 and deg > 0) else str(abs_c)
    
    if deg == 0:
        return f"{coeff}" if coeff < 0 else f"+ {coeff}"
    elif deg == 1:
        return f"{c_str}n"
    else:
        return f"{c_str}n^{deg}"


def _solve_decrement(a: int, step: int, fn: dict, n0: int, b0: int, rec_str: str, base_str: str) -> dict:
    """
    Handles recurrences of the form:
    T(n) = a*T(n - step) + f(n)
    """
    fn_type = fn["type"]
    c = fn.get("coeff", 1)
    deg = fn.get("deg", 0)

    # 1. T(n) = T(n-1) + c (Linear Decrement Additive)
    if a == 1 and step == 1 and fn_type == "const":
        c_val = c
        c_str = f" + {c_val}" if c_val > 0 else (f" - {abs(c_val)}" if c_val < 0 else "")
        c2_str = f" + {2*c_val}" if c_val > 0 else (f" - {2*abs(c_val)}" if c_val < 0 else "")
        c3_str = f" + {3*c_val}" if c_val > 0 else (f" - {3*abs(c_val)}" if c_val < 0 else "")
        ck_str = f" + {c_val}k" if c_val > 0 else (f" - {abs(c_val)}k" if c_val < 0 else "")

        slope = c_val
        intercept = b0 - c_val * n0
        if slope == 1:
            exact_str = f"n + {intercept}" if intercept > 0 else (f"n - {abs(intercept)}" if intercept < 0 else "n")
        elif slope == 0:
            exact_str = f"{b0}"
        else:
            if intercept > 0:
                exact_str = f"{slope}n + {intercept}"
            elif intercept < 0:
                exact_str = f"{slope}n - {abs(intercept)}"
            else:
                exact_str = f"{slope}n"

        steps = [
            {
                "number": 1,
                "title": "Given Recurrence",
                "equation": f"T(n) = T(n-1){c_str}",
                "explanation": f"Write down the given recurrence relation and base case $T({n0}) = {b0}$."
            },
            {
                "number": 2,
                "title": "First Substitution",
                "equation": f"T(n-1) = T(n-2){c_str} \\\\\n\\implies T(n) = [T(n-2){c_str}]{c_str} = T(n-2){c2_str}",
                "explanation": f"Substitute $T(n-1)$ back into the original relation for $T(n)$."
            },
            {
                "number": 3,
                "title": "Second Substitution",
                "equation": f"T(n-2) = T(n-3){c_str} \\\\\n\\implies T(n) = [T(n-3){c_str}]{c2_str} = T(n-3){c3_str}",
                "explanation": "Substitute $T(n-2)$ to observe how the additive constant accumulates."
            },
            {
                "number": 4,
                "title": "General Pattern (k-th step)",
                "equation": f"T(n) = T(n-k){ck_str}",
                "explanation": f"Generalize the equation after $k$ iterative substitutions in terms of $T(n-k)$ and $k$."
            },
            {
                "number": 5,
                "title": "Reach Base Case",
                "equation": f"n - k = {n0} \\implies k = n - {n0}",
                "explanation": f"Determine the number of substitutions $k$ required to reach the base case $T({n0})$."
            },
            {
                "number": 6,
                "title": "Substitute k & Apply Base Case",
                "equation": f"T(n) = T({n0}){f' + {c_val}(n - {n0})' if c_val != 0 else ''} \\\\\n\\text{{Since }} T({n0}) = {b0}: \\\\\nT(n) = {b0}{f' + {c_val}(n - {n0})' if c_val != 0 else ''} = {exact_str}",
                "explanation": f"Substitute $k = n - {n0}$ and replace $T({n0})$ with ${b0}$, then simplify algebraically."
            },
            {
                "number": 7,
                "title": "Final Complexity",
                "equation": "\\Theta(n)",
                "explanation": f"The dominant term in the closed form $T(n) = {exact_str}$ is linear in $n$, yielding a tight bound of $\\Theta(n)$."
            }
        ]

        return {
            "supported": True,
            "recurrence": rec_str,
            "base_case": f"T({n0}) = {b0}",
            "type_name": "Linear Decrement (Additive Constant)",
            "steps": steps,
            "exact_solution": f"T(n) = {exact_str}",
            "complexity": "Θ(n)",
            "complexity_latex": "\\Theta(n)",
            "method": "Substitution Method"
        }

    # 2. T(n) = T(n-1) + n or T(n-1) + c*n (Linear Growth Decrement e.g. Insertion Sort / Selection Sort)
    if a == 1 and step == 1 and fn_type == "poly" and deg == 1:
        c_n = f"{c}n" if c != 1 else "n"
        c_n_minus_1 = f"{c}(n-1)" if c != 1 else "(n-1)"
        c_n_minus_2 = f"{c}(n-2)" if c != 1 else "(n-2)"

        steps = [
            {
                "number": 1,
                "title": "Given Recurrence",
                "equation": f"T(n) = T(n-1) + {c_n}",
                "explanation": f"State the linear-growth recurrence with base case $T({n0}) = {b0}$."
            },
            {
                "number": 2,
                "title": "First Substitution",
                "equation": f"T(n-1) = T(n-2) + {c_n_minus_1} \\\\\n\\implies T(n) = T(n-2) + {c_n_minus_1} + {c_n}",
                "explanation": f"Substitute $T(n-1)$ into $T(n)$ to reveal the arithmetic progression."
            },
            {
                "number": 3,
                "title": "Second Substitution",
                "equation": f"T(n-2) = T(n-3) + {c_n_minus_2} \\\\\n\\implies T(n) = T(n-3) + {c_n_minus_2} + {c_n_minus_1} + {c_n}",
                "explanation": "Substitute $T(n-2)$ to confirm the summing series."
            },
            {
                "number": 4,
                "title": "General Pattern (k-th step)",
                "equation": f"T(n) = T(n-k) + {c if c != 1 else ''} \\sum_{{i=0}}^{{k-1}} (n - i)",
                "explanation": f"Express $T(n)$ after $k$ steps as $T(n-k)$ plus the sum of the first $k$ terms of the arithmetic progression."
            },
            {
                "number": 5,
                "title": "Reach Base Case",
                "equation": f"n - k = {n0} \\implies k = n - {n0}",
                "explanation": f"Set the inner subproblem equal to base index ${n0}$, giving $k = n - {n0}$."
            },
            {
                "number": 6,
                "title": "Substitute k & Apply Base Case",
                "equation": f"T(n) = T({n0}) + {c if c != 1 else ''} \\sum_{{i={n0}+1}}^{{n}} i = {b0} + {c if c != 1 else ''} \\left[ \\frac{{n(n+1)}}{{2}} - \\frac{{{n0}({n0}+1)}}{{2}} \\right]",
                "explanation": f"Using the Gaussian summation formula $\\sum_{{i=1}}^n i = \\frac{{n(n+1)}}{{2}}$, substitute $T({n0}) = {b0}$ and simplify."
            },
            {
                "number": 7,
                "title": "Final Complexity",
                "equation": "\\Theta(n^2)",
                "explanation": "The highest order term is quadratic ($\\frac{1}{2}n^2$), giving a tight asymptotic bound of $\\Theta(n^2)$."
            }
        ]

        exact_str = f"\\frac{{{c}n^2 + {c}n}}{{2}} + {b0 - c*n0*(n0+1)//2}" if c != 1 else f"\\frac{{n(n+1)}}{{2}}"

        return {
            "supported": True,
            "recurrence": rec_str,
            "base_case": f"T({n0}) = {b0}",
            "type_name": "Linear Growth Decrement Recurrence",
            "steps": steps,
            "exact_solution": f"T(n) = {exact_str}",
            "complexity": "Θ(n²)",
            "complexity_latex": "\\Theta(n^2)",
            "method": "Substitution Method"
        }

    # 3. T(n) = T(n-1) + c*n^2 (Quadratic Growth Decrement)
    if a == 1 and step == 1 and fn_type == "poly" and deg == 2:
        steps = [
            {
                "number": 1,
                "title": "Given Recurrence",
                "equation": f"T(n) = T(n-1) + {c if c != 1 else ''}n^2",
                "explanation": f"State the given recurrence and base case $T({n0}) = {b0}$."
            },
            {
                "number": 2,
                "title": "First Substitution",
                "equation": f"T(n-1) = T(n-2) + {c if c != 1 else ''}(n-1)^2 \\\\\n\\implies T(n) = T(n-2) + {c if c != 1 else ''}(n-1)^2 + {c if c != 1 else ''}n^2",
                "explanation": "Substitute $T(n-1)$ into $T(n)$."
            },
            {
                "number": 3,
                "title": "General Pattern (k-th step)",
                "equation": f"T(n) = T(n-k) + {c if c != 1 else ''} \\sum_{{i=0}}^{{k-1}} (n-i)^2",
                "explanation": f"Generalize after $k$ substitutions as the sum of consecutive squares."
            },
            {
                "number": 4,
                "title": "Reach Base Case",
                "equation": f"n - k = {n0} \\implies k = n - {n0}",
                "explanation": f"Calculate the number of steps to reach base condition $T({n0})$."
            },
            {
                "number": 5,
                "title": "Summation Formula & Closed Form",
                "equation": f"T(n) = T({n0}) + {c if c != 1 else ''} \\sum_{{i={n0}+1}}^{{n}} i^2 \\\\\n\\text{{Using }} \\sum_{{i=1}}^n i^2 = \\frac{{n(n+1)(2n+1)}}{{6}}: \\\\\nT(n) = {b0} + \\frac{{{c}n(n+1)(2n+1)}}{{6}} - \\text{{const}} = \\Theta(n^3)",
                "explanation": f"Apply the sum of squares identity $\\sum_{{i=1}}^n i^2 = \\frac{{n(n+1)(2n+1)}}{{6}}$."
            },
            {
                "number": 6,
                "title": "Final Complexity",
                "equation": "\\Theta(n^3)",
                "explanation": "The leading term has degree 3, yielding an asymptotic bound of $\\Theta(n^3)$."
            }
        ]

        return {
            "supported": True,
            "recurrence": rec_str,
            "base_case": f"T({n0}) = {b0}",
            "type_name": "Quadratic Growth Decrement Recurrence",
            "steps": steps,
            "exact_solution": f"T(n) = \\frac{{{c}n(n+1)(2n+1)}}{{6}} + O(1)",
            "complexity": "Θ(n³)",
            "complexity_latex": "\\Theta(n^3)",
            "method": "Substitution Method"
        }

    # 4. T(n) = a*T(n-1) + c (Exponential Decrement e.g. Tower of Hanoi: 2T(n-1) + 1)
    if a > 1 and step == 1 and fn_type == "const":
        c_val = c
        steps = [
            {
                "number": 1,
                "title": "Given Recurrence",
                "equation": f"T(n) = {a}T(n-1) + {c_val}",
                "explanation": f"State the recurrence with multiplicative branch factor $a = {a}$ and constant cost $c = {c_val}$."
            },
            {
                "number": 2,
                "title": "First Substitution",
                "equation": f"T(n-1) = {a}T(n-2) + {c_val} \\\\\n\\implies T(n) = {a}[{a}T(n-2) + {c_val}] + {c_val} = {a**2}T(n-2) + {a*c_val + c_val}",
                "explanation": f"Substitute $T(n-1)$ into $T(n)$ and distribute coefficient ${a}$."
            },
            {
                "number": 3,
                "title": "Second Substitution",
                "equation": f"T(n-2) = {a}T(n-3) + {c_val} \\\\\n\\implies T(n) = {a**2}[{a}T(n-3) + {c_val}] + {a*c_val + c_val} = {a**3}T(n-3) + {a**2*c_val + a*c_val + c_val}",
                "explanation": "Expand once more to reveal the geometric progression of cost terms."
            },
            {
                "number": 4,
                "title": "General Pattern (k-th step)",
                "equation": f"T(n) = {a}^k T(n-k) + {c_val} \\sum_{{i=0}}^{{k-1}} {a}^i = {a}^k T(n-k) + {c_val} \\cdot \\frac{{{a}^k - 1}}{{{a} - 1}}",
                "explanation": f"Using the geometric series sum formula $\\sum_{{i=0}}^{{k-1}} {a}^i = \\frac{{{a}^k - 1}}{{{a} - 1}}$, formulate the general $k$-step equation."
            },
            {
                "number": 5,
                "title": "Reach Base Case",
                "equation": f"n - k = {n0} \\implies k = n - {n0}",
                "explanation": f"Set $n - k = {n0}$ to find $k = n - {n0}$."
            },
            {
                "number": 6,
                "title": "Substitute k & Apply Base Case",
                "equation": f"T(n) = {a}^{{n-{n0}}} T({n0}) + {c_val} \\cdot \\frac{{{a}^{{n-{n0}}} - 1}}{{{a} - 1}} \\\\\n\\text{{Since }} T({n0}) = {b0}: \\\\\nT(n) = {b0} \\cdot {a}^{{n-{n0}}} + {c_val} \\cdot \\frac{{{a}^{{n-{n0}}} - 1}}{{{a} - 1}}",
                "explanation": f"Substitute $k = n - {n0}$ and replace $T({n0})$ with ${b0}$."
            },
            {
                "number": 7,
                "title": "Final Complexity",
                "equation": f"\\Theta({a}^n)",
                "explanation": f"The dominant term grows exponentially as ${a}^n$, yielding a tight bound of $\\Theta({a}^n)$."
            }
        ]

        if a == 2 and c_val == 1 and n0 == 1 and b0 == 1:
            exact_str = "T(n) = 2^n - 1"
        else:
            exact_str = f"T(n) = {b0} \\cdot {a}^{{n-{n0}}} + \\frac{{{c_val}({a}^{{n-{n0}}} - 1)}}{{{a-1}}}"

        return {
            "supported": True,
            "recurrence": rec_str,
            "base_case": f"T({n0}) = {b0}",
            "type_name": "Exponential Decrement Recurrence (Tower of Hanoi Type)",
            "steps": steps,
            "exact_solution": exact_str,
            "complexity": f"Θ({a}^n)",
            "complexity_latex": f"\\Theta({a}^n)",
            "method": "Substitution Method"
        }

    # 5. General T(n-k) + c (Arbitrary step decrement, e.g. T(n-2) + 3)
    if a == 1 and step > 1 and fn_type == "const":
        c_val = c
        steps = [
            {
                "number": 1,
                "title": "Given Recurrence",
                "equation": f"T(n) = T(n - {step}) + {c_val}",
                "explanation": f"State the decrement recurrence with step size ${step}$ and base case $T({n0}) = {b0}$."
            },
            {
                "number": 2,
                "title": "First Substitution",
                "equation": f"T(n - {step}) = T(n - {2*step}) + {c_val} \\\\\n\\implies T(n) = T(n - {2*step}) + {2*c_val}",
                "explanation": f"Substitute $T(n - {step})$ back into $T(n)$."
            },
            {
                "number": 3,
                "title": "General Pattern (k-th step)",
                "equation": f"T(n) = T(n - {step}k) + {c_val}k",
                "explanation": f"After $k$ steps of size ${step}$, the relation is $T(n - {step}k) + {c_val}k$."
            },
            {
                "number": 4,
                "title": "Reach Base Case",
                "equation": f"n - {step}k = {n0} \\implies k = \\frac{{n - {n0}}}{{{step}}}",
                "explanation": f"Solve for $k$ such that the argument reaches ${n0}$."
            },
            {
                "number": 5,
                "title": "Substitute k & Apply Base Case",
                "equation": f"T(n) = T({n0}) + {c_val} \\cdot \\left(\\frac{{n - {n0}}}{{{step}}}\\right) = {b0} + \\frac{{{c_val}}}{{{step}}}(n - {n0})",
                "explanation": f"Substitute $k$ and apply base value $T({n0}) = {b0}$."
            },
            {
                "number": 6,
                "title": "Final Complexity",
                "equation": "\\Theta(n)",
                "explanation": "The highest order term is linear in $n$, giving $\\Theta(n)$."
            }
        ]

        return {
            "supported": True,
            "recurrence": rec_str,
            "base_case": f"T({n0}) = {b0}",
            "type_name": f"Step-{step} Decrement Recurrence",
            "steps": steps,
            "exact_solution": f"T(n) = \\frac{{{c_val}}}{{{step}}}n + O(1)",
            "complexity": "Θ(n)",
            "complexity_latex": "\\Theta(n)",
            "method": "Substitution Method"
        }

    # Fallback for other decrement forms
    return {
        "supported": False,
        "error_message": "This specific decrement recurrence form is outside our direct substitution pattern library.",
        "suggested_examples": ["T(n) = T(n-1) + 5", "T(n) = 2T(n-1) + 1", "T(n) = T(n-1) + n"]
    }


def _solve_divide(a: int, b: int, fn: dict, n0: int, b0: int, rec_str: str, base_str: str) -> dict:
    """
    Handles divide-and-conquer recurrences of the form:
    T(n) = a*T(n/b) + f(n)
    """
    fn_type = fn["type"]
    c = fn.get("coeff", 1)
    deg = fn.get("deg", 0)

    log_b_str = f"\\log_{{{b}}} n" if b != 2 else "\\log_2 n"

    # 1. T(n) = T(n/b) + c (Binary Search type: a=1, f(n)=c)
    if a == 1 and fn_type == "const":
        c_val = c
        steps = [
            {
                "number": 1,
                "title": "Given Recurrence",
                "equation": f"T(n) = T(n/{b}) + {c_val}",
                "explanation": f"State the logarithmic divide-and-conquer recurrence with base case $T({n0}) = {b0}$."
            },
            {
                "number": 2,
                "title": "First Substitution",
                "equation": f"T(n/{b}) = T(n/{b**2}) + {c_val} \\\\\n\\implies T(n) = [T(n/{b**2}) + {c_val}] + {c_val} = T(n/{b**2}) + {2*c_val}",
                "explanation": f"Substitute $T(n/{b})$ into $T(n)$."
            },
            {
                "number": 3,
                "title": "Second Substitution",
                "equation": f"T(n/{b**2}) = T(n/{b**3}) + {c_val} \\\\\n\\implies T(n) = [T(n/{b**3}) + {c_val}] + {2*c_val} = T(n/{b**3}) + {3*c_val}",
                "explanation": "Perform the next substitution to identify how the constant cost accumulates."
            },
            {
                "number": 4,
                "title": "General Pattern (k-th step)",
                "equation": f"T(n) = T(n/{b}^k) + {c_val}k",
                "explanation": f"After $k$ successive recursive divisions, express $T(n)$ in terms of $T(n/{b}^k)$ and $k$."
            },
            {
                "number": 5,
                "title": "Reach Base Case",
                "equation": f"\\frac{{n}}{{{b}^k}} = {n0} \\implies {b}^k = \\frac{{n}}{{{n0}}} \\implies k = \\log_{{{b}}} \\left(\\frac{{n}}{{{n0}}}\\right)",
                "explanation": f"Solve for $k$ such that the subproblem argument reduces to base condition ${n0}$."
            },
            {
                "number": 6,
                "title": "Substitute k & Apply Base Case",
                "equation": f"T(n) = T({n0}) + {f'{c_val}' if c_val != 1 else ''}\\log_{{{b}}} n \\\\\n\\text{{Since }} T({n0}) = {b0}: \\\\\nT(n) = {b0} + {f'{c_val}' if c_val != 1 else ''}\\log_{{{b}}} n",
                "explanation": f"Substitute $k = \\log_{{{b}}} n$ and apply $T({n0}) = {b0}$ to get the exact analytical equation."
            },
            {
                "number": 7,
                "title": "Final Complexity",
                "equation": "\\Theta(\\log n)",
                "explanation": "Because logarithmic bases differ only by constant factors (change of base), the tight asymptotic bound is $\\Theta(\\log n)$."
            }
        ]

        c_disp = f"{c_val}" if c_val != 1 else ""
        exact_str = f"T(n) = {b0} + {c_disp}\\log_{{{b}}} n" if n0 == 1 else f"T(n) = {b0} + {c_disp}\\log_{{{b}}} (n/{n0})"

        return {
            "supported": True,
            "recurrence": rec_str,
            "base_case": f"T({n0}) = {b0}",
            "type_name": "Logarithmic Divide-and-Conquer (Binary Search Type)",
            "steps": steps,
            "exact_solution": exact_str,
            "complexity": "Θ(log n)",
            "complexity_latex": "\\Theta(\\log n)",
            "method": "Substitution Method"
        }

    # 2. T(n) = a*T(n/b) + c (e.g. 2T(n/2) + 1, 3T(n/2) + 1)
    if a > 1 and fn_type == "const":
        c_val = c
        log_b_a = math.log(a, b)
        log_str = f"n^{{\\log_{{{b}}} {a}}}" if not log_b_a.is_integer() else (f"n" if int(log_b_a) == 1 else f"n^{{{int(log_b_a)}}}")

        steps = [
            {
                "number": 1,
                "title": "Given Recurrence",
                "equation": f"T(n) = {a}T(n/{b}) + {c_val}",
                "explanation": f"State the branching divide-and-conquer relation with constant extra work per node."
            },
            {
                "number": 2,
                "title": "First Substitution",
                "equation": f"T(n/{b}) = {a}T(n/{b**2}) + {c_val} \\\\\n\\implies T(n) = {a}[{a}T(n/{b**2}) + {c_val}] + {c_val} = {a**2}T(n/{b**2}) + {a*c_val + c_val}",
                "explanation": f"Substitute $T(n/{b})$ into $T(n)$ and expand."
            },
            {
                "number": 3,
                "title": "Second Substitution",
                "equation": f"T(n/{b**2}) = {a}T(n/{b**3}) + {c_val} \\\\\n\\implies T(n) = {a**2}[{a}T(n/{b**3}) + {c_val}] + {a*c_val + c_val} = {a**3}T(n/{b**3}) + {a**2*c_val + a*c_val + c_val}",
                "explanation": "Observe the geometric expansion of constant work across recursive branches."
            },
            {
                "number": 4,
                "title": "General Pattern (k-th step)",
                "equation": f"T(n) = {a}^k T(n/{b}^k) + {c_val} \\sum_{{i=0}}^{{k-1}} {a}^i = {a}^k T(n/{b}^k) + {c_val} \\cdot \\frac{{{a}^k - 1}}{{{a} - 1}}",
                "explanation": f"Summing the geometric series $\\sum_{{i=0}}^{{k-1}} {a}^i = \\frac{{{a}^k - 1}}{{{a}-1}}$ after $k$ division steps."
            },
            {
                "number": 5,
                "title": "Reach Base Case",
                "equation": f"\\frac{{n}}{{{b}^k}} = 1 \\implies k = \\log_{{{b}}} n",
                "explanation": f"Solve for recursion depth $k = \\log_{{{b}}} n$ when reaching subproblem size 1."
            },
            {
                "number": 6,
                "title": "Substitute k & Apply Base Case",
                "equation": f"T(n) = {a}^{{\\log_{{{b}}} n}} T(1) + {c_val} \\cdot \\frac{{{a}^{{\\log_{{{b}}} n}} - 1}}{{{a} - 1}} \\\\\n\\text{{Using }} {a}^{{\\log_{{{b}}} n}} = n^{{\\log_{{{b}}} {a}}} = {log_str}: \\\\\nT(n) = {b0} \\cdot {log_str} + {c_val} \\cdot \\frac{{{log_str} - 1}}{{{a} - 1}}",
                "explanation": f"Using the logarithmic identity $a^{{\\log_b n}} = n^{{\\log_b a}}$, derive the closed form."
            },
            {
                "number": 7,
                "title": "Final Complexity",
                "equation": f"\\Theta({log_str})",
                "explanation": f"The total leaf node work dominates the execution time, giving a tight bound of $\\Theta({log_str})$."
            }
        ]

        return {
            "supported": True,
            "recurrence": rec_str,
            "base_case": f"T({n0}) = {b0}",
            "type_name": "Divide-and-Conquer (Branching with Constant Cost)",
            "steps": steps,
            "exact_solution": f"T(n) = \\Theta({log_str})",
            "complexity": f"Θ({log_str})",
            "complexity_latex": f"\\Theta({log_str})",
            "method": "Substitution Method"
        }

    # 3. T(n) = a*T(n/b) + c*n (Linear combine cost, e.g. MergeSort: 2T(n/2) + n, 3T(n/2) + n, 4T(n/2) + n, T(n/2) + n)
    if fn_type == "poly" and deg == 1:
        c_n_str = f"{c}n" if c != 1 else "n"

        # Subcase A: a == b (Balanced Divide-and-Conquer, e.g. 2T(n/2) + n MergeSort)
        if a == b:
            steps = [
                {
                    "number": 1,
                    "title": "Given Recurrence",
                    "equation": f"T(n) = {a}T(n/{b}) + {c_n_str}",
                    "explanation": "State the balanced divide-and-conquer recurrence (classic MergeSort structure)."
                },
                {
                    "number": 2,
                    "title": "First Substitution",
                    "equation": f"T(n/{b}) = {a}T(n/{b**2}) + {c}(n/{b}) \\\\\n\\implies T(n) = {a}\\left[{a}T(n/{b**2}) + {c}(n/{b})\\right] + {c_n_str} = {a**2}T(n/{b**2}) + {2*c}n",
                    "explanation": f"Substitute $T(n/{b})$ into $T(n)$ and simplify the non-recursive linear work."
                },
                {
                    "number": 3,
                    "title": "Second Substitution",
                    "equation": f"T(n/{b**2}) = {a}T(n/{b**3}) + {c}(n/{b**2}) \\\\\n\\implies T(n) = {a**2}\\left[{a}T(n/{b**3}) + {c}(n/{b**2})\\right] + {2*c}n = {a**3}T(n/{b**3}) + {3*c}n",
                    "explanation": f"Substitute $T(n/{b**2})$ to observe that every recursion level adds exactly ${c}n$ work."
                },
                {
                    "number": 4,
                    "title": "General Pattern (k-th step)",
                    "equation": f"T(n) = {a}^k T(n/{b}^k) + k \\cdot {c_n_str}",
                    "explanation": f"After $k$ substitutions, the generalized formula becomes ${a}^k T(n/{b}^k) + k \\cdot {c_n_str}$."
                },
                {
                    "number": 5,
                    "title": "Reach Base Case",
                    "equation": f"\\frac{{n}}{{{b}^k}} = 1 \\implies {b}^k = n \\implies k = \\log_{{{b}}} n",
                    "explanation": f"Solve for the tree depth $k = \\log_{{{b}}} n$ to reach base size 1."
                },
                {
                    "number": 6,
                    "title": "Substitute k & Apply Base Case",
                    "equation": f"T(n) = {a}^{{\\log_{{{b}}} n}} T(1) + (\\log_{{{b}}} n) \\cdot {c_n_str} \\\\\n\\text{{Using }} {a}^{{\\log_{{{b}}} n}} = n^{{\\log_{{{b}}} {a}}} = n^1 = n \\text{{ and }} T(1) = {b0}: \\\\\nT(n) = {f'{b0}n' if b0 != 1 else 'n'} + {f'{c}n' if c != 1 else 'n'} \\log_{{{b}}} n",
                    "explanation": f"Using identity $a^{{\\log_b n}} = n$, substitute $k$ and replace $T(1)$ with ${b0}$."
                },
                {
                    "number": 7,
                    "title": "Final Complexity",
                    "equation": "\\Theta(n \\log n)",
                    "explanation": f"The term $n \\log n$ strictly dominates linear $n$, giving a tight asymptotic bound of $\\Theta(n \\log n)$."
                }
            ]

            term1 = f"{c}n \\log_{{{b}}} n" if c != 1 else f"n \\log_{{{b}}} n"
            term2 = f" + {b0}n" if b0 != 0 and b0 != 1 else (" + n" if b0 == 1 else "")
            exact_str = f"T(n) = {term1}{term2}"

            return {
                "supported": True,
                "recurrence": rec_str,
                "base_case": f"T({n0}) = {b0}",
                "type_name": "Balanced Divide-and-Conquer (MergeSort Type)",
                "steps": steps,
                "exact_solution": exact_str,
                "complexity": "Θ(n log n)",
                "complexity_latex": "\\Theta(n \\log n)",
                "method": "Substitution Method"
            }

        # Subcase B: a > b (Leaf-heavy Divide-and-Conquer, e.g. 3T(n/2) + n, 4T(n/2) + n)
        elif a > b:
            log_b_a = math.log(a, b)
            if log_b_a.is_integer():
                log_power = int(log_b_a)
                leaf_work_str = f"n^{{{log_power}}}"
                complexity_str = f"\\Theta(n^{{{log_power}}})"
                complexity_plain = f"Θ(n^{log_power})" if log_power > 1 else "Θ(n)"
            else:
                leaf_work_str = f"n^{{\\log_{{{b}}} {a}}}"
                complexity_str = f"\\Theta(n^{{\\log_{{{b}}} {a}}})"
                complexity_plain = f"Θ(n^log_{b}{a})"

            steps = [
                {
                    "number": 1,
                    "title": "Given Recurrence",
                    "equation": f"T(n) = {a}T(n/{b}) + {c_n_str}",
                    "explanation": f"State the divide-and-conquer recurrence with branch factor $a = {a} > b = {b}$."
                },
                {
                    "number": 2,
                    "title": "First Substitution",
                    "equation": f"T(n/{b}) = {a}T(n/{b**2}) + {c}(n/{b}) \\\\\n\\implies T(n) = {a}\\left[{a}T(n/{b**2}) + {c}(n/{b})\\right] + {c_n_str} = {a**2}T(n/{b**2}) + {c}n\\left(1 + \\frac{{{a}}}{{{b}}}\\right)",
                    "explanation": f"Substitute $T(n/{b})$ into $T(n)$ and factor $cn$."
                },
                {
                    "number": 3,
                    "title": "Second Substitution",
                    "equation": f"T(n/{b**2}) = {a}T(n/{b**3}) + {c}(n/{b**2}) \\\\\n\\implies T(n) = {a**3}T(n/{b**3}) + {c}n\\left(1 + \\frac{{{a}}}{{{b}}} + \\left(\\frac{{{a}}}{{{b}}}\\right)^2\\right)",
                    "explanation": f"Substitute $T(n/{b**2})$ to observe the geometric series with common ratio $\\frac{{{a}}}{{{b}}} > 1$."
                },
                {
                    "number": 4,
                    "title": "General Pattern (k-th step)",
                    "equation": f"T(n) = {a}^k T(n/{b}^k) + {c}n \\sum_{{i=0}}^{{k-1}} \\left(\\frac{{{a}}}{{{b}}}\\right)^i = {a}^k T(n/{b}^k) + {c}n \\cdot \\frac{{\\left(\\frac{{{a}}}{{{b}}}\\right)^k - 1}}{{\\frac{{{a}}}{{{b}}} - 1}}",
                    "explanation": f"After $k$ steps, the work equals recursive leaf subproblems plus a growing geometric series."
                },
                {
                    "number": 5,
                    "title": "Reach Base Case",
                    "equation": f"\\frac{{n}}{{{b}^k}} = 1 \\implies k = \\log_{{{b}}} n",
                    "explanation": f"Solve for recursion depth $k = \\log_{{{b}}} n$."
                },
                {
                    "number": 6,
                    "title": "Substitute k & Evaluate Dominant Term",
                    "equation": f"T(n) = {a}^{{\\log_{{{b}}} n}} T(1) + {c}n \\cdot \\frac{{ (n/{b})^{{\\log_{{{b}}} (a/b)}} - 1 }}{{\\frac{{{a}}}{{{b}}} - 1}} \\\\\n\\text{{Since }} {a}^{{\\log_{{{b}}} n}} = {leaf_work_str} \\text{{ and }} a > b, \\text{{ the leaf work dominates.}}",
                    "explanation": f"Since the branching factor $a = {a}$ exceeds division factor $b = {b}$, the number of subproblems at the leaf level dominates the runtime."
                },
                {
                    "number": 7,
                    "title": "Final Complexity",
                    "equation": complexity_str,
                    "explanation": f"The total cost is dominated by the leaf level ${leaf_work_str}$, giving tight bound ${complexity_str}$."
                }
            ]

            return {
                "supported": True,
                "recurrence": rec_str,
                "base_case": f"T({n0}) = {b0}",
                "type_name": "Leaf-Dominant Divide-and-Conquer Recurrence",
                "steps": steps,
                "exact_solution": f"T(n) = \\Theta({leaf_work_str})",
                "complexity": complexity_plain,
                "complexity_latex": complexity_str,
                "method": "Substitution Method"
            }

        # Subcase C: a < b (Root-heavy Divide-and-Conquer, e.g. T(n) = T(n/2) + n)
        else:
            steps = [
                {
                    "number": 1,
                    "title": "Given Recurrence",
                    "equation": f"T(n) = {a if a != 1 else ''}T(n/{b}) + {c_n_str}",
                    "explanation": f"State the divide-and-conquer recurrence with branch factor $a = {a} < b = {b}$."
                },
                {
                    "number": 2,
                    "title": "First Substitution",
                    "equation": f"T(n/{b}) = {a if a != 1 else ''}T(n/{b**2}) + {c}(n/{b}) \\\\\n\\implies T(n) = {a**2 if a != 1 else ''}T(n/{b**2}) + {c}n\\left(1 + \\frac{{{a}}}{{{b}}}\\right)",
                    "explanation": f"Substitute $T(n/{b})$ into $T(n)$."
                },
                {
                    "number": 3,
                    "title": "General Pattern (k-th step)",
                    "equation": f"T(n) = {a}^k T(n/{b}^k) + {c}n \\sum_{{i=0}}^{{k-1}} \\left(\\frac{{{a}}}{{{b}}}\\right)^i",
                    "explanation": f"Since $\\frac{{{a}}}{{{b}}} < 1$, the geometric series converges to a constant upper bound $\\frac{{1}}{{1 - a/b}}$."
                },
                {
                    "number": 4,
                    "title": "Reach Base Case",
                    "equation": f"\\frac{{n}}{{{b}^k}} = 1 \\implies k = \\log_{{{b}}} n",
                    "explanation": f"Solve for recursion depth $k = \\log_{{{b}}} n$."
                },
                {
                    "number": 5,
                    "title": "Evaluate Convergent Geometric Series",
                    "equation": f"T(n) = {a}^{{\\log_{{{b}}} n}} T(1) + {c}n \\sum_{{i=0}}^{{\\infty}} \\left(\\frac{{{a}}}{{{b}}}\\right)^i = O(n) + {c}n \\cdot \\frac{{1}}{{1 - {a}/{b}}} = \\Theta(n)",
                    "explanation": f"The non-recursive root-level work $c \\cdot n$ dominates because the geometric ratio is less than 1."
                },
                {
                    "number": 6,
                    "title": "Final Complexity",
                    "equation": "\\Theta(n)",
                    "explanation": "The root-level linear work dominates the decreasing geometric series, yielding $\\Theta(n)$."
                }
            ]

            return {
                "supported": True,
                "recurrence": rec_str,
                "base_case": f"T({n0}) = {b0}",
                "type_name": "Root-Dominant Divide-and-Conquer Recurrence",
                "steps": steps,
                "exact_solution": f"T(n) = \\frac{{{c}}}{{1 - {a}/{b}}}n + O(1)",
                "complexity": "Θ(n)",
                "complexity_latex": "\\Theta(n)",
                "method": "Substitution Method"
            }

    # 4. T(n) = a*T(n/b) + c*n^2 (Polynomial combine cost e.g. 2T(n/2) + n^2, 4T(n/2) + n^2)
    if fn_type == "poly" and deg == 2:
        # Check a vs b^2
        b_sq = b**2
        if a < b_sq:
            # Root dominates: Theta(n^2)
            steps = [
                {
                    "number": 1,
                    "title": "Given Recurrence",
                    "equation": f"T(n) = {a if a != 1 else ''}T(n/{b}) + {c if c != 1 else ''}n^2",
                    "explanation": f"State the divide-and-conquer recurrence with quadratic non-recursive combine cost."
                },
                {
                    "number": 2,
                    "title": "First Substitution",
                    "equation": f"T(n/{b}) = {a if a != 1 else ''}T(n/{b**2}) + {c if c != 1 else ''}(n/{b})^2 \\\\\n\\implies T(n) = {a**2 if a != 1 else ''}T(n/{b**2}) + {c}n^2\\left(1 + \\frac{{{a}}}{{{b_sq}}}\\right)",
                    "explanation": f"Substitute $T(n/{b})$ into $T(n)$ and factor $cn^2$."
                },
                {
                    "number": 3,
                    "title": "General Pattern (k-th step)",
                    "equation": f"T(n) = {a}^k T(n/{b}^k) + {c}n^2 \\sum_{{i=0}}^{{k-1}} \\left(\\frac{{{a}}}{{{b_sq}}}\\right)^i",
                    "explanation": f"Since $\\frac{{{a}}}{{{b_sq}}} < 1$, the geometric series converges to a constant factor."
                },
                {
                    "number": 4,
                    "title": "Reach Base Case",
                    "equation": f"\\frac{{n}}{{{b}^k}} = 1 \\implies k = \\log_{{{b}}} n",
                    "explanation": f"Solve for recursion depth $k = \\log_{{{b}}} n$."
                },
                {
                    "number": 5,
                    "title": "Evaluate Closed Form & Complexity",
                    "equation": f"T(n) = {a}^{{\\log_{{{b}}} n}} T(1) + {c}n^2 \\cdot \\frac{{1}}{{1 - {a}/{b_sq}}} = \\Theta(n^2)",
                    "explanation": "The root level work $n^2$ dominates the total cost."
                },
                {
                    "number": 6,
                    "title": "Final Complexity",
                    "equation": "\\Theta(n^2)",
                    "explanation": "The quadratic root term dominates, yielding $\\Theta(n^2)$."
                }
            ]

            return {
                "supported": True,
                "recurrence": rec_str,
                "base_case": f"T({n0}) = {b0}",
                "type_name": "Root-Dominant Polynomial Divide-and-Conquer",
                "steps": steps,
                "exact_solution": f"T(n) = \\Theta(n^2)",
                "complexity": "Θ(n²)",
                "complexity_latex": "\\Theta(n^2)",
                "method": "Substitution Method"
            }
        elif a == b_sq:
            # Balanced: Theta(n^2 log n)
            steps = [
                {
                    "number": 1,
                    "title": "Given Recurrence",
                    "equation": f"T(n) = {a}T(n/{b}) + {c if c != 1 else ''}n^2",
                    "explanation": "State the balanced quadratic recurrence relation."
                },
                {
                    "number": 2,
                    "title": "General Pattern (k-th step)",
                    "equation": f"T(n) = {a}^k T(n/{b}^k) + k \\cdot {c if c != 1 else ''}n^2",
                    "explanation": f"Each recursion level contributes exactly $n^2$ work."
                },
                {
                    "number": 3,
                    "title": "Reach Base Case",
                    "equation": f"k = \\log_{{{b}}} n",
                    "explanation": "Recursion depth is $\\log_b n$."
                },
                {
                    "number": 4,
                    "title": "Final Complexity",
                    "equation": "\\Theta(n^2 \\log n)",
                    "explanation": "Summing across $\\log_b n$ levels gives $\\Theta(n^2 \\log n)$."
                }
            ]

            return {
                "supported": True,
                "recurrence": rec_str,
                "base_case": f"T({n0}) = {b0}",
                "type_name": "Balanced Quadratic Divide-and-Conquer",
                "steps": steps,
                "exact_solution": f"T(n) = \\Theta(n^2 \\log n)",
                "complexity": "Θ(n² log n)",
                "complexity_latex": "\\Theta(n^2 \\log n)",
                "method": "Substitution Method"
            }

    # Fallback for other divide forms
    return {
        "supported": False,
        "error_message": "This specific divide-and-conquer form is outside our direct substitution pattern library.",
        "suggested_examples": ["T(n) = T(n/2) + 1", "T(n) = 2T(n/2) + n", "T(n) = 3T(n/2) + n"]
    }
