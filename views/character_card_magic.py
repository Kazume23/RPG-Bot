import discord

from services.character_card import (
    CharacterCard,
)
from views.character_card_utils import (
    add_field,
    safe,
)


def build_magic_embed(
        card: CharacterCard,
        embed: discord.Embed,
) -> discord.Embed:
    for spell in card.get_magic_entries():
        add_field(
            embed,
            safe(
                spell.name
            ),
            (
                f"**Poziom mocy:** "
                f"{safe(spell.power_level)}\n"
                f"**Czas rzucania:** "
                f"{safe(spell.casting_time)}"
            ),
        )

    if not embed.fields:
        add_field(
            embed,
            "Magia",
            "Brak danych.",
        )

    return embed
