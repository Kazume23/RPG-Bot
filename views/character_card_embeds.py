import discord

from services.character_card import (
    CharacterCard,
)
from views.character_card_utils import (
    add_field,
    add_section,
    inline_code,
    safe,
)


def _build_base_embed(
        card: CharacterCard,
        page_name: str,
) -> discord.Embed:
    title = card.full_name

    if page_name != "Profil":
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
        description=description or None,
        color=discord.Color.dark_gold(),
    )

    embed.set_footer(
        text="Karta postaci • Google Sheets"
    )

    return embed


def _build_profile_embed(
        card: CharacterCard,
) -> discord.Embed:
    embed = _build_base_embed(
        card,
        "Profil",
    )

    profile_lines = [
        (
            f"**{safe(label)}:** "
            f"{safe(value)}"
        )
        for label, value
        in card.profile_fields
    ]

    if profile_lines:
        add_section(
            embed,
            "Informacje",
            profile_lines,
            bullets=False,
        )
    else:
        add_field(
            embed,
            "Informacje",
            "Brak dodatkowych danych.",
        )

    return embed


def _build_stats_embed(
        card: CharacterCard,
) -> discord.Embed:
    embed = _build_base_embed(
        card,
        "Cechy",
    )

    for stat in card.stats:
        value = (
            f"**{safe(stat.current_value)}**"
        )

        if (
                stat.value
                != stat.current_value
        ):
            value += (
                "\n"
                f"{inline_code(stat.value)}"
            )

        if not add_field(
                embed,
                safe(stat.abbreviation),
                value,
                inline=True,
        ):
            break

    if not embed.fields:
        add_field(
            embed,
            "Cechy",
            "Brak danych.",
        )

    return embed


def _build_skills_embed(
        card: CharacterCard,
) -> discord.Embed:
    embed = _build_base_embed(
        card,
        "Umiejętności",
    )

    add_section(
        embed,
        "Umiejętności",
        card.get_section(
            "Umiejętności"
        ),
    )

    add_section(
        embed,
        "Zdolności",
        card.get_section(
            "Zdolności"
        ),
    )

    add_section(
        embed,
        "Magia",
        card.get_section(
            "Magia"
        ),
    )

    if not embed.fields:
        add_field(
            embed,
            "Umiejętności",
            "Brak danych.",
        )

    return embed


def _build_combat_embed(
        card: CharacterCard,
) -> discord.Embed:
    embed = _build_base_embed(
        card,
        "Walka",
    )

    add_section(
        embed,
        "Broń",
        card.get_section(
            "Broń"
        ),
    )

    add_section(
        embed,
        "Pancerz",
        card.get_section(
            "Pancerz"
        ),
    )

    if not embed.fields:
        add_field(
            embed,
            "Walka",
            "Brak danych.",
        )

    return embed


def _build_equipment_embed(
        card: CharacterCard,
) -> discord.Embed:
    embed = _build_base_embed(
        card,
        "Ekwipunek",
    )

    add_section(
        embed,
        "Ekwipunek",
        card.get_section(
            "Ekwipunek"
        ),
    )

    add_section(
        embed,
        "Monety",
        card.get_section(
            "Monety"
        ),
    )

    if not embed.fields:
        add_field(
            embed,
            "Ekwipunek",
            "Brak danych.",
        )

    return embed


PAGE_BUILDERS = {
    "profile": _build_profile_embed,
    "stats": _build_stats_embed,
    "skills": _build_skills_embed,
    "combat": _build_combat_embed,
    "equipment": _build_equipment_embed,
}


def build_character_embed(
        card: CharacterCard,
        page: str = "profile",
) -> discord.Embed:
    builder = PAGE_BUILDERS.get(
        page,
        _build_profile_embed,
    )

    return builder(card)
