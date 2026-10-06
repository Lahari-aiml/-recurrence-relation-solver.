import unittest
import sys
import os

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from solver.substitution import solve_recurrence, parse_base_case, parse_recurrence


class TestSubstitutionSolver(unittest.TestCase):

    def test_decrement_additive_1(self):
        result = solve_recurrence("T(n) = T(n-1) + 1", "T(1) = 1")
        self.assertTrue(result["supported"])
        self.assertEqual(result["complexity"], "Θ(n)")
        self.assertIn("O(n)", result["big_o"])
        self.assertIn("\\Theta(n)", result["big_theta"])
        self.assertIn("\\Omega(n)", result["big_omega"])
        self.assertEqual(len(result["steps"]), 7)

    def test_decrement_additive_5(self):
        result = solve_recurrence("T(n) = T(n-1) + 5", "T(1) = 1")
        self.assertTrue(result["supported"])
        self.assertEqual(result["complexity"], "Θ(n)")
        self.assertIn("5n - 4", result["exact_solution"])
        self.assertEqual(len(result["steps"]), 7)

    def test_linear_growth_decrement(self):
        result = solve_recurrence("T(n) = T(n-1) + n", "T(1) = 1")
        self.assertTrue(result["supported"])
        self.assertEqual(result["complexity"], "Θ(n²)")
        self.assertIn("O(n^2)", result["big_o"])
        self.assertEqual(len(result["steps"]), 7)

    def test_quadratic_growth_decrement(self):
        result = solve_recurrence("T(n) = T(n-1) + n^2", "T(1) = 1")
        self.assertTrue(result["supported"])
        self.assertEqual(result["complexity"], "Θ(n³)")
        self.assertIn("O(n^3)", result["big_o"])
        self.assertEqual(len(result["steps"]), 7)

    def test_logarithmic_decrement(self):
        result = solve_recurrence("T(n) = T(n-1) + log n", "T(1) = 1")
        self.assertTrue(result["supported"])
        self.assertEqual(result["complexity"], "Θ(n log n)")
        self.assertEqual(len(result["steps"]), 7)

    def test_mergesort_recurrence(self):
        result = solve_recurrence("T(n) = 2T(n/2) + n", "T(1) = 1")
        self.assertTrue(result["supported"])
        self.assertEqual(result["complexity"], "Θ(n log n)")
        self.assertIn("\\log_2 n", result["num_levels"])
        self.assertIn("O(n \\log n)", result["big_o"])
        self.assertIn("\\Theta(n \\log n)", result["big_theta"])
        self.assertEqual(len(result["steps"]), 7)

    def test_binary_search_recurrence(self):
        result = solve_recurrence("T(n) = T(n/2) + 1", "T(1) = 1")
        self.assertTrue(result["supported"])
        self.assertEqual(result["complexity"], "Θ(log n)")
        self.assertEqual(len(result["steps"]), 7)

    def test_branching_divide_const(self):
        result = solve_recurrence("T(n) = 2T(n/2) + 1", "T(1) = 1")
        self.assertTrue(result["supported"])
        self.assertEqual(result["complexity"], "Θ(n)")
        self.assertEqual(len(result["steps"]), 7)

    def test_branching_divide_3(self):
        result = solve_recurrence("T(n) = 3T(n/2) + n", "T(1) = 1")
        self.assertTrue(result["supported"])
        self.assertIn(r"\log_{2} 3", result["complexity_latex"])
        self.assertEqual(len(result["steps"]), 7)

    def test_linearithmic_divide_mergesort(self):
        result = solve_recurrence("T(n) = 2T(n/2) + n log n", "T(1) = 1")
        self.assertTrue(result["supported"])
        self.assertEqual(result["complexity"], "Θ(n log^2 n)")
        self.assertEqual(len(result["steps"]), 7)

    def test_divide_by_3_root_dominant(self):
        result = solve_recurrence("T(n) = T(n/3) + n", "T(1) = 1")
        self.assertTrue(result["supported"])
        self.assertEqual(result["complexity"], "Θ(n)")
        self.assertEqual(len(result["steps"]), 7)

    def test_divide_by_3_two_subproblems(self):
        result = solve_recurrence("T(n) = 2T(n/3) + n", "T(1) = 1")
        self.assertTrue(result["supported"])
        self.assertEqual(result["complexity"], "Θ(n)")
        self.assertEqual(len(result["steps"]), 7)

    def test_divide_by_3_quadratic(self):
        result = solve_recurrence("T(n) = 4T(n/3) + n^2", "T(1) = 1")
        self.assertTrue(result["supported"])
        self.assertEqual(result["complexity"], "Θ(n²)")
        self.assertEqual(len(result["steps"]), 7)

    def test_exponential_decrement(self):
        result = solve_recurrence("T(n) = 2T(n-1) + 1", "T(1) = 1")
        self.assertTrue(result["supported"])
        self.assertEqual(result["complexity"], "Θ(2^n)")
        self.assertIn("2^n - 1", result["exact_solution"])
        self.assertEqual(len(result["steps"]), 7)

    def test_step_k_decrement(self):
        result = solve_recurrence("T(n) = T(n-2) + 3", "T(1) = 1")
        self.assertTrue(result["supported"])
        self.assertEqual(result["complexity"], "Θ(n)")
        self.assertEqual(len(result["steps"]), 7)

    def test_unspecified_base_case_assumption(self):
        result = solve_recurrence("T(n) = 2T(n/2) + n", "")
        self.assertTrue(result["supported"])
        self.assertTrue(result["base_case_assumed"])
        self.assertIn("assuming", result["base_case_note"].lower())

    def test_invalid_and_unsupported(self):
        res1 = solve_recurrence("", "T(1) = 1")
        self.assertFalse(res1["supported"])
        self.assertIn("Please enter a valid recurrence relation", res1["error_message"])

        res2 = solve_recurrence("T(n) = sin(n) + T(n-1)", "T(1) = 1")
        self.assertFalse(res2["supported"])
        self.assertIn("outside the supported substitution patterns", res2["error_message"])

    def test_parse_base_case(self):
        self.assertEqual(parse_base_case("T(1) = 1"), (1, 1, True))
        self.assertEqual(parse_base_case("T(0) = 5"), (0, 5, True))
        self.assertEqual(parse_base_case(""), (1, 1, False))


if __name__ == "__main__":
    unittest.main()
