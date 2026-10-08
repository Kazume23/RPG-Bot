import asyncio
import logging

import discord

from commands.utility import (
    has_admin_permissions,
)
from services.character_card import (
    build_character_card,
)
from services.google_sheets import (
    CharacterNotFoundError,
    CharacterNotLinkedError,
    CharacterSheetFormatError,
    GoogleSheetsConfigurationError,
    get_character_by_discord_id,
    get_character_by_name,
)
from views.character_card_view import (
    CharacterCardView,
    register_character_card,
)

logger = logging.getLogger(__name__)


def _safe(value) -> str:
    return discord.utils.escape_markdown(
        str(value).strip()
    )


async def _load_character(
        ctx,
        character_name: str,
) -> dict:
    if character_name:
        return await asyncio.to_thread(
            get_character_by_name,
            character_name,
        )

    return await asyncio.to_thread(
        get_character_by_discord_id,
        ctx.author.id,
    )


async def postac_command(
        ctx,
        args: str,
):
    character_name = args.strip()

    if (
            character_name
            and not has_admin_permissions(ctx)
    ):
        return (
            "Nie masz uprawnień do "
            "wyświetlania cudzej postaci chuju."
        )

    try:
        character_data = await _load_character(
            ctx,
            character_name,
        )

    except CharacterNotLinkedError:
        return (
            "Nie masz przypisanej postaci. "
            "Pierdol się."
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

        return (
            "Nie mogę teraz odczytać "
            "karty postaci."
        )

    except Exception:
        logger.exception(
            "Nieoczekiwany błąd podczas "
            "odczytu karty postaci"
        )

        return (
            "Nie mogę teraz odczytać "
            "karty postaci."
        )

    card = build_character_card(
        character_data
    )

    view = CharacterCardView(
        card=card,
        requester_id=ctx.author.id,
    )

    message = await ctx.channel.send(
        embed=view.initial_embed(),
        view=view,
    )

    view.bind_message(message)

    await register_character_card(
        view
    )

    return None
