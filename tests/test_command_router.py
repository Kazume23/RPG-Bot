import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import command_router


def run(coroutine):
    return asyncio.run(coroutine)


class CommandRouterTests(unittest.TestCase):
    def test_prefixed_message_is_handled(self):
        message = SimpleNamespace(content="  <roll 1d6")
        self.assertTrue(command_router.should_handle(message))

    def test_regular_message_is_ignored(self):
        message = SimpleNamespace(content="hej, co słychać?")
        self.assertFalse(command_router.should_handle(message))

    def test_roll_reaches_command_without_ai_layer(self):
        ctx = SimpleNamespace(content="<roll 1d6")
        with patch("services.rolls.random.randint", return_value=4):
            result = run(command_router.process_commands(ctx))
        self.assertIn("Wyniki rzutów", result)
        self.assertIn("4", result)


if __name__ == "__main__":
    unittest.main()
