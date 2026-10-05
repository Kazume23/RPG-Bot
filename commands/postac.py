import asyncio
import logging

import discord

from commands.utility import (
    command_usage,
    has_admin_permissions,
)
from services.google_sheets import (
    CharacterNotFoundError,
    CharacterNotLinkedError,
    CharacterSheetFormatError,
    GoogleSheetsConfigurationError,
    get_character_by_discord_id,
    get_character_by_name,
)


logger = logging.getLogger(__name__)


def _safe(value) -> str:
    return discord.utils.escape_markdown(str(value))


def format_character(character: dict) -> str:
    name = character.get("Imię", "Nieznana postać")
    surname = character.get("Nazwisko", "")

    full_name = f"{name} {surname}".strip()

    lines = [
        f"## {_safe(full_name)}"
    ]

    for label, value in character.items():
        if label in {"Imię", "Nazwisko"}:
            continue

        if not value:
            continue

        if isinstance(value, list):
            lines.append("")
            lines.append(f"**{_safe(label)}**")

            for item in value:
                lines.append(f"• {_safe(item)}")

            continue

        lines.append(
            f"**{_safe(label)}:** {_safe(value)}"
        )

    return "\n".join(lines)


async def postac_command(ctx, args: str):
    character_name = args.strip()

    if character_name and not has_admin_permissions(ctx):
        return "Nie masz uprawnień do wyświetlania cudzej postaci chuju."

    try:
        if character_name:
            character = await asyncio.to_thread(
                get_character_by_name,
                character_name,
            )
        else:
            character = await asyncio.to_thread(
                get_character_by_discord_id,
                ctx.author.id,
            )

    except CharacterNotLinkedError:
        return (
            "Nie masz przypisanej postaci. "
            f"Pierdol się."
        )

    except CharacterNotFoundError:
        return (
            f"Nie znaleziono postaci "
            f"`{_safe(character_name)}`."
        )

    except (
        GoogleSheetsConfigurationError,
        CharacterSheetFormatError,
    ):
        logger.exception(
            "Błąd konfiguracji Google Sheets"
        )
        return "Nie mogę teraz odczytać karty postaci."

    except Exception:
        logger.exception(
            "Coś się wyjebało i nie wiem co"
        )
        return "Nie mogę teraz odczytać karty postaci."

    return format_character(character)