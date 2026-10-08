import discord

from services.character_card import (
    CharacterCard,
)
from views.character_card_utils import (
    add_field,
    stat_map,
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


def _build_stat_table(
        card: CharacterCard,
        order,
) -> str:
    stats = stat_map(
        card
    )

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
        abbreviation.center(
            width
        )
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
            ].center(
                width
            )
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


def build_stats_embed(
        card: CharacterCard,
        embed: discord.Embed,
) -> discord.Embed:
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

    secondary_stats = _build_stat_table(
        card,
        SECONDARY_STATS,
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
