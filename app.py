from flask import Flask, render_template, request, redirect, url_for
from solver.substitution import solve_recurrence

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    """Renders home page with solver input form and preset examples."""
    return render_template("index.html")


@app.route("/about", methods=["GET"])
def about():
    """Renders educational about page explaining substitution method concepts."""
    return render_template("about.html")


@app.route("/solve", methods=["GET", "POST"])
def solve():
    """
    Handles recurrence relation solving requests.
    Extracts form parameters, invokes solver engine, and renders solution page.
    """
    if request.method == "GET":
        # If user visits /solve directly via URL GET, redirect to home page
        return redirect(url_for("index"))

    recurrence_input = request.form.get("recurrence", "").strip()
    base_case_input = request.form.get("base_case", "").strip()

    # Default base case if left empty
    if not base_case_input:
        base_case_input = "T(1) = 1"

    try:
        solution_data = solve_recurrence(recurrence_input, base_case_input)
    except Exception as e:
        # Prevent stack trace leakage to frontend
        solution_data = {
            "supported": False,
            "error_message": "An unexpected error occurred while parsing. Please check your syntax.",
            "suggested_examples": [
                "T(n) = T(n-1) + 5",
                "T(n) = T(n/2) + 1",
                "T(n) = 2T(n/2) + n",
                "T(n) = 2T(n-1) + 1"
            ]
        }

    return render_template(
        "solution.html",
        solution=solution_data,
        recurrence_input=recurrence_input,
        base_case_input=base_case_input
    )


@app.errorhandler(404)
def page_not_found(e):
    return render_template("index.html", error="Page not found. Redirected to home."), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("index.html", error="Internal server error. Please try again."), 500


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
