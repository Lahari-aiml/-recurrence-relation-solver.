import unittest
import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from solver.ai_chatbot import get_ai_chat_response, extract_recurrence_equation


class TestAIChatbot(unittest.TestCase):

    def setUp(self):
        self.app_client = app.test_client()
        self.app_client.testing = True

    def test_extract_recurrence_equation(self):
        eq1 = extract_recurrence_equation("Solve T(n) = 2T(n/2) + n please")
        self.assertIsNotNone(eq1)
        self.assertIn("T(n) = 2T(n/2) + n", eq1)

        eq2 = extract_recurrence_equation("What is the substitution method?")
        self.assertIsNone(eq2)

    def test_ai_chat_response_recurrence(self):
        res = get_ai_chat_response("Solve T(n) = T(n-1) + 1")
        self.assertTrue(res.get("equation_solved"))
        self.assertEqual(res.get("complexity"), "Θ(n)")

    def test_ai_chat_context_aware_step_explanation(self):
        context = {
            "recurrence": "T(n) = 2T(n/2) + n",
            "base_case": "T(1) = 1",
            "exact_solution": "T(n) = n log_2 n + n",
            "complexity": "Θ(n log n)",
            "complexity_latex": "\\Theta(n \\log n)",
            "num_levels": "k = \\log_2 n",
            "steps": [
                {"number": 1, "title": "Write the Original Recurrence", "equation": "T(n) = 2T(n/2) + n", "explanation": "Original equation"},
                {"number": 2, "title": "Substitute T(n/2)", "equation": "T(n) = 4T(n/4) + 2n", "explanation": "First substitution"},
                {"number": 3, "title": "Expand Again (Substitute T(n/4))", "equation": "T(n) = 8T(n/8) + 3n", "explanation": "Second expansion"}
            ]
        }
        res = get_ai_chat_response("Explain step 3", context=context)
        self.assertTrue(res.get("context_used"))
        self.assertIn("Step 3", res.get("response"))
        self.assertIn("8T(n/8) + 3n", res.get("response"))

    def test_ai_chat_context_aware_coefficient(self):
        context = {
            "recurrence": "T(n) = 2T(n/2) + n",
            "base_case": "T(1) = 1",
            "complexity": "Θ(n log n)"
        }
        res = get_ai_chat_response("Why did 2 become 4?", context=context)
        self.assertTrue(res.get("context_used"))
        self.assertIn("4T(n/4)", res.get("response"))

    def test_ai_chat_context_aware_why_substitute(self):
        context = {
            "recurrence": "T(n) = 2T(n/2) + n",
            "base_case": "T(1) = 1",
            "complexity": "Θ(n log n)"
        }
        res = get_ai_chat_response("Why did you substitute n/2?", context=context)
        self.assertTrue(res.get("context_used"))
        self.assertIn("Substitution Method", res.get("response"))

    def test_ai_chat_context_aware_k(self):
        context = {
            "recurrence": "T(n) = 2T(n/2) + n",
            "base_case": "T(1) = 1",
            "num_levels": "k = \\log_2 n",
            "complexity": "Θ(n log n)"
        }
        res = get_ai_chat_response("How did we get k?", context=context)
        self.assertTrue(res.get("context_used"))
        self.assertIn("\\log_b n", res.get("response"))

    def test_ai_chat_context_aware_complexity(self):
        context = {
            "recurrence": "T(n) = 2T(n/2) + n",
            "base_case": "T(1) = 1",
            "exact_solution": "T(n) = n log_2 n + n",
            "complexity": "Θ(n log n)",
            "complexity_latex": "\\Theta(n \\log n)",
            "complexity_explanation": "There are log_2 n levels of substitution, each contributing n work."
        }
        res = get_ai_chat_response("Why is the answer Θ(n log n)?", context=context)
        self.assertTrue(res.get("context_used"))
        self.assertIn("\\Theta(n \\log n)", res.get("response"))

    def test_api_chat_endpoint(self):
        response = self.app_client.post(
            "/api/chat",
            json={"message": "Hello"}
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn("response", json_data)
        self.assertIn("Recurrence", json_data["response"])


if __name__ == "__main__":
    unittest.main()
