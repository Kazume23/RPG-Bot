import discord

from services.character_card import (
    CharacterCard,
)
from views.character_card_combat import (
    build_combat_embed,
)
from views.character_card_equipment import (
    build_equipment_embed,
)
from views.character_card_magic import (
    build_magic_embed,
)
from views.character_card_profile import (
    build_profile_embed,
)
from views.character_card_skills import (
    build_skills_embed,
)
from views.character_card_stats import (
    build_stats_embed,
)
from views.character_card_utils import (
    safe,
)

CARD_COLOR = discord.Color.from_rgb(
    112,
    77,
    45,
)

FOOTER_TEXT = (
    "Warhammer Fantasy Roleplay 2e "
    "• Karta postaci"
)

PAGE_NAMES = {
    "profile": "Bohater",
    "stats": "Cechy",
    "skills": "Umiejętności",
    "combat": "Walka",
    "equipment": "Ekwipunek",
    "magic": "Magia",
}

PAGE_BUILDERS = {
    "profile": build_profile_embed,
    "stats": build_stats_embed,
    "skills": build_skills_embed,
    "combat": build_combat_embed,
    "equipment": build_equipment_embed,
    "magic": build_magic_embed,
}


def _build_base_embed(
        card: CharacterCard,
        page: str,
) -> discord.Embed:
    page_name = PAGE_NAMES.get(
        page,
        "Bohater",
    )

    title = card.full_name

    if page != "profile":
        title = (
            f"{card.full_name} "
            f"— {page_name}"
        )

    description = " • ".join(
        safe(value)
        for value in card.subtitle_parts
    )

    embed = discord.Embed(
        title=safe(title)[:256],
        description=(
                description
                or None
        ),
        color=CARD_COLOR,
    )

    embed.set_footer(
        text=FOOTER_TEXT
    )

    return embed


def build_character_embed(
        card: CharacterCard,
        page: str = "profile",
) -> discord.Embed:
    embed = _build_base_embed(
        card,
        page,
    )

    builder = PAGE_BUILDERS.get(
        page,
        build_profile_embed,
    )

    return builder(
        card,
        embed,
    )
