import unittest

from services.rolls import parse_roll, roll_logic


class RollTests(unittest.TestCase):
    def test_supported_syntax(self):
        self.assertEqual(parse_roll("d100"), (1, 100))
        self.assertEqual(parse_roll("2D10"), (2, 10))

    def test_invalid_dice_counts_are_rejected(self):
        for expression in ("0d6", "-1d6", "51d6"):
            with self.subTest(expression=expression):
                self.assertTrue(roll_logic(expression).startswith("Niepoprawny rzut"))

    def test_invalid_sides_are_rejected(self):
        for expression in ("1d0", "1d1", "1d-6"):
            with self.subTest(expression=expression):
                self.assertTrue(roll_logic(expression).startswith("Niepoprawny rzut"))


if __name__ == "__main__":
    unittest.main()
