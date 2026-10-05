import logging

import discord

from services.character_card import (
    CharacterCard,
)


logger = logging.getLogger(__name__)


VIEW_TIMEOUT = 300

FIELD_VALUE_LIMIT = 1024
FIELD_NAME_LIMIT = 256
MAX_FIELDS = 25
MAX_EMBED_LENGTH = 5800


PAGE_DEFINITIONS = (
    (
        "profile",
        "Profil",
        "👤",
    ),
    (
        "stats",
        "Cechy",
        "⚔️",
    ),
    (
        "skills",
        "Umiejętności",
        "📚",
    ),
    (
        "combat",
        "Walka",
        "🛡️",
    ),
    (
        "equipment",
        "Ekwipunek",
        "🎒",
    ),
)


def _safe(value) -> str:
    return discord.utils.escape_markdown(
        str(value).strip()
    )


def _inline_code(
    value,
) -> str:
    safe_value = str(value).replace(
        "`",
        "'",
    )

    return f"`{safe_value}`"


def _embed_length(
    embed: discord.Embed,
) -> int:
    total = len(
        embed.title or ""
    )

    total += len(
        embed.description or ""
    )

    footer_text = getattr(
        embed.footer,
        "text",
        None,
    )

    if footer_text:
        total += len(footer_text)

    for field in embed.fields:
        total += len(field.name)
        total += len(field.value)

    return total


def _split_text(
    text: str,
    limit: int = FIELD_VALUE_LIMIT,
) -> list[str]:
    if len(text) <= limit:
        return [text]

    chunks = []
    current = ""

    for line in text.splitlines():
        if len(line) > limit:
            if current:
                chunks.append(current)
                current = ""

            for start in range(
                0,
                len(line),
                limit,
            ):
                chunks.append(
                    line[
                        start:
                        start + limit
                    ]
                )

            continue

        candidate = line

        if current:
            candidate = (
                f"{current}\n{line}"
            )

        if len(candidate) <= limit:
            current = candidate
            continue

        chunks.append(current)
        current = line

    if current:
        chunks.append(current)

    return chunks


def _add_field(
    embed: discord.Embed,
    name: str,
    value: str,
    inline: bool = False,
) -> bool:
    if len(embed.fields) >= MAX_FIELDS:
        return False

    name = name[:FIELD_NAME_LIMIT]

    remaining = (
        MAX_EMBED_LENGTH
        - _embed_length(embed)
        - len(name)
    )

    if remaining <= 0:
        return False

    max_value_length = min(
        FIELD_VALUE_LIMIT,
        remaining,
    )

    value = value[:max_value_length]

    if not value:
        return False

    embed.add_field(
        name=name,
        value=value,
        inline=inline,
    )

    return True


def _add_section(
    embed: discord.Embed,
    title: str,
    values: list[str],
    bullets: bool = True,
) -> None:
    if not values:
        return

    if bullets:
        lines = [
            f"• {_safe(value)}"
            for value in values
        ]
    else:
        lines = values

    text = "\n".join(lines)

    for index, chunk in enumerate(
        _split_text(text)
    ):
        field_name = (
            title
            if index == 0
            else f"{title} (cd.)"
        )

        if not _add_field(
            embed,
            field_name,
            chunk,
        ):
            return


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
        _safe(value)
        for value in card.subtitle_parts
    )

    embed = discord.Embed(
        title=_safe(title)[:256],
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
            f"**{_safe(label)}:** "
            f"{_safe(value)}"
        )
        for label, value
        in card.profile_fields
    ]

    if profile_lines:
        _add_section(
            embed,
            "Informacje",
            profile_lines,
            bullets=False,
        )
    else:
        _add_field(
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
            f"**{_safe(stat.current_value)}**"
        )

        if (
            stat.value
            != stat.current_value
        ):
            value += (
                "\n"
                f"{_inline_code(stat.value)}"
            )

        if not _add_field(
            embed,
            _safe(stat.abbreviation),
            value,
            inline=True,
        ):
            break

    if not embed.fields:
        _add_field(
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

    _add_section(
        embed,
        "Umiejętności",
        card.get_section(
            "Umiejętności"
        ),
    )

    _add_section(
        embed,
        "Zdolności",
        card.get_section(
            "Zdolności"
        ),
    )

    _add_section(
        embed,
        "Magia",
        card.get_section(
            "Magia"
        ),
    )

    if not embed.fields:
        _add_field(
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

    _add_section(
        embed,
        "Broń",
        card.get_section(
            "Broń"
        ),
    )

    _add_section(
        embed,
        "Pancerz",
        card.get_section(
            "Pancerz"
        ),
    )

    if not embed.fields:
        _add_field(
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

    _add_section(
        embed,
        "Ekwipunek",
        card.get_section(
            "Ekwipunek"
        ),
    )

    _add_section(
        embed,
        "Monety",
        card.get_section(
            "Monety"
        ),
    )

    if not embed.fields:
        _add_field(
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


class CharacterPageButton(
    discord.ui.Button
):
    def __init__(
        self,
        page: str,
        label: str,
        emoji: str,
        active: bool = False,
    ):
        style = (
            discord.ButtonStyle.primary
            if active
            else discord.ButtonStyle.secondary
        )

        super().__init__(
            label=label,
            emoji=emoji,
            style=style,
        )

        self.page = page

    async def callback(
        self,
        interaction: discord.Interaction,
    ):
        view = self.view

        if not isinstance(
            view,
            CharacterCardView,
        ):
            return

        await view.show_page(
            interaction,
            self.page,
        )


class CharacterCardView(
    discord.ui.View
):
    def __init__(
        self,
        card: CharacterCard,
        requester_id: int,
    ):
        super().__init__(
            timeout=VIEW_TIMEOUT
        )

        self.card = card
        self.requester_id = requester_id
        self.message = None

        for page, label, emoji in PAGE_DEFINITIONS:
            self.add_item(
                CharacterPageButton(
                    page=page,
                    label=label,
                    emoji=emoji,
                    active=(
                        page == "profile"
                    ),
                )
            )

    def bind_message(
        self,
        message: discord.Message,
    ) -> None:
        self.message = message

    def initial_embed(
        self,
    ) -> discord.Embed:
        return build_character_embed(
            self.card,
            "profile",
        )

    async def interaction_check(
        self,
        interaction: discord.Interaction,
    ) -> bool:
        if (
            interaction.user.id
            == self.requester_id
        ):
            return True

        await interaction.response.send_message(
            "To nie jest twoja karta do klikania.",
            ephemeral=True,
        )

        return False

    def _set_active_page(
        self,
        page: str,
    ) -> None:
        for item in self.children:
            if not isinstance(
                item,
                CharacterPageButton,
            ):
                continue

            item.style = (
                discord.ButtonStyle.primary
                if item.page == page
                else discord.ButtonStyle.secondary
            )

    async def show_page(
        self,
        interaction: discord.Interaction,
        page: str,
    ) -> None:
        self._set_active_page(page)

        embed = build_character_embed(
            self.card,
            page,
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self,
        )

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        if self.message is None:
            return

        try:
            await self.message.edit(
                view=self
            )

        except (
            discord.NotFound,
            discord.HTTPException,
        ):
            pass

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
        item,
    ):
        logger.error(
            "Błąd podczas obsługi "
            "interaktywnej karty postaci",
            exc_info=(
                type(error),
                error,
                error.__traceback__,
            ),
        )

        message = (
            "Coś się wyjebało podczas "
            "obsługi karty postaci."
        )

        try:
            if interaction.response.is_done():
                await interaction.followup.send(
                    message,
                    ephemeral=True,
                )
                return

            await interaction.response.send_message(
                message,
                ephemeral=True,
            )

        except discord.HTTPException:
            pass