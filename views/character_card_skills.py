import discord

from services.character_card import (
    CharacterCard,
)
from views.character_card_utils import (
    add_field,
    format_sorted_list,
)


def build_skills_embed(
        card: CharacterCard,
        embed: discord.Embed,
) -> discord.Embed:
    skills = card.get_section(
        "Umiejętności"
    )

    abilities = card.get_section(
        "Zdolności"
    )

    if skills:
        add_field(
            embed,
            "UMIEJĘTNOŚCI",
            format_sorted_list(
                skills
            ),
            inline=True,
        )

    if abilities:
        add_field(
            embed,
            "ZDOLNOŚCI",
            format_sorted_list(
                abilities
            ),
            inline=True,
        )

    if not embed.fields:
        add_field(
            embed,
            "Umiejętności",
            "Brak danych.",
        )

    return embed
