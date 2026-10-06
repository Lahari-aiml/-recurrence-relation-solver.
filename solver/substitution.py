"""
Substitution Method Solver Engine for Recurrence Relations.
Solves recurrence relations dynamically using ONLY the Step-by-Step Substitution Method.
Generates rigorous, mathematically correct step-by-step unrolling, pattern formulation,
stopping conditions, closed forms, and Big-O, Big-Theta, and Big-Omega bounds.
"""

import re
import math


def parse_base_case(base_str: str) -> tuple[int, int, bool]:
    """
    Parses base case string like 'T(1) = 1', 'T(0) = 0', 'T(1) = 5', '1', '0'.
    Returns (n0, b0, is_explicit). Defaults to (1, 1, False) if empty or unspecified.
    """
    if not base_str or not base_str.strip():
        return (1, 1, False)

    cleaned = base_str.replace(" ", "")
    # Pattern: T(n0) = b0
    match = re.search(r"[T|t]\((\d+)\)\=(\-?\d+)", cleaned)
    if match:
        return (int(match.group(1)), int(match.group(2)), True)

    # Just a single integer
    if cleaned.lstrip("-").isdigit():
        return (1, int(cleaned), True)

    return (1, 1, False)


def normalize_math_symbols(s: str) -> str:
    """Normalizes unicode superscripts, multiplication asterisks, and whitespace."""
    s = s.replace("²", "^2").replace("³", "^3").replace("⁴", "^4")
    s = s.replace("**", "^")
    s = s.replace("−", "-").replace("—", "-")
    return s


def parse_fn_term(term_str: str) -> dict:
    """
    Parses non-recursive cost term f(n).
    Supports:
    - Constants: '1', '5', '0', '-2'
    - Linear: 'n', '2n', '5*n'
    - Polynomial: 'n^2', 'n^3', 'n^4', '2n^2', '3n^3'
    - Logarithmic: 'log n', 'logn', 'log2(n)', 'log(n)', 'ln(n)', 'log^2 n'
    - Linearithmic: 'n log n', 'nlogn', 'n*log(n)', '2n log n', 'n log^2 n'
    - Poly-log: 'n^2 log n', 'n^2 log^2 n'
    """
    s = term_str.strip()
    if not s:
        return {"type": "const", "coeff": 0, "deg": 0, "log_deg": 0, "raw": "0"}

    # Normalize symbols
    s_norm = normalize_math_symbols(s).replace("*", "").replace(" ", "").lower()

    # Pure integer constant
    if s_norm.isdigit() or (s_norm.startswith("-") and s_norm[1:].isdigit()):
        return {"type": "const", "coeff": int(s_norm), "deg": 0, "log_deg": 0, "raw": s}

    # Linearithmic with power of log: e.g. n log^2 n or n(logn)^2 or nlog^2(n)
    m_nlogn_pow = re.fullmatch(r"(\d*)n(?:log(?:2)?|\(log(?:2)?\))\^?(\d*)(?:\(n\)|n)?", s_norm)
    if m_nlogn_pow:
        c = int(m_nlogn_pow.group(1)) if m_nlogn_pow.group(1) else 1
        log_d = int(m_nlogn_pow.group(2)) if m_nlogn_pow.group(2) else 1
        return {"type": "n_log_n", "coeff": c, "deg": 1, "log_deg": log_d, "raw": s}

    # Linearithmic standard: n log n, 2n log n, nlogn, n*log2(n)
    m_nlogn = re.fullmatch(r"(\d*)nlog(?:2)?(?:\(n\)|n)?", s_norm)
    if m_nlogn:
        c = int(m_nlogn.group(1)) if m_nlogn.group(1) else 1
        return {"type": "n_log_n", "coeff": c, "deg": 1, "log_deg": 1, "raw": s}

    # Logarithmic with power: log^2 n, log^2(n), log2^2(n)
    m_logn_pow = re.fullmatch(r"(\d*)log(?:2)?\^?(\d*)(?:\(n\)|n)?", s_norm)
    if m_logn_pow and m_logn_pow.group(2):
        c = int(m_logn_pow.group(1)) if m_logn_pow.group(1) else 1
        log_d = int(m_logn_pow.group(2))
        return {"type": "log_n", "coeff": c, "deg": 0, "log_deg": log_d, "raw": s}

    # Logarithmic standard: log n, log2 n, log(n), ln(n)
    m_logn = re.fullmatch(r"(\d*)(?:log(?:2)?|ln)(?:\(n\)|n)?", s_norm)
    if m_logn:
        c = int(m_logn.group(1)) if m_logn.group(1) else 1
        return {"type": "log_n", "coeff": c, "deg": 0, "log_deg": 1, "raw": s}

    # Polynomial / Linear: e.g. n, 2n, n^2, 3n^2, n^3, n^4
    m_poly = re.fullmatch(r"(\d*)n\^?(\d*)", s_norm)
    if m_poly:
        c = int(m_poly.group(1)) if m_poly.group(1) else 1
        d = int(m_poly.group(2)) if m_poly.group(2) else 1
        return {"type": "poly", "coeff": c, "deg": d, "log_deg": 0, "raw": s}

    # Poly-log: e.g. n^2 log n
    m_polylog = re.fullmatch(r"(\d*)n\^?(\d*)log(?:2)?(?:\(n\)|n)?", s_norm)
    if m_polylog:
        c = int(m_polylog.group(1)) if m_polylog.group(1) else 1
        d = int(m_polylog.group(2)) if m_polylog.group(2) else 1
        return {"type": "poly_log", "coeff": c, "deg": d, "log_deg": 1, "raw": s}

    return {"type": "custom", "coeff": 1, "deg": 1, "log_deg": 0, "raw": s}


def parse_recurrence(rec_str: str) -> dict:
    """
    Parses a recurrence relation into structured mathematical components.
    Handles variations in spacing, casing, power notation, and LHS/RHS prefixes.
    """
    if not rec_str or not rec_str.strip():
        return {"type": "INVALID", "error": "Please enter a valid recurrence relation."}

    # Normalize string
    s = normalize_math_symbols(rec_str).strip()
    s_clean = s.replace(" ", "")

    if "=" in s_clean:
        lhs, rhs = s_clean.split("=", 1)
    else:
        rhs = s_clean

    # 1. Pattern for decrement: a*T(n-k) +/- rest
    # Examples: T(n-1)+1, T(n-1)+n, 2T(n-1)+1, T(n-2)+3, T(n-1)+n^2, T(n-1)+logn
    m_dec = re.fullmatch(r"(\d*)\*?[T|t]\(n\-(\d+)\)(?:([\+\-])(.+))?", rhs)
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

    # 2. Pattern for divide-and-conquer: a*T(n/b) +/- rest
    # Examples: 2T(n/2)+n, T(n/2)+1, 3T(n/2)+n, 2T(n/2)+1, 2T(n/2)+nlogn, T(n/3)+n, 2T(n/3)+n, 4T(n/3)+n^2
    m_div = re.fullmatch(r"(\d*)\*?[T|t]\(n\/(\d+)\)(?:([\+\-])(.+))?", rhs)
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

    # Check if user entered something like sin(n) or invalid syntax
    return {
        "type": "UNSUPPORTED",
        "error": "This recurrence is currently outside the supported substitution patterns."
    }


def solve_recurrence(rec_str: str, base_str: str = "T(1) = 1") -> dict:
    """
    Main entry point for solving recurrence relations using the Substitution Method.
    Generates structured, mathematically accurate step-by-step substitution derivation.
    """
    if not rec_str or not rec_str.strip():
        return {
            "supported": False,
            "error_message": "Please enter a valid recurrence relation.",
            "suggested_examples": [
                "T(n) = 2T(n/2) + n",
                "T(n) = T(n-1) + 1",
                "T(n) = T(n-1) + n",
                "T(n) = T(n/2) + 1",
                "T(n) = 3T(n/2) + n",
                "T(n) = 2T(n/3) + n",
                "T(n) = 2T(n/2) + n log n"
            ]
        }

    parsed = parse_recurrence(rec_str)
    if parsed.get("type") in ["INVALID", "UNSUPPORTED"]:
        err_msg = parsed.get("error", "Please enter a valid recurrence relation.")
        return {
            "supported": False,
            "error_message": err_msg,
            "suggested_examples": [
                "T(n) = 2T(n/2) + n",
                "T(n) = T(n-1) + 1",
                "T(n) = T(n-1) + n",
                "T(n) = T(n/2) + 1",
                "T(n) = 3T(n/2) + n",
                "T(n) = 2T(n/3) + n",
                "T(n) = 2T(n/2) + n log n"
            ]
        }

    n0, b0, is_explicit_base = parse_base_case(base_str)
    rec_type = parsed["type"]

    # Normalize recurrence display string: ensure T(n) = prefix
    clean_rec = rec_str.strip()
    if not clean_rec.startswith("T(n)") and not clean_rec.startswith("t(n)"):
        clean_rec = f"T(n) = {clean_rec}"

    if rec_type == "DECREMENT":
        return _solve_decrement(parsed["a"], parsed["k_step"], parsed["fn"], n0, b0, is_explicit_base, clean_rec)
    elif rec_type == "DIVIDE":
        return _solve_divide(parsed["a"], parsed["b"], parsed["fn"], n0, b0, is_explicit_base, clean_rec)

    return {
        "supported": False,
        "error_message": "This recurrence is currently outside the supported substitution patterns.",
        "suggested_examples": [
            "T(n) = 2T(n/2) + n",
            "T(n) = T(n-1) + 1",
            "T(n) = T(n-1) + n",
            "T(n) = T(n/2) + 1",
            "T(n) = 3T(n/2) + n",
            "T(n) = 2T(n/3) + n",
            "T(n) = 2T(n/2) + n log n"
        ]
    }


def _solve_decrement(a: int, step: int, fn: dict, n0: int, b0: int, is_explicit_base: bool, rec_str: str) -> dict:
    """
    Handles recurrences of the form:
    T(n) = a*T(n - step) + f(n)
    """
    fn_type = fn["type"]
    c = fn.get("coeff", 1)
    deg = fn.get("deg", 0)
    log_deg = fn.get("log_deg", 0)

    base_note = f"Base case: $T({n0}) = {b0}$." if is_explicit_base else f"Base case not specified; assuming standard boundary condition $T({n0}) = {b0}$."

    # 1. T(n) = T(n-1) + c (e.g. T(n-1) + 1, T(n-1) + 5)
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
                "title": "Write the Original Recurrence",
                "equation": f"T(n) = T(n-1){c_str}",
                "explanation": f"Write the original recurrence relation. {base_note}"
            },
            {
                "number": 2,
                "title": "Substitute T(n-1)",
                "equation": f"T(n-1) = T(n-2){c_str} \\\\\n\\text{{Therefore: }} \\\\\nT(n) = [T(n-2){c_str}]{c_str} = T(n-2){c2_str}",
                "explanation": "Substitute $T(n-1)$ back into the original relation for $T(n)$ and simplify."
            },
            {
                "number": 3,
                "title": "Expand Again (Substitute T(n-2))",
                "equation": f"T(n-2) = T(n-3){c_str} \\\\\n\\text{{Therefore: }} \\\\\nT(n) = [T(n-3){c_str}]{c2_str} = T(n-3){c3_str}",
                "explanation": "Substitute $T(n-2)$ to observe how the additive constant accumulates at each step."
            },
            {
                "number": 4,
                "title": "General Pattern (k-th step)",
                "equation": f"T(n) = T(n-k){ck_str}",
                "explanation": f"After $k$ successive substitutions, express $T(n)$ in terms of $T(n-k)$ and $k$."
            },
            {
                "number": 5,
                "title": "Find the Stopping Condition (Base Case)",
                "equation": f"n - k = {n0} \\implies k = n - {n0}",
                "explanation": f"Set the inner subproblem equal to base index ${n0}$ to determine the number of levels $k$."
            },
            {
                "number": 6,
                "title": "Substitute k and Simplify",
                "equation": f"T(n) = T({n0}){f' + {c_val}(n - {n0})' if c_val != 0 else ''} \\\\\n\\text{{Since }} T({n0}) = {b0}: \\\\\nT(n) = {b0}{f' + {c_val}(n - {n0})' if c_val != 0 else ''} = {exact_str}",
                "explanation": f"Substitute $k = n - {n0}$ and replace $T({n0})$ with ${b0}$ to get the simplified closed form."
            },
            {
                "number": 7,
                "title": "Final Complexity",
                "equation": "T(n) = \\Theta(n)",
                "explanation": f"There are $n - {n0}$ levels of substitution, and each level adds constant work ${c_val}$. Total work is $(n - {n0}) \\times {c_val} + {b0} = \\Theta(n)$."
            }
        ]

        explanation = f"There are $n - {n0}$ levels of substitution, and each level contributes a constant work of ${c_val}$. Total work $= {c_val} \\times (n - {n0}) + {b0} = \\Theta(n)$."

        return {
            "supported": True,
            "recurrence": rec_str,
            "base_case": f"T({n0}) = {b0}",
            "base_case_assumed": not is_explicit_base,
            "base_case_note": base_note,
            "type_name": "Linear Decrement (Substitution Method)",
            "steps": steps,
            "exact_solution": f"T(n) = {exact_str}",
            "num_levels": f"k = n - {n0}",
            "complexity": "Θ(n)",
            "complexity_latex": "\\Theta(n)",
            "big_o": "O(n)",
            "big_theta": "\\Theta(n)",
            "big_omega": "\\Omega(n)",
            "complexity_explanation": explanation,
            "method": "Substitution Method"
        }

    # 2. T(n) = T(n-1) + n or T(n-1) + c*n (Linear work decrement, e.g. Selection/Insertion Sort)
    if a == 1 and step == 1 and fn_type == "poly" and deg == 1:
        c_n = f"{c}n" if c != 1 else "n"
        c_n_minus_1 = f"{c}(n-1)" if c != 1 else "(n-1)"
        c_n_minus_2 = f"{c}(n-2)" if c != 1 else "(n-2)"

        steps = [
            {
                "number": 1,
                "title": "Write the Original Recurrence",
                "equation": f"T(n) = T(n-1) + {c_n}",
                "explanation": f"Write the original recurrence relation. {base_note}"
            },
            {
                "number": 2,
                "title": "Substitute T(n-1)",
                "equation": f"T(n-1) = T(n-2) + {c_n_minus_1} \\\\\n\\text{{Therefore: }} \\\\\nT(n) = T(n-2) + {c_n_minus_1} + {c_n}",
                "explanation": f"Substitute $T(n-1)$ into $T(n)$."
            },
            {
                "number": 3,
                "title": "Expand Again (Substitute T(n-2))",
                "equation": f"T(n-2) = T(n-3) + {c_n_minus_2} \\\\\n\\text{{Therefore: }} \\\\\nT(n) = T(n-3) + {c_n_minus_2} + {c_n_minus_1} + {c_n}",
                "explanation": "Substitute $T(n-2)$ to observe the arithmetic progression series."
            },
            {
                "number": 4,
                "title": "General Pattern (k-th step)",
                "equation": f"T(n) = T(n-k) + {c if c != 1 else ''} \\sum_{{i=0}}^{{k-1}} (n - i)",
                "explanation": f"After $k$ steps, express $T(n)$ as $T(n-k)$ plus the sum of the first $k$ terms."
            },
            {
                "number": 5,
                "title": "Find the Stopping Condition (Base Case)",
                "equation": f"n - k = {n0} \\implies k = n - {n0}",
                "explanation": f"Set inner subproblem size to base case index ${n0}$."
            },
            {
                "number": 6,
                "title": "Substitute k and Simplify",
                "equation": f"T(n) = T({n0}) + {c if c != 1 else ''} \\sum_{{i={n0}+1}}^{{n}} i \\\\\n\\text{{Using }} \\sum_{{i=1}}^n i = \\frac{{n(n+1)}}{{2}}: \\\\\nT(n) = {b0} + {c if c != 1 else ''} \\left[ \\frac{{n(n+1)}}{{2}} - \\frac{{{n0}({n0}+1)}}{{2}} \\right]",
                "explanation": f"Apply Gaussian summation formula $\\sum_{{i=1}}^n i = \\frac{{n(n+1)}}{{2}}$ and substitute $T({n0}) = {b0}$."
            },
            {
                "number": 7,
                "title": "Final Complexity",
                "equation": "T(n) = \\Theta(n^2)",
                "explanation": f"The arithmetic progression of $n$ terms evaluates to $\\frac{{n(n+1)}}{{2}} = \\frac{{1}}{{2}}n^2 + \\frac{{1}}{{2}}n$. The dominant term is quadratic, yielding $\\Theta(n^2)$."
            }
        ]

        exact_str = f"\\frac{{{c}n(n+1)}}{{2}}" if (n0 == 1 and b0 == 1 and c == 1) else f"\\frac{{{c}n^2 + {c}n}}{{2}} + O(1)"
        explanation = f"There are $n - {n0}$ levels of substitution, and the work decreases linearly from $n$ to $1$. The sum of the arithmetic series is $\\sum_{{i=1}}^n i = \\frac{{n(n+1)}}{{2}} = \\Theta(n^2)$."

        return {
            "supported": True,
            "recurrence": rec_str,
            "base_case": f"T({n0}) = {b0}",
            "base_case_assumed": not is_explicit_base,
            "base_case_note": base_note,
            "type_name": "Linear Growth Decrement Recurrence (Substitution Method)",
            "steps": steps,
            "exact_solution": f"T(n) = {exact_str}",
            "num_levels": f"k = n - {n0}",
            "complexity": "Θ(n²)",
            "complexity_latex": "\\Theta(n^2)",
            "big_o": "O(n^2)",
            "big_theta": "\\Theta(n^2)",
            "big_omega": "\\Omega(n^2)",
            "complexity_explanation": explanation,
            "method": "Substitution Method"
        }

    # 3. T(n) = T(n-1) + n^2 (Quadratic Growth Decrement)
    if a == 1 and step == 1 and fn_type == "poly" and deg == 2:
        steps = [
            {
                "number": 1,
                "title": "Write the Original Recurrence",
                "equation": f"T(n) = T(n-1) + {c if c != 1 else ''}n^2",
                "explanation": f"Write the original recurrence relation. {base_note}"
            },
            {
                "number": 2,
                "title": "Substitute T(n-1)",
                "equation": f"T(n-1) = T(n-2) + {c if c != 1 else ''}(n-1)^2 \\\\\n\\text{{Therefore: }} \\\\\nT(n) = T(n-2) + {c if c != 1 else ''}(n-1)^2 + {c if c != 1 else ''}n^2",
                "explanation": "Substitute $T(n-1)$ into $T(n)$."
            },
            {
                "number": 3,
                "title": "Expand Again (Substitute T(n-2))",
                "equation": f"T(n-2) = T(n-3) + {c if c != 1 else ''}(n-2)^2 \\\\\n\\text{{Therefore: }} \\\\\nT(n) = T(n-3) + {c if c != 1 else ''}(n-2)^2 + {c if c != 1 else ''}(n-1)^2 + {c if c != 1 else ''}n^2",
                "explanation": "Substitute $T(n-2)$ to observe the sum of consecutive squares."
            },
            {
                "number": 4,
                "title": "General Pattern (k-th step)",
                "equation": f"T(n) = T(n-k) + {c if c != 1 else ''} \\sum_{{i=0}}^{{k-1}} (n-i)^2",
                "explanation": f"After $k$ substitutions, the non-recursive work is the sum of squares."
            },
            {
                "number": 5,
                "title": "Find the Stopping Condition (Base Case)",
                "equation": f"n - k = {n0} \\implies k = n - {n0}",
                "explanation": f"Calculate the number of levels $k = n - {n0}$."
            },
            {
                "number": 6,
                "title": "Substitute k and Simplify",
                "equation": f"T(n) = T({n0}) + {c if c != 1 else ''} \\sum_{{i={n0}+1}}^{{n}} i^2 \\\\\n\\text{{Using }} \\sum_{{i=1}}^n i^2 = \\frac{{n(n+1)(2n+1)}}{{6}}: \\\\\nT(n) = {b0} + \\frac{{{c}n(n+1)(2n+1)}}{{6}} - O(1) = \\frac{{{c}}}{{3}}n^3 + O(n^2)",
                "explanation": "Apply the sum of squares identity $\\sum_{{i=1}}^n i^2 = \\frac{{n(n+1)(2n+1)}}{{6}}$."
            },
            {
                "number": 7,
                "title": "Final Complexity",
                "equation": "T(n) = \\Theta(n^3)",
                "explanation": "Summing $n$ squared terms $\\sum_{{i=1}}^n i^2$ yields $\\frac{{n^3}}{{3}} + O(n^2) = \\Theta(n^3)$."
            }
        ]

        return {
            "supported": True,
            "recurrence": rec_str,
            "base_case": f"T({n0}) = {b0}",
            "base_case_assumed": not is_explicit_base,
            "base_case_note": base_note,
            "type_name": "Quadratic Growth Decrement Recurrence (Substitution Method)",
            "steps": steps,
            "exact_solution": f"T(n) = \\frac{{{c}n(n+1)(2n+1)}}{{6}}",
            "num_levels": f"k = n - {n0}",
            "complexity": "Θ(n³)",
            "complexity_latex": "\\Theta(n^3)",
            "big_o": "O(n^3)",
            "big_theta": "\\Theta(n^3)",
            "big_omega": "\\Omega(n^3)",
            "complexity_explanation": "Summing quadratic work across $n$ decrement levels results in $\\sum_{i=1}^n i^2 = \\Theta(n^3)$.",
            "method": "Substitution Method"
        }

    # 4. T(n) = T(n-1) + log n (Logarithmic Decrement)
    if a == 1 and step == 1 and fn_type == "log_n":
        steps = [
            {
                "number": 1,
                "title": "Write the Original Recurrence",
                "equation": f"T(n) = T(n-1) + \\log n",
                "explanation": f"Write the original recurrence relation. {base_note}"
            },
            {
                "number": 2,
                "title": "Substitute T(n-1)",
                "equation": f"T(n-1) = T(n-2) + \\log(n-1) \\\\\n\\text{{Therefore: }} \\\\\nT(n) = T(n-2) + \\log(n-1) + \\log n",
                "explanation": "Substitute $T(n-1)$ into $T(n)$."
            },
            {
                "number": 3,
                "title": "Expand Again (Substitute T(n-2))",
                "equation": f"T(n-2) = T(n-3) + \\log(n-2) \\\\\n\\text{{Therefore: }} \\\\\nT(n) = T(n-3) + \\log(n-2) + \\log(n-1) + \\log n",
                "explanation": "Substitute $T(n-2)$ to confirm the sum of logarithms."
            },
            {
                "number": 4,
                "title": "General Pattern (k-th step)",
                "equation": f"T(n) = T(n-k) + \\sum_{{i=0}}^{{k-1}} \\log(n-i)",
                "explanation": "After $k$ steps, express the total work as the sum of logarithms."
            },
            {
                "number": 5,
                "title": "Find the Stopping Condition (Base Case)",
                "equation": f"n - k = {n0} \\implies k = n - {n0}",
                "explanation": f"Set inner subproblem size equal to ${n0}$."
            },
            {
                "number": 6,
                "title": "Substitute k and Simplify",
                "equation": f"T(n) = T({n0}) + \\sum_{{i={n0}+1}}^{{n}} \\log i = {b0} + \\log(n!) \\\\\n\\text{{By Stirling's approximation: }} \\log(n!) = n \\log n - n + O(\\log n)",
                "explanation": "Using Stirling's approximation, the sum $\\sum_{{i=1}}^n \\log i = \\log(n!) = \\Theta(n \\log n)$."
            },
            {
                "number": 7,
                "title": "Final Complexity",
                "equation": "T(n) = \\Theta(n \\log n)",
                "explanation": "The sum $\\sum_{{i=1}}^n \\log i = \\log(n!) = \\Theta(n \\log n)$ by Stirling's approximation."
            }
        ]

        return {
            "supported": True,
            "recurrence": rec_str,
            "base_case": f"T({n0}) = {b0}",
            "base_case_assumed": not is_explicit_base,
            "base_case_note": base_note,
            "type_name": "Logarithmic Decrement Recurrence (Substitution Method)",
            "steps": steps,
            "exact_solution": f"T(n) = \\log(n!) + {b0}",
            "num_levels": f"k = n - {n0}",
            "complexity": "Θ(n log n)",
            "complexity_latex": "\\Theta(n \\log n)",
            "big_o": "O(n \\log n)",
            "big_theta": "\\Theta(n \\log n)",
            "big_omega": "\\Omega(n \\log n)",
            "complexity_explanation": "Summing logarithmic work across $n$ decrement steps gives $\\sum_{i=1}^n \\log i = \\log(n!) = \\Theta(n \\log n)$ by Stirling's approximation.",
            "method": "Substitution Method"
        }

    # 5. T(n) = a*T(n-1) + c (Exponential Decrement e.g. Tower of Hanoi: 2T(n-1) + 1)
    if a > 1 and step == 1 and fn_type == "const":
        c_val = c
        steps = [
            {
                "number": 1,
                "title": "Write the Original Recurrence",
                "equation": f"T(n) = {a}T(n-1) + {c_val}",
                "explanation": f"Write the original recurrence relation. {base_note}"
            },
            {
                "number": 2,
                "title": "Substitute T(n-1)",
                "equation": f"T(n-1) = {a}T(n-2) + {c_val} \\\\\n\\text{{Therefore: }} \\\\\nT(n) = {a}[{a}T(n-2) + {c_val}] + {c_val} = {a**2}T(n-2) + {a*c_val + c_val}",
                "explanation": f"Substitute $T(n-1)$ into $T(n)$ and distribute the coefficient ${a}$."
            },
            {
                "number": 3,
                "title": "Expand Again (Substitute T(n-2))",
                "equation": f"T(n-2) = {a}T(n-3) + {c_val} \\\\\n\\text{{Therefore: }} \\\\\nT(n) = {a**2}[{a}T(n-3) + {c_val}] + {a*c_val + c_val} = {a**3}T(n-3) + {a**2*c_val + a*c_val + c_val}",
                "explanation": "Substitute $T(n-2)$ to observe the geometric progression of cost terms."
            },
            {
                "number": 4,
                "title": "General Pattern (k-th step)",
                "equation": f"T(n) = {a}^k T(n-k) + {c_val} \\sum_{{i=0}}^{{k-1}} {a}^i = {a}^k T(n-k) + {c_val} \\cdot \\frac{{{a}^k - 1}}{{{a} - 1}}",
                "explanation": f"Using geometric series sum $\\sum_{{i=0}}^{{k-1}} {a}^i = \\frac{{{a}^k - 1}}{{{a} - 1}}$, formulate the general $k$-th pattern."
            },
            {
                "number": 5,
                "title": "Find the Stopping Condition (Base Case)",
                "equation": f"n - k = {n0} \\implies k = n - {n0}",
                "explanation": f"Set $n - k = {n0}$ to find $k = n - {n0}$."
            },
            {
                "number": 6,
                "title": "Substitute k and Simplify",
                "equation": f"T(n) = {a}^{{n-{n0}}} T({n0}) + {c_val} \\cdot \\frac{{{a}^{{n-{n0}}} - 1}}{{{a} - 1}} \\\\\n\\text{{Since }} T({n0}) = {b0}: \\\\\nT(n) = {b0} \\cdot {a}^{{n-{n0}}} + {c_val} \\cdot \\frac{{{a}^{{n-{n0}}} - 1}}{{{a} - 1}}",
                "explanation": f"Substitute $k = n - {n0}$ and replace $T({n0})$ with ${b0}$."
            },
            {
                "number": 7,
                "title": "Final Complexity",
                "equation": f"T(n) = \\Theta({a}^n)",
                "explanation": f"There are $n - {n0}$ levels of recursion, and the number of subproblems multiplies by ${a}$ at each step. Total work is a geometric series summing to $\\Theta({a}^n)$."
            }
        ]

        if a == 2 and c_val == 1 and n0 == 1 and b0 == 1:
            exact_str = "T(n) = 2^n - 1"
        else:
            exact_str = f"T(n) = {b0} \\cdot {a}^{{n-{n0}}} + \\frac{{{c_val}({a}^{{n-{n0}}} - 1)}}{{{a-1}}}"

        explanation = f"There are $n - {n0}$ substitution levels, and each step multiplies the recursive calls by ${a}$. Summing the geometric series across all levels gives $\\Theta({a}^n)$."

        return {
            "supported": True,
            "recurrence": rec_str,
            "base_case": f"T({n0}) = {b0}",
            "base_case_assumed": not is_explicit_base,
            "base_case_note": base_note,
            "type_name": "Exponential Decrement Recurrence (Substitution Method)",
            "steps": steps,
            "exact_solution": exact_str,
            "num_levels": f"k = n - {n0}",
            "complexity": f"Θ({a}^n)",
            "complexity_latex": f"\\Theta({a}^n)",
            "big_o": f"O({a}^n)",
            "big_theta": f"\\Theta({a}^n)",
            "big_omega": f"\\Omega({a}^n)",
            "complexity_explanation": explanation,
            "method": "Substitution Method"
        }

    # 6. General T(n-step) + c
    if a == 1 and step > 1 and fn_type == "const":
        c_val = c
        steps = [
            {
                "number": 1,
                "title": "Write the Original Recurrence",
                "equation": f"T(n) = T(n - {step}) + {c_val}",
                "explanation": f"Write the original recurrence relation. {base_note}"
            },
            {
                "number": 2,
                "title": f"Substitute T(n - {step})",
                "equation": f"T(n - {step}) = T(n - {2*step}) + {c_val} \\\\\n\\text{{Therefore: }} \\\\\nT(n) = T(n - {2*step}) + {2*c_val}",
                "explanation": f"Substitute $T(n - {step})$ into $T(n)$."
            },
            {
                "number": 3,
                "title": f"Expand Again (Substitute T(n - {2*step}))",
                "equation": f"T(n - {2*step}) = T(n - {3*step}) + {c_val} \\\\\n\\text{{Therefore: }} \\\\\nT(n) = T(n - {3*step}) + {3*c_val}",
                "explanation": "Substitute again to confirm constant accumulation."
            },
            {
                "number": 4,
                "title": "General Pattern (k-th step)",
                "equation": f"T(n) = T(n - {step}k) + {c_val}k",
                "explanation": f"After $k$ steps of size ${step}$, the relation is $T(n - {step}k) + {c_val}k$."
            },
            {
                "number": 5,
                "title": "Find the Stopping Condition (Base Case)",
                "equation": f"n - {step}k = {n0} \\implies k = \\frac{{n - {n0}}}{{{step}}}",
                "explanation": f"Solve for $k$ to reach base argument ${n0}$."
            },
            {
                "number": 6,
                "title": "Substitute k and Simplify",
                "equation": f"T(n) = T({n0}) + {c_val} \\cdot \\left(\\frac{{n - {n0}}}{{{step}}}\\right) = {b0} + \\frac{{{c_val}}}{{{step}}}(n - {n0})",
                "explanation": f"Substitute $k$ and replace $T({n0})$ with ${b0}$."
            },
            {
                "number": 7,
                "title": "Final Complexity",
                "equation": "T(n) = \\Theta(n)",
                "explanation": f"There are $\\frac{{n - {n0}}}{{{step}}}$ levels of substitution, giving a linear complexity of $\\Theta(n)$."
            }
        ]

        return {
            "supported": True,
            "recurrence": rec_str,
            "base_case": f"T({n0}) = {b0}",
            "base_case_assumed": not is_explicit_base,
            "base_case_note": base_note,
            "type_name": f"Step-{step} Decrement Recurrence (Substitution Method)",
            "steps": steps,
            "exact_solution": f"T(n) = \\frac{{{c_val}}}{{{step}}}n + O(1)",
            "num_levels": f"k = \\frac{{n - {n0}}}{{{step}}}",
            "complexity": "Θ(n)",
            "complexity_latex": "\\Theta(n)",
            "big_o": "O(n)",
            "big_theta": "\\Theta(n)",
            "big_omega": "\\Omega(n)",
            "complexity_explanation": f"There are $(n - {n0})/{step}$ levels, each contributing ${c_val}$ work. Total work is linear: $\\Theta(n)$.",
            "method": "Substitution Method"
        }

    # Fallback for unsupported decrement forms
    return {
        "supported": False,
        "error_message": "This recurrence is currently outside the supported substitution patterns.",
        "suggested_examples": ["T(n) = T(n-1) + 1", "T(n) = T(n-1) + n", "T(n) = 2T(n-1) + 1"]
    }


def _solve_divide(a: int, b: int, fn: dict, n0: int, b0: int, is_explicit_base: bool, rec_str: str) -> dict:
    """
    Handles divide-and-conquer recurrences of the form:
    T(n) = a*T(n/b) + f(n)
    """
    fn_type = fn["type"]
    c = fn.get("coeff", 1)
    deg = fn.get("deg", 0)
    log_deg = fn.get("log_deg", 0)

    log_b_str = f"\\log_{{{b}}} n" if b != 2 else "\\log_2 n"
    log_b_plain = f"log_{b} n" if b != 2 else "log n"
    base_note = f"Base case: $T({n0}) = {b0}$." if is_explicit_base else f"Base case not specified; assuming standard boundary condition $T({n0}) = {b0}$."

    # 1. T(n) = T(n/b) + c (e.g. Binary Search: T(n/2) + 1)
    if a == 1 and fn_type == "const":
        c_val = c
        steps = [
            {
                "number": 1,
                "title": "Write the Original Recurrence",
                "equation": f"T(n) = T(n/{b}) + {c_val}",
                "explanation": f"Write the original recurrence relation. {base_note}"
            },
            {
                "number": 2,
                "title": f"Substitute T(n/{b})",
                "equation": f"T(n/{b}) = T(n/{b**2}) + {c_val} \\\\\n\\text{{Therefore: }} \\\\\nT(n) = [T(n/{b**2}) + {c_val}] + {c_val} = T(n/{b**2}) + {2*c_val}",
                "explanation": f"Substitute $T(n/{b})$ into $T(n)$ and simplify."
            },
            {
                "number": 3,
                "title": f"Expand Again (Substitute T(n/{b**2}))",
                "equation": f"T(n/{b**2}) = T(n/{b**3}) + {c_val} \\\\\n\\text{{Therefore: }} \\\\\nT(n) = [T(n/{b**3}) + {c_val}] + {2*c_val} = T(n/{b**3}) + {3*c_val}",
                "explanation": "Substitute again to identify how the constant work accumulates across division levels."
            },
            {
                "number": 4,
                "title": "General Pattern (k-th step)",
                "equation": f"T(n) = T(n/{b}^k) + {c_val}k",
                "explanation": f"After $k$ successive divisions, express $T(n)$ as $T(n/{b}^k) + {c_val}k$."
            },
            {
                "number": 5,
                "title": "Find the Stopping Condition (Base Case)",
                "equation": f"\\frac{{n}}{{{b}^k}} = {n0} \\implies {b}^k = \\frac{{n}}{{{n0}}} \\implies k = \\log_{{{b}}} \\left(\\frac{{n}}{{{n0}}}\\right) = {log_b_str}",
                "explanation": f"Set the inner subproblem size to base case index ${n0}$ to solve for recursion depth $k = {log_b_str}$."
            },
            {
                "number": 6,
                "title": "Substitute k and Simplify",
                "equation": f"T(n) = T({n0}) + {f'{c_val}' if c_val != 1 else ''}{log_b_str} \\\\\n\\text{{Since }} T({n0}) = {b0}: \\\\\nT(n) = {b0} + {f'{c_val}' if c_val != 1 else ''}{log_b_str}",
                "explanation": f"Substitute $k = {log_b_str}$ and replace $T({n0})$ with ${b0}$."
            },
            {
                "number": 7,
                "title": "Final Complexity",
                "equation": "T(n) = \\Theta(\\log n)",
                "explanation": f"There are ${log_b_str}$ levels of substitution, and each level contributes ${c_val}$ constant work. Total work is ${c_val} \\times {log_b_str} = \\Theta(\\log n)$."
            }
        ]

        c_disp = f"{c_val}" if c_val != 1 else ""
        exact_str = f"T(n) = {b0} + {c_disp}{log_b_str}" if n0 == 1 else f"T(n) = {b0} + {c_disp}\\log_{{{b}}} (n/{n0})"
        explanation = f"There are ${log_b_str}$ levels of substitution, and each level contributes a constant work of ${c_val}$. Therefore, total work $= {c_val} \\times {log_b_str} = \\Theta(\\log n)$."

        return {
            "supported": True,
            "recurrence": rec_str,
            "base_case": f"T({n0}) = {b0}",
            "base_case_assumed": not is_explicit_base,
            "base_case_note": base_note,
            "type_name": "Logarithmic Divide-and-Conquer (Substitution Method)",
            "steps": steps,
            "exact_solution": exact_str,
            "num_levels": f"k = {log_b_str}",
            "complexity": "Θ(log n)",
            "complexity_latex": "\\Theta(\\log n)",
            "big_o": "O(\\log n)",
            "big_theta": "\\Theta(\\log n)",
            "big_omega": "\\Omega(\\log n)",
            "complexity_explanation": explanation,
            "method": "Substitution Method"
        }

    # 2. T(n) = a*T(n/b) + c with a > 1 (e.g. 2T(n/2) + 1, 3T(n/2) + 1, 2T(n/3) + 1)
    if a > 1 and fn_type == "const":
        c_val = c
        log_b_a = math.log(a, b)
        if log_b_a.is_integer():
            log_power = int(log_b_a)
            log_str = "n" if log_power == 1 else f"n^{{{log_power}}}"
            log_plain = "n" if log_power == 1 else f"n^{log_power}"
        else:
            log_str = f"n^{{\\log_{{{b}}} {a}}}"
            log_plain = f"n^(log_{b} {a})"

        steps = [
            {
                "number": 1,
                "title": "Write the Original Recurrence",
                "equation": f"T(n) = {a}T(n/{b}) + {c_val}",
                "explanation": f"Write the original recurrence relation. {base_note}"
            },
            {
                "number": 2,
                "title": f"Substitute T(n/{b})",
                "equation": f"T(n/{b}) = {a}T(n/{b**2}) + {c_val} \\\\\n\\text{{Therefore: }} \\\\\nT(n) = {a}[{a}T(n/{b**2}) + {c_val}] + {c_val} = {a**2}T(n/{b**2}) + {a*c_val + c_val}",
                "explanation": f"Substitute $T(n/{b})$ into $T(n)$ and distribute the coefficient ${a}$."
            },
            {
                "number": 3,
                "title": f"Expand Again (Substitute T(n/{b**2}))",
                "equation": f"T(n/{b**2}) = {a}T(n/{b**3}) + {c_val} \\\\\n\\text{{Therefore: }} \\\\\nT(n) = {a**2}[{a}T(n/{b**3}) + {c_val}] + {a*c_val + c_val} = {a**3}T(n/{b**3}) + {a**2*c_val + a*c_val + c_val}",
                "explanation": "Substitute again to reveal the geometric progression of subproblem costs."
            },
            {
                "number": 4,
                "title": "General Pattern (k-th step)",
                "equation": f"T(n) = {a}^k T(n/{b}^k) + {c_val} \\sum_{{i=0}}^{{k-1}} {a}^i = {a}^k T(n/{b}^k) + {c_val} \\cdot \\frac{{{a}^k - 1}}{{{a} - 1}}",
                "explanation": f"Summing the geometric series $\\sum_{{i=0}}^{{k-1}} {a}^i = \\frac{{{a}^k - 1}}{{{a}-1}}$ after $k$ recursive divisions."
            },
            {
                "number": 5,
                "title": "Find the Stopping Condition (Base Case)",
                "equation": f"\\frac{{n}}{{{b}^k}} = 1 \\implies {b}^k = n \\implies k = {log_b_str}",
                "explanation": f"Solve for recursion depth $k = {log_b_str}$."
            },
            {
                "number": 6,
                "title": "Substitute k and Simplify",
                "equation": f"T(n) = {a}^{{{log_b_str}}} T(1) + {c_val} \\cdot \\frac{{{a}^{{{log_b_str}}} - 1}}{{{a} - 1}} \\\\\n\\text{{Using }} {a}^{{{log_b_str}}} = n^{{\\log_{{{b}}} {a}}} = {log_str}: \\\\\nT(n) = {b0} \\cdot {log_str} + {c_val} \\cdot \\frac{{{log_str} - 1}}{{{a} - 1}}",
                "explanation": f"Using identity $a^{{\\log_b n}} = n^{{\\log_b a}}$, derive the closed form."
            },
            {
                "number": 7,
                "title": "Final Complexity",
                "equation": f"T(n) = \\Theta({log_str})",
                "explanation": f"There are ${log_b_str}$ levels. The number of leaf subproblems is $a^{{{log_b_str}}} = {log_str}$, which dominates the runtime, giving $\\Theta({log_str})$."
            }
        ]

        explanation = f"There are ${log_b_str}$ levels of substitution. The branching factor is $a = {a}$, so the number of subproblems at the base case leaves is $a^{{{log_b_str}}} = n^{{\\log_{{{b}}} {a}}} = {log_str}$. The leaf work dominates, giving $\\Theta({log_str})$."

        return {
            "supported": True,
            "recurrence": rec_str,
            "base_case": f"T({n0}) = {b0}",
            "base_case_assumed": not is_explicit_base,
            "base_case_note": base_note,
            "type_name": "Divide-and-Conquer (Branching with Constant Work)",
            "steps": steps,
            "exact_solution": f"T(n) = {b0} \\cdot {log_str} + \\frac{{{c_val}({log_str} - 1)}}{{{a - 1}}}",
            "num_levels": f"k = {log_b_str}",
            "complexity": f"Θ({log_plain})",
            "complexity_latex": f"\\Theta({log_str})",
            "big_o": f"O({log_str})",
            "big_theta": f"\\Theta({log_str})",
            "big_omega": f"\\Omega({log_str})",
            "complexity_explanation": explanation,
            "method": "Substitution Method"
        }

    # 3. T(n) = a*T(n/b) + c*n*log^d n (Linearithmic combine cost, e.g. 2T(n/2) + n log n)
    if fn_type == "n_log_n":
        c_val = c
        if a == b:
            # e.g. 2T(n/2) + n log n -> Theta(n log^2 n)
            target_log_pow = log_deg + 1
            tex_pow = f"^{{{target_log_pow}}}" if target_log_pow > 1 else ""
            plain_pow = f"^{target_log_pow}" if target_log_pow > 1 else ""

            steps = [
                {
                    "number": 1,
                    "title": "Write the Original Recurrence",
                    "equation": f"T(n) = {a}T(n/{b}) + {f'{c_val}' if c_val != 1 else ''}n \\log n",
                    "explanation": f"Write the original recurrence relation. {base_note}"
                },
                {
                    "number": 2,
                    "title": f"Substitute T(n/{b})",
                    "equation": f"T(n/{b}) = {a}T(n/{b**2}) + {f'{c_val}' if c_val != 1 else ''}\\frac{{n}}{{{b}}} \\log(n/{b}) \\\\\n\\text{{Therefore: }} \\\\\nT(n) = {a}\\left[{a}T(n/{b**2}) + {f'{c_val}' if c_val != 1 else ''}\\frac{{n}}{{{b}}} \\log(n/{b})\\right] + {f'{c_val}' if c_val != 1 else ''}n \\log n \\\\\n= {a**2}T(n/{b**2}) + {f'{c_val}' if c_val != 1 else ''}n [\\log(n/{b}) + \\log n]",
                    "explanation": f"Substitute $T(n/{b})$ into $T(n)$ and distribute coefficient ${a}$."
                },
                {
                    "number": 3,
                    "title": f"Expand Again (Substitute T(n/{b**2}))",
                    "equation": f"T(n/{b**2}) = {a}T(n/{b**3}) + {f'{c_val}' if c_val != 1 else ''}\\frac{{n}}{{{b**2}}} \\log(n/{b**2}) \\\\\n\\text{{Therefore: }} \\\\\nT(n) = {a**3}T(n/{b**3}) + {f'{c_val}' if c_val != 1 else ''}n [\\log(n/{b**2}) + \\log(n/{b}) + \\log n]",
                    "explanation": "Substitute again to establish the sum of logarithmic work across levels."
                },
                {
                    "number": 4,
                    "title": "General Pattern (k-th step)",
                    "equation": f"T(n) = {a}^k T(n/{b}^k) + {f'{c_val}' if c_val != 1 else ''}n \\sum_{{i=0}}^{{k-1}} \\log(n/{b}^i) = {a}^k T(n/{b}^k) + {f'{c_val}' if c_val != 1 else ''}n \\left[ k \\log n - \\frac{{k(k-1)}}{{2}} \\log {b} \\right]",
                    "explanation": "After $k$ levels, each of the $k$ levels contributes $n \\log(n/b^i)$ work."
                },
                {
                    "number": 5,
                    "title": "Find the Stopping Condition (Base Case)",
                    "equation": f"\\frac{{n}}{{{b}^k}} = 1 \\implies k = {log_b_str}",
                    "explanation": f"Solve for tree depth $k = {log_b_str}$."
                },
                {
                    "number": 6,
                    "title": "Substitute k and Simplify",
                    "equation": f"T(n) = {a}^{{{log_b_str}}} T(1) + {f'{c_val}' if c_val != 1 else ''}n \\left[ ({log_b_str}) \\log n - \\frac{{{log_b_str}({log_b_str}-1)}}{{2}} \\log {b} \\right] \\\\\n= {b0}n + \\frac{{{f'{c_val}' if c_val != 1 else ''}}}{{2}} n \\log_{{{b}}}^2 n + O(n \\log n)",
                    "explanation": f"Substitute $k = {log_b_str}$ and simplify the arithmetic progression of logarithmic terms."
                },
                {
                    "number": 7,
                    "title": "Final Complexity",
                    "equation": f"T(n) = \\Theta(n \\log{tex_pow} n)",
                    "explanation": f"There are ${log_b_str}$ levels, and the average combine work per level is $\\Theta(n \\log n)$. Multiplying yields $\\Theta(n \\log{tex_pow} n)$."
                }
            ]

            explanation = f"There are ${log_b_str}$ levels of substitution. At each level $i$, the work is $a^i \\times \\frac{{n}}{{b^i}} \\log(n/b^i) = n(\\log n - i \\log b)$. Summing across all ${log_b_str}$ levels gives $\\sum_{{i=0}}^{{k-1}} n(\\log n - i) = \\Theta(n \\log{tex_pow} n)$."

            return {
                "supported": True,
                "recurrence": rec_str,
                "base_case": f"T({n0}) = {b0}",
                "base_case_assumed": not is_explicit_base,
                "base_case_note": base_note,
                "type_name": "Linearithmic Divide-and-Conquer (Substitution Method)",
                "steps": steps,
                "exact_solution": f"T(n) = \\frac{{{f'{c_val}' if c_val != 1 else ''}}}{{2}} n \\log_{{{b}}}^2 n + O(n \\log n)",
                "num_levels": f"k = {log_b_str}",
                "complexity": f"Θ(n log{plain_pow} n)",
                "complexity_latex": f"\\Theta(n \\log{tex_pow} n)",
                "big_o": f"O(n \\log{tex_pow} n)",
                "big_theta": f"\\Theta(n \\log{tex_pow} n)",
                "big_omega": f"\\Omega(n \\log{tex_pow} n)",
                "complexity_explanation": explanation,
                "method": "Substitution Method"
            }

    # 4. T(n) = a*T(n/b) + c*n (Linear combine cost, e.g. 2T(n/2) + n, 3T(n/2) + n, T(n/3) + n, 2T(n/3) + n)
    if fn_type == "poly" and deg == 1:
        c_n_str = f"{c}n" if c != 1 else "n"

        # Case A: a == b (Balanced Divide-and-Conquer, e.g. 2T(n/2) + n MergeSort)
        if a == b:
            steps = [
                {
                    "number": 1,
                    "title": "Write the Original Recurrence",
                    "equation": f"T(n) = {a}T(n/{b}) + {c_n_str}",
                    "explanation": f"Write the original recurrence relation. {base_note}"
                },
                {
                    "number": 2,
                    "title": f"Substitute T(n/{b})",
                    "equation": f"T(n/{b}) = {a}T(n/{b**2}) + {c}(n/{b}) \\\\\n\\text{{Therefore: }} \\\\\nT(n) = {a}\\left[{a}T(n/{b**2}) + {c}(n/{b})\\right] + {c_n_str} = {a**2}T(n/{b**2}) + {2*c}n",
                    "explanation": f"Substitute $T(n/{b})$ into $T(n)$ and simplify the linear combine cost."
                },
                {
                    "number": 3,
                    "title": f"Expand Again (Substitute T(n/{b**2}))",
                    "equation": f"T(n/{b**2}) = {a}T(n/{b**3}) + {c}(n/{b**2}) \\\\\n\\text{{Therefore: }} \\\\\nT(n) = {a**2}\\left[{a}T(n/{b**3}) + {c}(n/{b**2})\\right] + {2*c}n = {a**3}T(n/{b**3}) + {3*c}n",
                    "explanation": f"Substitute $T(n/{b**2})$ to observe that every recursion level contributes exactly ${c}n$ work."
                },
                {
                    "number": 4,
                    "title": "General Pattern (k-th step)",
                    "equation": f"T(n) = {a}^k T(n/{b}^k) + k \\cdot {c_n_str}",
                    "explanation": f"After $k$ successive substitutions, the formula is ${a}^k T(n/{b}^k) + k \\cdot {c_n_str}$."
                },
                {
                    "number": 5,
                    "title": "Find the Stopping Condition (Base Case)",
                    "equation": f"\\frac{{n}}{{{b}^k}} = 1 \\implies {b}^k = n \\implies k = {log_b_str}",
                    "explanation": f"Solve for recursion depth $k = {log_b_str}$."
                },
                {
                    "number": 6,
                    "title": "Substitute k and Simplify",
                    "equation": f"T(n) = {a}^{{{log_b_str}}} T(1) + ({log_b_str}) \\cdot {c_n_str} \\\\\n\\text{{Using }} {a}^{{{log_b_str}}} = n^{{\\log_{{{b}}} {a}}} = n^1 = n \\text{{ and }} T(1) = {b0}: \\\\\nT(n) = {f'{b0}n' if b0 != 1 else 'n'} + {f'{c}n' if c != 1 else 'n'} {log_b_str}",
                    "explanation": f"Using identity $a^{{\\log_b n}} = n$, substitute $k$ and replace $T(1)$ with ${b0}$."
                },
                {
                    "number": 7,
                    "title": "Final Complexity",
                    "equation": "T(n) = \\Theta(n \\log n)",
                    "explanation": f"There are ${log_b_str}$ levels of substitution, and each level contributes ${c}n$ work. Therefore: $n \\times {log_b_str} = \\Theta(n \\log n)$."
                }
            ]

            term1 = f"{c}n {log_b_str}" if c != 1 else f"n {log_b_str}"
            term2 = f" + {b0}n" if b0 != 0 and b0 != 1 else (" + n" if b0 == 1 else "")
            exact_str = f"T(n) = {term1}{term2}"
            explanation = f"There are ${log_b_str}$ levels of substitution, and each level contributes $n$ work. Therefore: $n \\times {log_b_str} = \\Theta(n \\log n)$."

            return {
                "supported": True,
                "recurrence": rec_str,
                "base_case": f"T({n0}) = {b0}",
                "base_case_assumed": not is_explicit_base,
                "base_case_note": base_note,
                "type_name": "Balanced Divide-and-Conquer (Substitution Method)",
                "steps": steps,
                "exact_solution": exact_str,
                "num_levels": f"k = {log_b_str}",
                "complexity": "Θ(n log n)",
                "complexity_latex": "\\Theta(n \\log n)",
                "big_o": "O(n \\log n)",
                "big_theta": "\\Theta(n \\log n)",
                "big_omega": "\\Omega(n \\log n)",
                "complexity_explanation": explanation,
                "method": "Substitution Method"
            }

        # Case B: a > b (Leaf-dominant, e.g. 3T(n/2) + n, 4T(n/2) + n, 4T(n/3) + n)
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
                    "title": "Write the Original Recurrence",
                    "equation": f"T(n) = {a}T(n/{b}) + {c_n_str}",
                    "explanation": f"Write the original recurrence relation. {base_note}"
                },
                {
                    "number": 2,
                    "title": f"Substitute T(n/{b})",
                    "equation": f"T(n/{b}) = {a}T(n/{b**2}) + {c}(n/{b}) \\\\\n\\text{{Therefore: }} \\\\\nT(n) = {a}\\left[{a}T(n/{b**2}) + {c}(n/{b})\\right] + {c_n_str} = {a**2}T(n/{b**2}) + {c}n\\left(1 + \\frac{{{a}}}{{{b}}}\\right)",
                    "explanation": f"Substitute $T(n/{b})$ into $T(n)$ and factor ${c}n$."
                },
                {
                    "number": 3,
                    "title": f"Expand Again (Substitute T(n/{b**2}))",
                    "equation": f"T(n/{b**2}) = {a}T(n/{b**3}) + {c}(n/{b**2}) \\\\\n\\text{{Therefore: }} \\\\\nT(n) = {a**3}T(n/{b**3}) + {c}n\\left(1 + \\frac{{{a}}}{{{b}}} + \\left(\\frac{{{a}}}{{{b}}}\\right)^2\\right)",
                    "explanation": f"Substitute $T(n/{b**2})$ to observe the geometric series with ratio $\\frac{{{a}}}{{{b}}} > 1$."
                },
                {
                    "number": 4,
                    "title": "General Pattern (k-th step)",
                    "equation": f"T(n) = {a}^k T(n/{b}^k) + {c}n \\sum_{{i=0}}^{{k-1}} \\left(\\frac{{{a}}}{{{b}}}\\right)^i = {a}^k T(n/{b}^k) + {c}n \\cdot \\frac{{\\left(\\frac{{{a}}}{{{b}}}\\right)^k - 1}}{{\\frac{{{a}}}{{{b}}} - 1}}",
                    "explanation": f"After $k$ steps, the work is $a^k T(n/b^k)$ plus a growing geometric series."
                },
                {
                    "number": 5,
                    "title": "Find the Stopping Condition (Base Case)",
                    "equation": f"\\frac{{n}}{{{b}^k}} = 1 \\implies k = {log_b_str}",
                    "explanation": f"Solve for recursion depth $k = {log_b_str}$."
                },
                {
                    "number": 6,
                    "title": "Substitute k and Simplify",
                    "equation": f"T(n) = {a}^{{{log_b_str}}} T(1) + {c}n \\cdot \\frac{{ (n/{b})^{{\\log_{{{b}}} (a/b)}} - 1 }}{{\\frac{{{a}}}{{{b}}} - 1}} \\\\\n\\text{{Since }} {a}^{{{log_b_str}}} = {leaf_work_str} \\text{{ and }} a > b, \\text{{ the leaf work strictly dominates.}}",
                    "explanation": f"Because branching factor $a = {a} > b = {b}$, the number of subproblems at the leaf level dominates the runtime."
                },
                {
                    "number": 7,
                    "title": "Final Complexity",
                    "equation": f"T(n) = {complexity_str}",
                    "explanation": f"There are ${log_b_str}$ levels. Since $a = {a} > b = {b}$, the geometric ratio is $\\frac{{{a}}}{{{b}}} > 1$. The total work is dominated by the leaf level ${leaf_work_str}$, giving ${complexity_str}$."
                }
            ]

            explanation = f"There are ${log_b_str}$ levels of substitution. Since the branching factor $a = {a}$ is strictly greater than the division factor $b = {b}$, the work grows geometrically across levels by ratio $\\frac{{{a}}}{{{b}}} > 1$. The leaf level work $a^{{{log_b_str}}} = {leaf_work_str}$ dominates, yielding ${complexity_str}$."

            return {
                "supported": True,
                "recurrence": rec_str,
                "base_case": f"T({n0}) = {b0}",
                "base_case_assumed": not is_explicit_base,
                "base_case_note": base_note,
                "type_name": "Leaf-Dominant Divide-and-Conquer (Substitution Method)",
                "steps": steps,
                "exact_solution": f"T(n) = \\Theta({leaf_work_str})",
                "num_levels": f"k = {log_b_str}",
                "complexity": complexity_plain,
                "complexity_latex": complexity_str,
                "big_o": f"O({leaf_work_str})",
                "big_theta": complexity_str,
                "big_omega": f"\\Omega({leaf_work_str})",
                "complexity_explanation": explanation,
                "method": "Substitution Method"
            }

        # Case C: a < b (Root-dominant, e.g. T(n/2) + n, T(n/3) + n, 2T(n/3) + n)
        else:
            steps = [
                {
                    "number": 1,
                    "title": "Write the Original Recurrence",
                    "equation": f"T(n) = {a if a != 1 else ''}T(n/{b}) + {c_n_str}",
                    "explanation": f"Write the original recurrence relation. {base_note}"
                },
                {
                    "number": 2,
                    "title": f"Substitute T(n/{b})",
                    "equation": f"T(n/{b}) = {a if a != 1 else ''}T(n/{b**2}) + {c}(n/{b}) \\\\\n\\text{{Therefore: }} \\\\\nT(n) = {a**2 if a != 1 else ''}T(n/{b**2}) + {c}n\\left(1 + \\frac{{{a}}}{{{b}}}\\right)",
                    "explanation": f"Substitute $T(n/{b})$ into $T(n)$ and factor ${c}n$."
                },
                {
                    "number": 3,
                    "title": f"Expand Again (Substitute T(n/{b**2}))",
                    "equation": f"T(n/{b**2}) = {a if a != 1 else ''}T(n/{b**3}) + {c}(n/{b**2}) \\\\\n\\text{{Therefore: }} \\\\\nT(n) = {a**3 if a != 1 else ''}T(n/{b**3}) + {c}n\\left(1 + \\frac{{{a}}}{{{b}}} + \\left(\\frac{{{a}}}{{{b}}}\\right)^2\\right)",
                    "explanation": f"Substitute $T(n/{b**2})$ to observe the decaying geometric series with ratio $\\frac{{{a}}}{{{b}}} < 1$."
                },
                {
                    "number": 4,
                    "title": "General Pattern (k-th step)",
                    "equation": f"T(n) = {a}^k T(n/{b}^k) + {c}n \\sum_{{i=0}}^{{k-1}} \\left(\\frac{{{a}}}{{{b}}}\\right)^i = {a}^k T(n/{b}^k) + {c}n \\cdot \\frac{{1 - (\\frac{{{a}}}{{{b}}})^k}}{{1 - \\frac{{{a}}}{{{b}}}}}",
                    "explanation": f"Since $\\frac{{{a}}}{{{b}}} < 1$, the geometric series is bounded by the constant $\\frac{{1}}{{1 - a/b}}$."
                },
                {
                    "number": 5,
                    "title": "Find the Stopping Condition (Base Case)",
                    "equation": f"\\frac{{n}}{{{b}^k}} = 1 \\implies k = {log_b_str}",
                    "explanation": f"Solve for recursion depth $k = {log_b_str}$."
                },
                {
                    "number": 6,
                    "title": "Substitute k and Simplify",
                    "equation": f"T(n) = {a}^{{{log_b_str}}} T(1) + {c}n \\cdot \\frac{{1 - (\\frac{{{a}}}{{{b}}})^{{{log_b_str}}}}}{{1 - \\frac{{{a}}}{{{b}}}}} = O(n^{{\\log_{{{b}}} {a}}}) + \\frac{{{c}}}{{1 - {a}/{b}}} n = \\Theta(n)",
                    "explanation": f"Because $\\frac{{{a}}}{{{b}}} < 1$, the infinite geometric series sum converges to $\\frac{{1}}{{1 - a/b}}$, so the root work $cn$ dominates."
                },
                {
                    "number": 7,
                    "title": "Final Complexity",
                    "equation": "T(n) = \\Theta(n)",
                    "explanation": f"There are ${log_b_str}$ levels. Since $a = {a} < b = {b}$, the work shrinks geometrically at each level by ratio $\\frac{{{a}}}{{{b}}} < 1$. The root-level work $n$ dominates, giving $\\Theta(n)$."
                }
            ]

            explanation = f"There are ${log_b_str}$ levels of substitution. Since the branching factor $a = {a}$ is strictly less than the division factor $b = {b}$, the combine work decreases geometrically at each level by ratio $\\frac{{{a}}}{{{b}}} < 1$. The sum of the geometric series converges to $\\frac{{1}}{{1 - {a}/{b}}}$, and the top-level linear work $n$ strictly dominates, giving $\\Theta(n)$."

            return {
                "supported": True,
                "recurrence": rec_str,
                "base_case": f"T({n0}) = {b0}",
                "base_case_assumed": not is_explicit_base,
                "base_case_note": base_note,
                "type_name": "Root-Dominant Divide-and-Conquer (Substitution Method)",
                "steps": steps,
                "exact_solution": f"T(n) = \\frac{{{c}}}{{1 - {a}/{b}}}n + O(1)",
                "num_levels": f"k = {log_b_str}",
                "complexity": "Θ(n)",
                "complexity_latex": "\\Theta(n)",
                "big_o": "O(n)",
                "big_theta": "\\Theta(n)",
                "big_omega": "\\Omega(n)",
                "complexity_explanation": explanation,
                "method": "Substitution Method"
            }

    # 5. T(n) = a*T(n/b) + c*n^d (Polynomial combine cost e.g. 2T(n/2) + n^2, 4T(n/2) + n^2, 4T(n/3) + n^2)
    if fn_type == "poly" and deg >= 2:
        b_d = b**deg
        d_power_str = f"^{{{deg}}}" if deg > 1 else ""
        if deg == 2:
            d_plain = "²"
        elif deg == 3:
            d_plain = "³"
        else:
            d_plain = f"^{deg}" if deg > 1 else ""

        if a < b_d:
            # Root dominates: Theta(n^d)
            steps = [
                {
                    "number": 1,
                    "title": "Write the Original Recurrence",
                    "equation": f"T(n) = {a if a != 1 else ''}T(n/{b}) + {c if c != 1 else ''}n{d_power_str}",
                    "explanation": f"Write the original recurrence relation. {base_note}"
                },
                {
                    "number": 2,
                    "title": f"Substitute T(n/{b})",
                    "equation": f"T(n/{b}) = {a if a != 1 else ''}T(n/{b**2}) + {c if c != 1 else ''}(n/{b}){d_power_str} \\\\\n\\text{{Therefore: }} \\\\\nT(n) = {a**2 if a != 1 else ''}T(n/{b**2}) + {c}n{d_power_str}\\left(1 + \\frac{{{a}}}{{{b_d}}}\\right)",
                    "explanation": f"Substitute $T(n/{b})$ into $T(n)$ and factor ${c}n{d_power_str}$."
                },
                {
                    "number": 3,
                    "title": f"Expand Again (Substitute T(n/{b**2}))",
                    "equation": f"T(n/{b**2}) = {a if a != 1 else ''}T(n/{b**3}) + {c if c != 1 else ''}(n/{b**2}){d_power_str} \\\\\n\\text{{Therefore: }} \\\\\nT(n) = {a**3 if a != 1 else ''}T(n/{b**3}) + {c}n{d_power_str}\\left(1 + \\frac{{{a}}}{{{b_d}}} + \\left(\\frac{{{a}}}{{{b_d}}}\\right)^2\\right)",
                    "explanation": f"Substitute $T(n/{b**2})$ to observe the geometric ratio $\\frac{{{a}}}{{{b}^{{{deg}}}}} = \\frac{{{a}}}{{{b_d}}} < 1$."
                },
                {
                    "number": 4,
                    "title": "General Pattern (k-th step)",
                    "equation": f"T(n) = {a}^k T(n/{b}^k) + {c}n{d_power_str} \\sum_{{i=0}}^{{k-1}} \\left(\\frac{{{a}}}{{{b_d}}}\\right)^i",
                    "explanation": f"Since $\\frac{{{a}}}{{{b_d}}} < 1$, the geometric series converges to $\\frac{{1}}{{1 - a/{b_d}}}$."
                },
                {
                    "number": 5,
                    "title": "Find the Stopping Condition (Base Case)",
                    "equation": f"\\frac{{n}}{{{b}^k}} = 1 \\implies k = {log_b_str}",
                    "explanation": f"Solve for recursion depth $k = {log_b_str}$."
                },
                {
                    "number": 6,
                    "title": "Substitute k and Simplify",
                    "equation": f"T(n) = {a}^{{{log_b_str}}} T(1) + {c}n{d_power_str} \\cdot \\frac{{1}}{{1 - {a}/{b_d}}} = \\Theta(n{d_power_str})",
                    "explanation": f"The root level work $n{d_power_str}$ dominates the convergent geometric series."
                },
                {
                    "number": 7,
                    "title": "Final Complexity",
                    "equation": f"T(n) = \\Theta(n{d_power_str})",
                    "explanation": f"There are ${log_b_str}$ levels. Since $a = {a} < b^{{{deg}}} = {b_d}$, the geometric series converges to a constant factor, leaving the root polynomial term $\\Theta(n{d_power_str})$ dominant."
                }
            ]

            explanation = f"There are ${log_b_str}$ levels of substitution. Since $a = {a} < b^{{{deg}}} = {b_d}$, the work decreases geometrically across levels by ratio $\\frac{{{a}}}{{{b_d}}} < 1$. The sum of the geometric series converges to $\\frac{{1}}{{1 - {a}/{b_d}}}$, so the top-level polynomial work $n{d_power_str}$ strictly dominates, yielding $\\Theta(n{d_power_str})$."

            return {
                "supported": True,
                "recurrence": rec_str,
                "base_case": f"T({n0}) = {b0}",
                "base_case_assumed": not is_explicit_base,
                "base_case_note": base_note,
                "type_name": "Root-Dominant Polynomial Divide-and-Conquer (Substitution Method)",
                "steps": steps,
                "exact_solution": f"T(n) = \\Theta(n{d_power_str})",
                "num_levels": f"k = {log_b_str}",
                "complexity": f"Θ(n{d_plain})",
                "complexity_latex": f"\\Theta(n{d_power_str})",
                "big_o": f"O(n{d_power_str})",
                "big_theta": f"\\Theta(n{d_power_str})",
                "big_omega": f"\\Omega(n{d_power_str})",
                "complexity_explanation": explanation,
                "method": "Substitution Method"
            }
        elif a == b_d:
            # Balanced: Theta(n^d log n)
            steps = [
                {
                    "number": 1,
                    "title": "Write the Original Recurrence",
                    "equation": f"T(n) = {a}T(n/{b}) + {c if c != 1 else ''}n{d_power_str}",
                    "explanation": f"Write the original recurrence relation. {base_note}"
                },
                {
                    "number": 2,
                    "title": f"Substitute T(n/{b})",
                    "equation": f"T(n/{b}) = {a}T(n/{b**2}) + {c if c != 1 else ''}(n/{b}){d_power_str} \\\\\n\\text{{Therefore: }} \\\\\nT(n) = {a**2}T(n/{b**2}) + {2*c}n{d_power_str}",
                    "explanation": f"Substitute $T(n/{b})$ into $T(n)$."
                },
                {
                    "number": 3,
                    "title": f"Expand Again (Substitute T(n/{b**2}))",
                    "equation": f"T(n/{b**2}) = {a}T(n/{b**3}) + {c if c != 1 else ''}(n/{b**2}){d_power_str} \\\\\n\\text{{Therefore: }} \\\\\nT(n) = {a**3}T(n/{b**3}) + {3*c}n{d_power_str}",
                    "explanation": f"Each level contributes exactly $n{d_power_str}$ work."
                },
                {
                    "number": 4,
                    "title": "General Pattern (k-th step)",
                    "equation": f"T(n) = {a}^k T(n/{b}^k) + k \\cdot {c if c != 1 else ''}n{d_power_str}",
                    "explanation": f"After $k$ steps, the formula is ${a}^k T(n/{b}^k) + k \\cdot n{d_power_str}$."
                },
                {
                    "number": 5,
                    "title": "Find the Stopping Condition (Base Case)",
                    "equation": f"\\frac{{n}}{{{b}^k}} = 1 \\implies k = {log_b_str}",
                    "explanation": f"Solve for recursion depth $k = {log_b_str}$."
                },
                {
                    "number": 6,
                    "title": "Substitute k and Simplify",
                    "equation": f"T(n) = {a}^{{{log_b_str}}} T(1) + ({log_b_str}) \\cdot n{d_power_str} = {b0}n{d_power_str} + n{d_power_str} {log_b_str}",
                    "explanation": f"Substitute $k = {log_b_str}$ and simplify."
                },
                {
                    "number": 7,
                    "title": "Final Complexity",
                    "equation": f"T(n) = \\Theta(n{d_power_str} \\log n)",
                    "explanation": f"There are ${log_b_str}$ levels, and each level contributes $n{d_power_str}$ work. Summing yields $n{d_power_str} \\times {log_b_str} = \\Theta(n{d_power_str} \\log n)$."
                }
            ]

            explanation = f"There are ${log_b_str}$ levels of substitution, and each level contributes $n{d_power_str}$ work. Therefore: $n{d_power_str} \\times {log_b_str} = \\Theta(n{d_power_str} \\log n)$."

            return {
                "supported": True,
                "recurrence": rec_str,
                "base_case": f"T({n0}) = {b0}",
                "base_case_assumed": not is_explicit_base,
                "base_case_note": base_note,
                "type_name": "Balanced Polynomial Divide-and-Conquer (Substitution Method)",
                "steps": steps,
                "exact_solution": f"T(n) = n{d_power_str} {log_b_str} + O(n{d_power_str})",
                "num_levels": f"k = {log_b_str}",
                "complexity": f"Θ(n{d_plain} log n)",
                "complexity_latex": f"\\Theta(n{d_power_str} \\log n)",
                "big_o": f"O(n{d_power_str} \\log n)",
                "big_theta": f"\\Theta(n{d_power_str} \\log n)",
                "big_omega": f"\\Omega(n{d_power_str} \\log n)",
                "complexity_explanation": explanation,
                "method": "Substitution Method"
            }

    # Fallback for other divide forms
    return {
        "supported": False,
        "error_message": "This recurrence is currently outside the supported substitution patterns.",
        "suggested_examples": [
            "T(n) = 2T(n/2) + n",
            "T(n) = T(n/2) + 1",
            "T(n) = 3T(n/2) + n",
            "T(n) = 2T(n/3) + n",
            "T(n) = 2T(n/2) + n log n"
        ]
    }
