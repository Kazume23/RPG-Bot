import asyncio
import unittest

from services.character_aliver import character_randomizer


class CharacterTests(unittest.TestCase):
    def test_equipment_does_not_leak_python_lists(self):
        result = asyncio.run(character_randomizer("człowiek", "m", "berserker z norski"))
        self.assertNotIn("- ['", result)
        self.assertNotIn('- ["', result)


if __name__ == "__main__":
    unittest.main()
