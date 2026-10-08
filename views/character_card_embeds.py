import discord

from services.character_card import (
    CharacterCard,
)
from views.character_card_utils import (
    add_field,
    add_section,
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

MAIN_STATS = (
    "WW",
    "US",
    "K",
    "ODP",
    "ZR",
    "INT",
    "SW",
    "OGD",
)

SECONDARY_STATS = (
    "A",
    "ŻYW",
    "S",
    "WT",
    "H",
    "SZ",
    "MAG",
    "PO",
    "PP",
)

PROFILE_INLINE_VALUE_LIMIT = 32
PROFILE_INLINE_LABEL_LIMIT = 24

PROFILE_HANDLED_FIELDS = {
    "Wiek",
    "Wzrost",
    "Waga",
    "Włosy",
    "Oczy",
    "Cechy fizyczne",
    "Cechy psychicz.",
    "Choroby psych.",
    "Charakter",
    "Wróżba",
    "Rodzina",
    "Obecne Żyw",
    "Punkty Grzechu",
    "Punkty Szczęścia",
    "PP",
    "P.Obłędu",
    "PDki wydane",
    "niewydane",
    "PD razem",
    "Błogosławieństwa",
    "Gniew Boży",
    "Byłe profesje",
}


def _build_base_embed(
        card: CharacterCard,
        page_name: str,
) -> discord.Embed:
    title = card.full_name

    if page_name != "Bohater":
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
        color=CARD_COLOR,
    )

    embed.set_footer(
        text=FOOTER_TEXT
    )

    return embed


def _is_compact_profile_field(
        label: str,
        value: str,
) -> bool:
    return (
            len(label)
            <= PROFILE_INLINE_LABEL_LIMIT

            and len(value)
            <= PROFILE_INLINE_VALUE_LIMIT

            and "\n" not in value
    )


def _profile_map(
        card: CharacterCard,
) -> dict[str, str]:
    return {
        label: value
        for label, value
        in card.profile_fields
    }


def _add_empty_profile_field(
        embed: discord.Embed,
) -> None:
    add_field(
        embed,
        "\u200b",
        "\u200b",
        inline=True,
    )


def _add_profile_row(
        embed: discord.Embed,
        profile: dict[str, str],
        labels,
) -> None:
    has_value = any(
        label is not None
        and profile.get(label)
        for label in labels
    )

    if not has_value:
        return

    for label in labels:
        if label is None:
            _add_empty_profile_field(
                embed
            )
            continue

        value = profile.get(label)

        if not value:
            _add_empty_profile_field(
                embed
            )
            continue

        add_field(
            embed,
            safe(label),
            safe(value),
            inline=True,
        )


def _add_profile_full_field(
        embed: discord.Embed,
        profile: dict[str, str],
        label: str,
) -> None:
    value = profile.get(label)

    if not value:
        return

    add_field(
        embed,
        safe(label),
        safe(value),
        inline=False,
    )


def _build_profile_embed(
        card: CharacterCard,
) -> discord.Embed:
    embed = _build_base_embed(
        card,
        "Bohater",
    )

    profile = _profile_map(
        card
    )

    _add_profile_row(
        embed,
        profile,
        (
            "Wiek",
            "Wzrost",
            "Waga",
        ),
    )

    _add_profile_row(
        embed,
        profile,
        (
            "Włosy",
            "Oczy",
            None,
        ),
    )

    _add_profile_full_field(
        embed,
        profile,
        "Cechy fizyczne",
    )

    _add_profile_row(
        embed,
        profile,
        (
            "Cechy psychicz.",
            "Choroby psych.",
            "Charakter",
        ),
    )

    _add_profile_full_field(
        embed,
        profile,
        "Wróżba",
    )

    _add_profile_row(
        embed,
        profile,
        (
            "Obecne Żyw",
            "Punkty Grzechu",
            "Punkty Szczęścia",
        ),
    )

    _add_profile_row(
        embed,
        profile,
        (
            "PP",
            "P.Obłędu",
            None,
        ),
    )

    for label, value in card.profile_fields:
        if label in PROFILE_HANDLED_FIELDS:
            continue

        add_field(
            embed,
            safe(label),
            safe(value),
            inline=(
                _is_compact_profile_field(
                    label,
                    value,
                )
            ),
        )

    _add_profile_row(
        embed,
        profile,
        (
            "PDki wydane",
            "niewydane",
            "PD razem",
        ),
    )

    _add_profile_row(
        embed,
        profile,
        (
            "Błogosławieństwa",
            "Gniew Boży",
            "Byłe profesje",
        ),
    )

    if not embed.fields:
        add_field(
            embed,
            "Bohater",
            "Brak dodatkowych danych.",
        )

    return embed


def _stat_map(
        card: CharacterCard,
) -> dict:
    return {
        stat.abbreviation.casefold(): stat
        for stat in card.stats
    }


def _build_stat_table(
        card: CharacterCard,
        order,
) -> str:
    stats = _stat_map(card)

    selected = []

    for abbreviation in order:
        stat = stats.get(
            abbreviation.casefold()
        )

        if stat is None:
            continue

        selected.append(
            (
                abbreviation,
                stat.base_value,
                stat.development_value,
                stat.final_value,
            )
        )

    if not selected:
        return ""

    column_widths = [
        max(
            3,
            len(abbreviation),
            len(base_value),
            len(development_value),
            len(final_value),
        )
        for (
            abbreviation,
            base_value,
            development_value,
            final_value,
        ) in selected
    ]

    row_label_width = len(
        "Podstawowa"
    )

    header = (
            " " * row_label_width
            + "  "
            + "  ".join(
        abbreviation.center(width)
        for (
            abbreviation,
            _,
            _,
            _,
        ), width in zip(
            selected,
            column_widths,
        )
    )
    )

    def build_row(
            label: str,
            value_index: int,
    ) -> str:
        return (
                label.ljust(
                    row_label_width
                )
                + "  "
                + "  ".join(
            values[
                value_index
            ].center(width)
            for (
                values,
                width,
            ) in zip(
                selected,
                column_widths,
            )
        )
        )

    return (
        "```text\n"
        f"{header}\n"
        f"{build_row('Podstawowa', 1)}\n"
        f"{build_row('Rozwój', 2)}\n"
        f"{build_row('Końcowa', 3)}\n"
        "```"
    )


def _build_stats_embed(
        card: CharacterCard,
) -> discord.Embed:
    embed = _build_base_embed(
        card,
        "Cechy",
    )

    main_stats = _build_stat_table(
        card,
        MAIN_STATS,
    )

    if main_stats:
        add_field(
            embed,
            "CECHY GŁÓWNE",
            main_stats,
        )

    secondary_stats = (
        _build_stat_table(
            card,
            SECONDARY_STATS,
        )
    )

    if secondary_stats:
        add_field(
            embed,
            "CECHY DRUGORZĘDNE",
            secondary_stats,
        )

    if not embed.fields:
        add_field(
            embed,
            "Cechy",
            "Brak danych.",
        )

    return embed


def _format_sorted_list(
        values: list[str],
) -> str:
    sorted_values = sorted(
        values,
        key=str.casefold,
    )

    return "\n".join(
        f"• {safe(value)}"
        for value in sorted_values
    )


def _build_skills_embed(
        card: CharacterCard,
) -> discord.Embed:
    embed = _build_base_embed(
        card,
        "Umiejętności",
    )

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
            _format_sorted_list(
                skills
            ),
            inline=True,
        )

    if abilities:
        add_field(
            embed,
            "ZDOLNOŚCI",
            _format_sorted_list(
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


def _build_magic_embed(
        card: CharacterCard,
) -> discord.Embed:
    embed = _build_base_embed(
        card,
        "Magia",
    )

    for spell in (
            card.get_magic_entries()
    ):
        add_field(
            embed,
            safe(spell.name),
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


def _build_combat_embed(
        card: CharacterCard,
) -> discord.Embed:
    embed = _build_base_embed(
        card,
        "Walka",
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


def _build_equipment_embed(
        card: CharacterCard,
) -> discord.Embed:
    embed = _build_base_embed(
        card,
        "Ekwipunek",
    )

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


PAGE_BUILDERS = {
    "profile": _build_profile_embed,
    "stats": _build_stats_embed,
    "skills": _build_skills_embed,
    "magic": _build_magic_embed,
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
