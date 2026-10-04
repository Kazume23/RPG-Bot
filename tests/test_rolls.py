import unittest

from services.rolls import parse_roll, roll_logic


class RollTests(unittest.TestCase):
    def test_supported_syntax(self):
        self.assertEqual(parse_roll("d100"), (1, 100))
        self.assertEqual(parse_roll("2D10"), (2, 10))

    def test_invalid_dice_counts_are_rejected(self):
        for expression in ("0d6", "-1d6", "51d6"):
            with self.subTest(expression=expression):
                self.assertIn(
                    roll_logic(expression),
                    {"No chyba cię coś pojebało", "Ty chuju. Pisz jak człowiek np: 5d6"},
                )

    def test_invalid_sides_are_rejected(self):
        for expression in ("1d0", "1d1", "1d-6"):
            with self.subTest(expression=expression):
                self.assertEqual("Ty chuju. Pisz jak człowiek np: 5d6", roll_logic(expression))


if __name__ == "__main__":
    unittest.main()
