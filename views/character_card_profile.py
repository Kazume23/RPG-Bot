import discord

from services.character_card import (
    CharacterCard,
)
from views.character_card_utils import (
    add_field,
    profile_map,
    safe,
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


def _add_empty_field(
        embed: discord.Embed,
) -> None:
    add_field(
        embed,
        "\u200b",
        "\u200b",
        inline=True,
    )


def _add_row(
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
            _add_empty_field(
                embed
            )
            continue

        value = profile.get(
            label
        )

        if not value:
            _add_empty_field(
                embed
            )
            continue

        add_field(
            embed,
            safe(label),
            safe(value),
            inline=True,
        )


def _add_full_field(
        embed: discord.Embed,
        profile: dict[str, str],
        label: str,
) -> None:
    value = profile.get(
        label
    )

    if not value:
        return

    add_field(
        embed,
        safe(label),
        safe(value),
        inline=False,
    )


def build_profile_embed(
        card: CharacterCard,
        embed: discord.Embed,
) -> discord.Embed:
    profile = profile_map(
        card
    )

    _add_row(
        embed,
        profile,
        (
            "Wiek",
            "Wzrost",
            "Waga",
        ),
    )

    _add_row(
        embed,
        profile,
        (
            "Włosy",
            "Oczy",
            None,
        ),
    )

    _add_full_field(
        embed,
        profile,
        "Cechy fizyczne",
    )

    _add_row(
        embed,
        profile,
        (
            "Cechy psychicz.",
            "Choroby psych.",
            "Charakter",
        ),
    )

    _add_full_field(
        embed,
        profile,
        "Wróżba",
    )

    _add_row(
        embed,
        profile,
        (
            "Obecne Żyw",
            "Punkty Grzechu",
            "Punkty Szczęścia",
        ),
    )

    _add_row(
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

    _add_row(
        embed,
        profile,
        (
            "PDki wydane",
            "niewydane",
            "PD razem",
        ),
    )

    _add_row(
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
