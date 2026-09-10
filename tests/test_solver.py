import unittest
import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from solver.substitution import solve_recurrence, parse_base_case, parse_recurrence


class TestSubstitutionSolver(unittest.TestCase):

    def test_decrement_additive(self):
        result = solve_recurrence("T(n) = T(n-1) + 5", "T(1) = 1")
        self.assertTrue(result["supported"])
        self.assertEqual(result["complexity"], "Θ(n)")
        self.assertIn("5n - 4", result["exact_solution"])
        self.assertGreaterEqual(len(result["steps"]), 6)

    def test_divide_and_conquer_logarithmic(self):
        result = solve_recurrence("T(n) = T(n/2) + 1", "T(1) = 1")
        self.assertTrue(result["supported"])
        self.assertEqual(result["complexity"], "Θ(log n)")
        self.assertIn("log", result["exact_solution"])
        self.assertGreaterEqual(len(result["steps"]), 6)

    def test_mergesort_recurrence(self):
        result = solve_recurrence("T(n) = 2T(n/2) + n", "T(1) = 1")
        self.assertTrue(result["supported"])
        self.assertEqual(result["complexity"], "Θ(n log n)")
        self.assertGreaterEqual(len(result["steps"]), 6)

    def test_exponential_decrement(self):
        result = solve_recurrence("T(n) = 2T(n-1) + 1", "T(1) = 1")
        self.assertTrue(result["supported"])
        self.assertEqual(result["complexity"], "Θ(2^n)")
        self.assertIn("2^n - 1", result["exact_solution"])

    def test_invalid_and_unsupported(self):
        res1 = solve_recurrence("", "T(1) = 1")
        self.assertFalse(res1["supported"])
        self.assertIn("Please enter a recurrence relation", res1["error_message"])

        res2 = solve_recurrence("T(n) = sin(n) + T(n-1)", "T(1) = 1")
        self.assertFalse(res2["supported"])

    def test_parse_base_case(self):
        self.assertEqual(parse_base_case("T(1) = 1"), (1, 1))
        self.assertEqual(parse_base_case("T(0) = 5"), (0, 5))
        self.assertEqual(parse_base_case(""), (1, 1))


if __name__ == "__main__":
    unittest.main()
