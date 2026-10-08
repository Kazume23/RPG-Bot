import discord

from services.character_card import (
    CharacterCard,
)
from views.character_card_utils import (
    add_field,
    add_section,
    safe,
)


def build_equipment_embed(
        card: CharacterCard,
        embed: discord.Embed,
) -> discord.Embed:
    money = card.get_section(
        "Monety"
    )

    if money:
        add_field(
            embed,
            "PIENIĄDZE",
            " • ".join(
                safe(value)
                for value in money
            ),
        )

    add_section(
        embed,
        "WYPOSAŻENIE",
        card.get_section(
            "Ekwipunek"
        ),
    )

    if not embed.fields:
        add_field(
            embed,
            "Ekwipunek",
            "Brak danych.",
        )

    return embed
