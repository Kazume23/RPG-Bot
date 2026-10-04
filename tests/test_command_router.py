import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import bot as bot_module
import command_router
from config.settings import COMMAND_PREFIX


def run(coroutine):
    return asyncio.run(coroutine)


class TypingContext:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False


class CommandRouterTests(unittest.TestCase):
    def test_prefixed_message_is_handled(self):
        message = SimpleNamespace(content=f"  {COMMAND_PREFIX}roll 1d6")
        self.assertTrue(command_router.should_handle(message))

    def test_regular_message_is_ignored(self):
        message = SimpleNamespace(content="hej, co słychać?")
        self.assertFalse(command_router.should_handle(message))

    def test_roll_reaches_command_without_ai_layer(self):
        ctx = SimpleNamespace(content=f"{COMMAND_PREFIX}roll 1d6")
        with patch("services.rolls.random.randint", return_value=4):
            result = run(command_router.process_commands(ctx))
        self.assertIn("Wyniki rzutów", result)
        self.assertIn("4", result)

    def test_unknown_command_keeps_original_tone(self):
        ctx = SimpleNamespace(content=f"{COMMAND_PREFIX}co-to-jest")
        result = run(command_router.process_commands(ctx))
        self.assertEqual("Naucz się w końcu tych komend KURWAAA", result)

    def test_discord_message_reaches_send(self):
        channel = SimpleNamespace(
            typing=lambda: TypingContext(),
            send=AsyncMock(),
        )
        message = SimpleNamespace(
            author=SimpleNamespace(bot=False),
            channel=channel,
            guild=None,
            content=f"{COMMAND_PREFIX}hello",
        )

        run(bot_module.on_message(message))

        channel.send.assert_awaited_once_with("Spierdalaj")


if __name__ == "__main__":
    unittest.main()
