import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from commands.classes import classes_command
from commands.npc import npc_command
from commands.roll import roll_command
from commands.utility import has_admin_permissions
from static.wyzwiska import przeklenstwa_ogolne


def run(coroutine):
    return asyncio.run(coroutine)


class CommandTests(unittest.TestCase):
    def test_multiword_class_name(self):
        result = run(classes_command("łowca czarownic"))
        self.assertIn("Łowca czarownic", result)

    def test_unknown_class_returns_message(self):
        result = run(classes_command("nieistniejąca klasa"))
        self.assertEqual("Naucz się dobrze wpisywać klasy przyczłapie", result)

    def test_original_roll_insult_is_preserved(self):
        self.assertEqual("Ty chuju. Pisz jak człowiek np: 5d6", run(roll_command("")))

    def test_all_original_insults_are_present(self):
        self.assertEqual(70, len(przeklenstwa_ogolne))
        self.assertEqual(70, len(set(przeklenstwa_ogolne)))

    def test_npc_rejects_invalid_gender(self):
        ctx = SimpleNamespace(
            guild=object(),
            author=SimpleNamespace(
                id=123,
                roles=[],
                guild_permissions=SimpleNamespace(administrator=True),
            ),
        )
        fake_settings = SimpleNamespace(owner_id=123, gm_role_id=None)
        with patch("commands.utility.settings", fake_settings):
            result = run(npc_command(ctx, "człowiek x akolita"))
        self.assertIn("m` albo `f", result)

    def test_server_admin_without_gm_role_is_not_automatically_authorized(self):
        ctx = SimpleNamespace(
            guild=object(),
            author=SimpleNamespace(
                id=999,
                roles=[],
                guild_permissions=SimpleNamespace(administrator=True),
            ),
        )
        fake_settings = SimpleNamespace(owner_id=123, gm_role_id=456)
        with patch("commands.utility.settings", fake_settings):
            self.assertFalse(has_admin_permissions(ctx))

    def test_gm_role_is_authorized(self):
        ctx = SimpleNamespace(
            guild=object(),
            author=SimpleNamespace(
                id=999,
                roles=[SimpleNamespace(id=456)],
                guild_permissions=SimpleNamespace(administrator=False),
            ),
        )
        fake_settings = SimpleNamespace(owner_id=123, gm_role_id=456)
        with patch("commands.utility.settings", fake_settings):
            self.assertTrue(has_admin_permissions(ctx))


if __name__ == "__main__":
    unittest.main()
