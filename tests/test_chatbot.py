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

        eq2 = extract_recurrence_equation("What is Master Theorem?")
        self.assertIsNone(eq2)

    def test_ai_chat_response_recurrence(self):
        res = get_ai_chat_response("Solve T(n) = T(n-1) + 5")
        self.assertTrue(res.get("equation_solved"))
        self.assertEqual(res.get("complexity"), "Θ(n)")

    def test_ai_chat_context_aware_k(self):
        context = {
            "recurrence": "T(n) = T(n-1) + 5",
            "base_case": "T(1) = 1",
            "exact_solution": "T(n) = 5n - 4",
            "complexity": "Θ(n)",
            "type_name": "Linear Decrement (Additive Constant)"
        }
        res = get_ai_chat_response("Why is k = n-1?", context=context)
        self.assertTrue(res.get("context_used"))
        self.assertIn("n - k = 1", res.get("response"))

    def test_ai_chat_context_aware_complexity(self):
        context = {
            "recurrence": "T(n) = 2T(n/2) + n",
            "base_case": "T(1) = 1",
            "exact_solution": "T(n) = n log_2 n + n",
            "complexity": "Θ(n log n)",
            "type_name": "Balanced Divide-and-Conquer"
        }
        res = get_ai_chat_response("Why is the answer Θ(n log n)?", context=context)
        self.assertTrue(res.get("context_used"))
        self.assertIn("Θ(n log n)", res.get("response"))

    def test_api_chat_endpoint(self):
        response = self.app_client.post(
            "/api/chat",
            json={"message": "Hello"}
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn("response", json_data)
        self.assertIn("AI Tutor", json_data["response"])


if __name__ == "__main__":
    unittest.main()
