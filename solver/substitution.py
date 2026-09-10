"""
Substitution Method Solver Engine for Recurrence Relations.
Supports step-by-step derivation for common recurrence structures in DAA.
"""

import re
import math


def parse_base_case(base_str: str) -> tuple[int, int]:
    """
    Parses base case string like 'T(1) = 1' or 'T(0) = 5'.
    Returns (n0, T_n0). Defaults to (1, 1) if unspecified or invalid.
    """
    if not base_str or not base_str.strip():
        return (1, 1)
    
    cleaned = base_str.replace(" ", "")
    # Pattern: T(n0) = b0
    match = re.search(r"[T|t]\((\d+)\)\=(\d+)", cleaned)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    
    # Just a number like '1'
    if cleaned.isdigit():
        return (1, int(cleaned))
        
    return (1, 1)


def parse_recurrence(rec_str: str) -> dict:
    """
    Parses a recurrence relation string into structured components.
    Supported forms:
    1. T(n) = T(n-1) + c          (Linear Decrement Additive)
    2. T(n) = a*T(n-1) + c        (Linear Decrement Multiplicative)
    3. T(n) = T(n/b) + c          (Divide & Conquer Logarithmic)
    4. T(n) = a*T(n/b) + c*n      (Divide & Conquer Linear, e.g., MergeSort)
    5. T(n) = a*T(n/b) + c*n^d    (Divide & Conquer Polynomial)
    """
    if not rec_str:
        return {"type": "INVALID", "error": "Please enter a recurrence relation."}

    # Normalize string: remove spaces, lowercase 't'
    s = rec_str.replace(" ", "")
    if "=" in s:
        lhs, rhs = s.split("=", 1)
    else:
        rhs = s

    # 1. Check: T(n) = a*T(n-1) + c  or T(n-1) + c
    # Example: 2T(n-1)+1, T(n-1)+5
    m_dec = re.fullmatch(r"(\d*)[\*]?[T|t]\(n\-1\)\+(\d+)", rhs)
    if m_dec:
        a = int(m_dec.group(1)) if m_dec.group(1) else 1
        c = int(m_dec.group(2))
        if a == 1:
            return {"type": "DEC_ADDITIVE", "a": 1, "c": c}
        else:
            return {"type": "DEC_MULTIPLICATIVE", "a": a, "c": c}

    # Check T(n-1) with subtraction/no constant: T(n) = T(n-1) + 0
    m_dec_simple = re.fullmatch(r"(\d*)[\*]?[T|t]\(n\-1\)", rhs)
    if m_dec_simple:
        a = int(m_dec_simple.group(1)) if m_dec_simple.group(1) else 1
        if a == 1:
            return {"type": "DEC_ADDITIVE", "a": 1, "c": 0}
        else:
            return {"type": "DEC_MULTIPLICATIVE", "a": a, "c": 0}

    # 2. Check Divide & Conquer: a*T(n/b) + ...
    # Examples: T(n/2)+1, 2T(n/2)+n, 4T(n/2)+n, 2T(n/2)+3
    m_div_const = re.fullmatch(r"(\d*)[\*]?[T|t]\(n\/(\d+)\)\+(\d+)", rhs)
    if m_div_const:
        a = int(m_div_const.group(1)) if m_div_const.group(1) else 1
        b = int(m_div_const.group(2))
        c = int(m_div_const.group(3))
        if a == 1:
            return {"type": "DIV_LOG", "a": 1, "b": b, "c": c}
        else:
            return {"type": "DIV_GENERAL_CONST", "a": a, "b": b, "c": c}

    m_div_n = re.fullmatch(r"(\d*)[\*]?[T|t]\(n\/(\d+)\)\+(\d*)[\*]?n", rhs)
    if m_div_n:
        a = int(m_div_n.group(1)) if m_div_n.group(1) else 1
        b = int(m_div_n.group(2))
        c = int(m_div_n.group(3)) if m_div_n.group(3) else 1
        return {"type": "DIV_LINEAR_N", "a": a, "b": b, "c": c}

    # Check T(n/b) without extra term: e.g. T(n) = T(n/2)
    m_div_bare = re.fullmatch(r"(\d*)[\*]?[T|t]\(n\/(\d+)\)", rhs)
    if m_div_bare:
        a = int(m_div_bare.group(1)) if m_div_bare.group(1) else 1
        b = int(m_div_bare.group(2))
        if a == 1:
            return {"type": "DIV_LOG", "a": 1, "b": b, "c": 0}
        else:
            return {"type": "DIV_GENERAL_CONST", "a": a, "b": b, "c": 0}

    return {"type": "UNSUPPORTED", "error": "We couldn't understand that recurrence. Try one of the supported examples below."}


def solve_recurrence(rec_str: str, base_str: str = "T(1) = 1") -> dict:
    """
    Main solver pipeline. Returns a structured JSON dict suitable for Jinja2 template rendering.
    """
    if not rec_str or not rec_str.strip():
        return {
            "supported": False,
            "error_message": "Please enter a recurrence relation.",
            "suggested_examples": [
                "T(n) = T(n-1) + 5",
                "T(n) = T(n/2) + 1",
                "T(n) = 2T(n/2) + n",
                "T(n) = 2T(n-1) + 1"
            ]
        }

    parsed_rec = parse_recurrence(rec_str)
    if parsed_rec.get("type") == "UNSUPPORTED" or parsed_rec.get("type") == "INVALID":
        return {
            "supported": False,
            "error_message": parsed_rec.get("error", "Unsupported recurrence relation format."),
            "suggested_examples": [
                "T(n) = T(n-1) + 5",
                "T(n) = T(n/2) + 1",
                "T(n) = 2T(n/2) + n",
                "T(n) = 2T(n-1) + 1"
            ]
        }

    n0, b0 = parse_base_case(base_str)
    rec_type = parsed_rec["type"]

    if rec_type == "DEC_ADDITIVE":
        return _solve_dec_additive(parsed_rec["c"], n0, b0, rec_str, base_str)
    elif rec_type == "DEC_MULTIPLICATIVE":
        return _solve_dec_multiplicative(parsed_rec["a"], parsed_rec["c"], n0, b0, rec_str, base_str)
    elif rec_type == "DIV_LOG":
        return _solve_div_log(parsed_rec["b"], parsed_rec["c"], n0, b0, rec_str, base_str)
    elif rec_type == "DIV_LINEAR_N":
        return _solve_div_linear_n(parsed_rec["a"], parsed_rec["b"], parsed_rec["c"], n0, b0, rec_str, base_str)
    elif rec_type == "DIV_GENERAL_CONST":
        return _solve_div_general_const(parsed_rec["a"], parsed_rec["b"], parsed_rec["c"], n0, b0, rec_str, base_str)

    return {
        "supported": False,
        "error_message": "Sorry, this recurrence pattern is currently outside the supported solver.",
        "suggested_examples": [
            "T(n) = T(n-1) + 5",
            "T(n) = T(n/2) + 1",
            "T(n) = 2T(n/2) + n",
            "T(n) = 2T(n-1) + 1"
        ]
    }


def _solve_dec_additive(c: int, n0: int, b0: int, rec_str: str, base_str: str) -> dict:
    """
    T(n) = T(n-1) + c
    """
    # Formatting constants for equations
    c_str = f" + {c}" if c > 0 else ""
    c2_str = f" + {2*c}" if c > 0 else ""
    c3_str = f" + {3*c}" if c > 0 else ""
    ck_str = f" + {c}k" if c > 0 else ""

    # Exact closed form: T(n) = b0 + c*(n - n0) = c*n + (b0 - c*n0)
    slope = c
    intercept = b0 - c * n0
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
            "explanation": "Write down the original recurrence relation provided for analysis."
        },
        {
            "number": 2,
            "title": "First Substitution",
            "equation": f"T(n-1) = T(n-2){c_str}\n\\implies T(n) = [T(n-2){c_str}]{c_str} = T(n-2){c2_str}",
            "explanation": f"Express $T(n-1)$ using the recurrence relation and substitute it back into the equation for $T(n)$."
        },
        {
            "number": 3,
            "title": "Second Substitution",
            "equation": f"T(n-2) = T(n-3){c_str}\n\\implies T(n) = [T(n-3){c_str}]{c2_str} = T(n-3){c3_str}",
            "explanation": f"Substitute $T(n-2)$ into $T(n)$ to observe the growing constant term."
        },
        {
            "number": 4,
            "title": "General Pattern (k-th step)",
            "equation": f"T(n) = T(n-k){ck_str}",
            "explanation": f"After $k$ successive substitutions, express $T(n)$ in terms of $T(n-k)$ and parameter $k$."
        },
        {
            "number": 5,
            "title": "Reach Base Case",
            "equation": f"Set \\; n - k = {n0} \\implies k = n - {n0}",
            "explanation": f"Determine the number of steps $k$ required to hit the base condition $T({n0})$."
        },
        {
            "number": 6,
            "title": "Substitute k",
            "equation": f"T(n) = T({n0}){f' + {c}(n - {n0})' if c > 0 else ''}",
            "explanation": f"Replace $k$ with $n - {n0}$ in the general pattern equation."
        },
        {
            "number": 7,
            "title": "Apply Base Case Value",
            "equation": f"T({n0}) = {b0}\n\\implies T(n) = {b0}{f' + {c}(n - {n0})' if c > 0 else ''} = {exact_str}",
            "explanation": f"Substitute the base case value $T({n0}) = {b0}$ to get the exact closed-form solution."
        },
        {
            "number": 8,
            "title": "Asymptotic Time Complexity",
            "equation": "\\Theta(n)",
            "explanation": f"The highest order term in the closed form $T(n) = {exact_str}$ is $n$, giving a tight asymptotic bound of $\\Theta(n)$."
        }
    ]

    return {
        "supported": True,
        "recurrence": rec_str,
        "base_case": f"T({n0}) = {b0}",
        "type_name": "Linear Decrement Additive Recurrence",
        "steps": steps,
        "exact_solution": f"T(n) = {exact_str}",
        "complexity": "Θ(n)",
        "complexity_latex": "\\Theta(n)",
        "method": "Substitution Method"
    }


def _solve_dec_multiplicative(a: int, c: int, n0: int, b0: int, rec_str: str, base_str: str) -> dict:
    """
    T(n) = a*T(n-1) + c  (for a > 1)
    Example: 2T(n-1) + 1
    """
    # Pattern: T(n) = a^k * T(n-k) + c * (a^k - 1) / (a - 1)
    c_coeff = c // (a - 1) if (c % (a - 1) == 0) else None
    
    steps = [
        {
            "number": 1,
            "title": "Given Recurrence",
            "equation": f"T(n) = {a}T(n-1) + {c}",
            "explanation": "Identify the non-homogeneous linear decrement relation."
        },
        {
            "number": 2,
            "title": "First Substitution",
            "equation": f"T(n-1) = {a}T(n-2) + {c}\n\\implies T(n) = {a}[{a}T(n-2) + {c}] + {c} = {a**2}T(n-2) + {a*c + c}",
            "explanation": f"Substitute $T(n-1)$ into the original relation and expand coefficients."
        },
        {
            "number": 3,
            "title": "Second Substitution",
            "equation": f"T(n-2) = {a}T(n-3) + {c}\n\\implies T(n) = {a**2}[{a}T(n-3) + {c}] + {a*c + c} = {a**3}T(n-3) + {a**2*c + a*c + c}",
            "explanation": "Substitute $T(n-2)$ and simplify terms to observe geometric series growth."
        },
        {
            "number": 4,
            "title": "General Pattern (k-th step)",
            "equation": f"T(n) = {a}^k T(n-k) + {c} \\sum_{{i=0}}^{{k-1}} {a}^i = {a}^k T(n-k) + {c} \\cdot \\frac{{{a}^k - 1}}{{{a} - 1}}",
            "explanation": f"Using geometric series summation $\\sum_{{i=0}}^{{k-1}} {a}^i = \\frac{{{a}^k - 1}}{{{a}-1}}$, establish the general $k$-th term."
        },
        {
            "number": 5,
            "title": "Reach Base Case",
            "equation": f"Set \\; n - k = {n0} \\implies k = n - {n0}",
            "explanation": f"Calculate the number of steps required to reach $T({n0})$."
        },
        {
            "number": 6,
            "title": "Substitute k",
            "equation": f"T(n) = {a}^{{n-{n0}}} T({n0}) + {c} \\cdot \\frac{{{a}^{{n-{n0}}} - 1}}{{{a} - 1}}",
            "explanation": f"Substitute $k = n - {n0}$ into the general pattern equation."
        },
        {
            "number": 7,
            "title": "Apply Base Case Value",
            "equation": f"T({n0}) = {b0} \\implies T(n) = {b0} \\cdot {a}^{{n-{n0}}} + {c} \\cdot \\frac{{{a}^{{n-{n0}}} - 1}}{{{a} - 1}}",
            "explanation": "Simplify terms to produce the closed-form representation."
        },
        {
            "number": 8,
            "title": "Asymptotic Time Complexity",
            "equation": f"\\Theta({a}^n)",
            "explanation": f"The dominant term grows exponentially as ${a}^n$, yielding an asymptotic time complexity of $\\Theta({a}^n)$."
        }
    ]

    # Simplified representation for a=2, c=1, n0=1, b0=1 => 2^n - 1
    if a == 2 and c == 1 and n0 == 1 and b0 == 1:
        exact_solution_str = "T(n) = 2^n - 1"
    else:
        exact_solution_str = f"T(n) = {b0} \\cdot {a}^{{n-{n0}}} + \\frac{{{c}({a}^{{n-{n0}}} - 1)}}{{{a-1}}}"

    return {
        "supported": True,
        "recurrence": rec_str,
        "base_case": f"T({n0}) = {b0}",
        "type_name": "Exponential Decrement Recurrence",
        "steps": steps,
        "exact_solution": exact_solution_str,
        "complexity": f"Θ({a}^n)",
        "complexity_latex": f"\\Theta({a}^n)",
        "method": "Substitution Method"
    }


def _solve_div_log(b: int, c: int, n0: int, b0: int, rec_str: str, base_str: str) -> dict:
    """
    T(n) = T(n/b) + c
    Example: T(n) = T(n/2) + 1
    """
    log_b_str = f"\\log_{{{b}}} n" if b != 2 else "\\log_2 n"
    
    steps = [
        {
            "number": 1,
            "title": "Given Recurrence",
            "equation": f"T(n) = T(n/{b}) + {c}",
            "explanation": "State the logarithmic divide-and-conquer recurrence relation."
        },
        {
            "number": 2,
            "title": "First Substitution",
            "equation": f"T(n/{b}) = T(n/{b**2}) + {c}\n\\implies T(n) = [T(n/{b**2}) + {c}] + {c} = T(n/{b**2}) + {2*c}",
            "explanation": f"Substitute $T(n/{b})$ into $T(n)$."
        },
        {
            "number": 3,
            "title": "Second Substitution",
            "equation": f"T(n/{b**2}) = T(n/{b**3}) + {c}\n\\implies T(n) = [T(n/{b**3}) + {c}] + {2*c} = T(n/{b**3}) + {3*c}",
            "explanation": "Perform the next substitution to identify how the constant accumulates."
        },
        {
            "number": 4,
            "title": "General Pattern (k-th step)",
            "equation": f"T(n) = T(n/{b}^k) + {c}k",
            "explanation": f"Express $T(n)$ after $k$ recursive divisions as $T(n/{b}^k) + {c}k$."
        },
        {
            "number": 5,
            "title": "Reach Base Case",
            "equation": f"Set \\; \\frac{{n}}{{{b}^k}} = {n0} \\implies {b}^k = \\frac{{n}}{{{n0}}} \\implies k = \\log_{{{b}}} \\left(\\frac{{n}}{{{n0}}}\\right)",
            "explanation": f"Solve for $k$ such that the argument reduces to the base condition $n/{b}^k = {n0}$."
        },
        {
            "number": 6,
            "title": "Substitute k",
            "equation": f"T(n) = T({n0}) + {c} \\log_{{{b}}} n" if n0 == 1 else f"T(n) = T({n0}) + {c} \\log_{{{b}}} (n/{n0})",
            "explanation": "Replace $k$ with the logarithmic expression."
        },
        {
            "number": 7,
            "title": "Apply Base Case Value",
            "equation": f"T({n0}) = {b0} \\implies T(n) = {b0} + {c} \\log_{{{b}}} n" if n0 == 1 else f"T(n) = {b0} + {c} \\log_{{{b}}} (n/{n0})",
            "explanation": f"Substitute $T({n0}) = {b0}$ to derive the final exact function."
        },
        {
            "number": 8,
            "title": "Asymptotic Time Complexity",
            "equation": "\\Theta(\\log n)",
            "explanation": f"Since logarithmic bases differ only by constant factors ($\\,\\log_b n = \\frac{{\\log n}}{{\\log b}}\\,$), the tight bound is $\\Theta(\\log n)$."
        }
    ]

    exact_str = f"T(n) = {b0} + {c} \\log_{{{b}}} n" if n0 == 1 else f"T(n) = {b0} + {c} \\log_{{{b}}} (n/{n0})"

    return {
        "supported": True,
        "recurrence": rec_str,
        "base_case": f"T({n0}) = {b0}",
        "type_name": "Logarithmic Divide-and-Conquer Recurrence",
        "steps": steps,
        "exact_solution": exact_str,
        "complexity": "Θ(log n)",
        "complexity_latex": "\\Theta(\\log n)",
        "method": "Substitution Method"
    }


def _solve_div_linear_n(a: int, b: int, c: int, n0: int, b0: int, rec_str: str, base_str: str) -> dict:
    """
    T(n) = a*T(n/b) + c*n
    Example: 2T(n/2) + n  (MergeSort)
    """
    c_n_str = f"{c}n" if c != 1 else "n"
    log_b_str = f"\\log_{{{b}}} n" if b != 2 else "\\log_2 n"

    # Case: a == b (e.g. 2T(n/2) + n)
    if a == b:
        steps = [
            {
                "number": 1,
                "title": "Given Recurrence",
                "equation": f"T(n) = {a}T(n/{b}) + {c_n_str}",
                "explanation": "State the divide-and-conquer recurrence relation (typical for MergeSort-like algorithms)."
            },
            {
                "number": 2,
                "title": "First Substitution",
                "equation": f"T(n/{b}) = {a}T(n/{b**2}) + {c}(n/{b})\n\\implies T(n) = {a}\\left[{a}T(n/{b**2}) + {c}(n/{b})\\right] + {c}n = {a**2}T(n/{b**2}) + {a*c/b:.0f}n + {c}n = {a**2}T(n/{b**2}) + {2*c}n",
                "explanation": f"Substitute $T(n/{b})$ into $T(n)$ and simplify the linear term."
            },
            {
                "number": 3,
                "title": "Second Substitution",
                "equation": f"T(n/{b**2}) = {a}T(n/{b**3}) + {c}(n/{b**2})\n\\implies T(n) = {a**2}\\left[{a}T(n/{b**3}) + {c}(n/{b**2})\\right] + {2*c}n = {a**3}T(n/{b**3}) + {3*c}n",
                "explanation": f"Substitute $T(n/{b**2})$ to observe that each step adds exactly ${c}n$ to the non-recursive work."
            },
            {
                "number": 4,
                "title": "General Pattern (k-th step)",
                "equation": f"T(n) = {a}^k T(n/{b}^k) + k \\cdot {c_n_str}",
                "explanation": f"After $k$ substitutions, the expression becomes ${a}^k T(n/{b}^k) + k \\cdot {c_n_str}$."
            },
            {
                "number": 5,
                "title": "Reach Base Case",
                "equation": f"Set \\; \\frac{{n}}{{{b}^k}} = {n0} \\implies {b}^k = n \\implies k = \\log_{{{b}}} n",
                "explanation": f"Solve for $k$ to reach the base condition $n/{b}^k = 1$."
            },
            {
                "number": 6,
                "title": "Substitute k",
                "equation": f"T(n) = {a}^{{\\log_{{{b}}} n}} T(1) + (\\log_{{{b}}} n) \\cdot {c_n_str} = n T(1) + {c} n \\log_{{{b}}} n",
                "explanation": f"Using the logarithm power identity ${a}^{{\\log_{{{b}}} n}} = n^{{\\log_{{{b}}} {a}}} = n^1 = n$, substitute $k$ back into the formula."
            },
            {
                "number": 7,
                "title": "Apply Base Case Value",
                "equation": f"T(1) = {b0} \\implies T(n) = {b0}n + {c} n \\log_{{{b}}} n",
                "explanation": f"Substitute $T(1) = {b0}$ to obtain the exact analytical equation."
            },
            {
                "number": 8,
                "title": "Asymptotic Time Complexity",
                "equation": "\\Theta(n \\log n)",
                "explanation": "The term $n \\log n$ grows faster than linear $n$, making the tight upper and lower bound $\\Theta(n \\log n)$."
            }
        ]

        exact_str = f"T(n) = {c} n \\log_{{{b}}} n + {b0}n" if b0 != 0 else f"T(n) = {c} n \\log_{{{b}}} n"

        return {
            "supported": True,
            "recurrence": rec_str,
            "base_case": f"T({n0}) = {b0}",
            "type_name": "Linear-Divide Recurrence (MergeSort Type)",
            "steps": steps,
            "exact_solution": exact_str,
            "complexity": "Θ(n log n)",
            "complexity_latex": "\\Theta(n \\log n)",
            "method": "Substitution Method"
        }
    else:
        # Case a != b (e.g., 4T(n/2) + n)
        log_b_a = math.log(a, b)
        log_str = f"n^{{\\log_{{{b}}} {a}}}" if not log_b_a.is_integer() else f"n^{{{int(log_b_a)}}}"
        
        steps = [
            {
                "number": 1,
                "title": "Given Recurrence",
                "equation": f"T(n) = {a}T(n/{b}) + {c_n_str}",
                "explanation": "State the non-equal branching divide-and-conquer recurrence."
            },
            {
                "number": 2,
                "title": "First Substitution",
                "equation": f"T(n/{b}) = {a}T(n/{b**2}) + {c}(n/{b})\n\\implies T(n) = {a}\\left[{a}T(n/{b**2}) + {c}(n/{b})\\right] + {c}n = {a**2}T(n/{b**2}) + c n \\left(1 + \\frac{{{a}}}{{{b}}}\\right)",
                "explanation": "Substitute $T(n/b)$ and collect powers of $(a/b)$."
            },
            {
                "number": 3,
                "title": "General Pattern (k-th step)",
                "equation": f"T(n) = {a}^k T(n/{b}^k) + c n \\sum_{{i=0}}^{{k-1}} \\left(\\frac{{{a}}}{{{b}}}\\right)^i",
                "explanation": "After $k$ steps, the non-recursive work forms a geometric series with ratio $(a/b)$."
            },
            {
                "number": 4,
                "title": "Reach Base Case",
                "equation": f"Set \\; \\frac{{n}}{{{b}^k}} = 1 \\implies k = \\log_{{{b}}} n",
                "explanation": "Solve for $k$ when argument reaches 1."
            },
            {
                "number": 5,
                "title": "Apply Base Case & Master Theorem Boundary",
                "equation": f"T(n) = {a}^{{\\log_{{{b}}} n}} T(1) + c n \\sum_{{i=0}}^{{\\log_{{{b}}} n - 1}} \\left(\\frac{{{a}}}{{{b}}}\\right)^i = \\Theta({log_str})",
                "explanation": f"Since $a > b$ ($a={a}, b={b}$), the leaf nodes dominate the recursive work."
            },
            {
                "number": 6,
                "title": "Asymptotic Time Complexity",
                "equation": f"\\Theta({log_str})",
                "explanation": f"The dominant work is performed at the leaf level, yielding $\\Theta({log_str})$."
            }
        ]

        return {
            "supported": True,
            "recurrence": rec_str,
            "base_case": f"T({n0}) = {b0}",
            "type_name": "Divide-and-Conquer Recurrence",
            "steps": steps,
            "exact_solution": f"T(n) = \\Theta({log_str})",
            "complexity": f"Θ({log_str})",
            "complexity_latex": f"\\Theta({log_str})",
            "method": "Substitution Method"
        }


def _solve_div_general_const(a: int, b: int, c: int, n0: int, b0: int, rec_str: str, base_str: str) -> dict:
    """
    T(n) = a*T(n/b) + c
    Example: 2T(n/2) + 1
    """
    log_b_a = math.log(a, b)
    log_str = f"n^{{\\log_{{{b}}} {a}}}" if not log_b_a.is_integer() else (f"n" if int(log_b_a) == 1 else f"n^{{{int(log_b_a)}}}")

    steps = [
        {
            "number": 1,
            "title": "Given Recurrence",
            "equation": f"T(n) = {a}T(n/{b}) + {c}",
            "explanation": "State the branching divide-and-conquer relation with constant extra work."
        },
        {
            "number": 2,
            "title": "First Substitution",
            "equation": f"T(n/{b}) = {a}T(n/{b**2}) + {c}\n\\implies T(n) = {a}[{a}T(n/{b**2}) + {c}] + {c} = {a**2}T(n/{b**2}) + {a*c + c}",
            "explanation": f"Substitute $T(n/{b})$ into $T(n)$."
        },
        {
            "number": 3,
            "title": "Second Substitution",
            "equation": f"T(n/{b**2}) = {a}T(n/{b**3}) + {c}\n\\implies T(n) = {a**2}[{a}T(n/{b**3}) + {c}] + {a*c + c} = {a**3}T(n/{b**3}) + {a**2*c + a*c + c}",
            "explanation": "Observe the geometric expansion of constant work across branches."
        },
        {
            "number": 4,
            "title": "General Pattern (k-th step)",
            "equation": f"T(n) = {a}^k T(n/{b}^k) + {c} \\sum_{{i=0}}^{{k-1}} {a}^i = {a}^k T(n/{b}^k) + {c} \\cdot \\frac{{{a}^k - 1}}{{{a} - 1}}",
            "explanation": f"Summing geometric series $\\sum_{{i=0}}^{{k-1}} {a}^i = \\frac{{{a}^k - 1}}{{{a}-1}}$ for $k$ steps."
        },
        {
            "number": 5,
            "title": "Reach Base Case",
            "equation": f"Set \\; \\frac{{n}}{{{b}^k}} = 1 \\implies k = \\log_{{{b}}} n",
            "explanation": "Calculate the depth of the recursion tree $k = \\log_b n$."
        },
        {
            "number": 6,
            "title": "Substitute k & Apply Base Case",
            "equation": f"T(n) = {a}^{{\\log_{{{b}}} n}} T(1) + {c} \\cdot \\frac{{{a}^{{\\log_{{{b}}} n}} - 1}}{{{a} - 1}} = {log_str} \\cdot {b0} + {c} \\cdot \\frac{{{log_str} - 1}}{{{a} - 1}}",
            "explanation": f"Using identity ${a}^{{\\log_{{{b}}} n}} = {log_str}$, solve for closed form."
        },
        {
            "number": 7,
            "title": "Asymptotic Time Complexity",
            "equation": f"\\Theta({log_str})",
            "explanation": f"The number of leaves dominates the total execution time, resulting in $\\Theta({log_str})$."
        }
    ]

    return {
        "supported": True,
        "recurrence": rec_str,
        "base_case": f"T({n0}) = {b0}",
        "type_name": "General Divide-and-Conquer Recurrence",
        "steps": steps,
        "exact_solution": f"T(n) = \\Theta({log_str})",
        "complexity": f"Θ({log_str})",
        "complexity_latex": f"\\Theta({log_str})",
        "method": "Substitution Method"
    }
