import discord

from services.character_card import (
    CharacterCard,
)
from views.character_card_utils import (
    add_field,
    add_section,
    get_stat_value,
    profile_map,
    safe,
)


def _health_value(
        card: CharacterCard,
) -> str:
    profile = profile_map(
        card
    )

    current_health = profile.get(
        "Obecne Żyw",
        "",
    )

    max_health = get_stat_value(
        card,
        "ŻYW",
    )

    if not current_health:
        return max_health

    if "/" in current_health:
        return current_health

    if max_health == "—":
        return current_health

    return (
        f"{current_health}/{max_health}"
    )


def _add_empty_field(
        embed: discord.Embed,
) -> None:
    add_field(
        embed,
        "\u200b",
        "\u200b",
        inline=True,
    )


def _add_combat_stats(
        embed: discord.Embed,
        card: CharacterCard,
) -> None:
    first_row = (
        f"**WW** {safe(get_stat_value(card, 'WW'))}  "
        f"**US** {safe(get_stat_value(card, 'US'))}  "
        f"**ZR** {safe(get_stat_value(card, 'ZR'))}  "
        f"**SW** {safe(get_stat_value(card, 'SW'))}"
    )

    second_row = (
        f"**S** {safe(get_stat_value(card, 'S'))}  "
        f"**WT** {safe(get_stat_value(card, 'WT'))}  "
        f"**SZ** {safe(get_stat_value(card, 'SZ'))}  "
        f"**H** {safe(get_stat_value(card, 'H'))}"
    )

    third_row = (
        f"**A** {safe(get_stat_value(card, 'A'))}  "
        f"**ŻYW** {safe(_health_value(card))}  "
        f"**MAG** {safe(get_stat_value(card, 'MAG'))}"
    )

    add_field(
        embed,
        "\u200b",
        f"{first_row}\n{second_row}\n{third_row}",
        inline=False,
    )


def build_combat_embed(
        card: CharacterCard,
        embed: discord.Embed,
) -> discord.Embed:
    _add_combat_stats(
        embed,
        card,
    )

    add_section(
        embed,
        "BROŃ",
        card.get_section(
            "Broń"
        ),
    )

    add_section(
        embed,
        "PANCERZ",
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
