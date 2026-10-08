import logging

import discord

from services.character_card import (
    CharacterCard,
)
from views.character_card_embeds import (
    build_character_embed,
)

logger = logging.getLogger(__name__)

VIEW_TIMEOUT = 300

PAGE_DEFINITIONS = (
    (
        "profile",
        "Bohater",
    ),
    (
        "stats",
        "Cechy",
    ),
    (
        "skills",
        "Umiejętności",
    ),
    (
        "combat",
        "Walka",
    ),
    (
        "equipment",
        "Ekwipunek",
    ),
)

MAGIC_PAGE_DEFINITION = (
    "magic",
    "Magia",
)


class CharacterPageButton(
    discord.ui.Button
):
    def __init__(
            self,
            page: str,
            label: str,
            active: bool = False,
    ):
        self.page = page
        self.base_label = label

        display_label = (
            f"• {label}"
            if active
            else label
        )

        super().__init__(
            label=display_label,
            style=(
                discord.ButtonStyle.secondary
            ),
        )

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

        pages = list(
            PAGE_DEFINITIONS
        )

        if card.get_section("Magia"):
            pages.append(
                MAGIC_PAGE_DEFINITION
            )

        for (
                page,
                label,
        ) in pages:
            self.add_item(
                CharacterPageButton(
                    page=page,
                    label=label,
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
            (
                "To nie jest twoja karta "
                "do klikania."
            ),
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

            item.label = (
                f"• {item.base_label}"
                if item.page == page
                else item.base_label
            )

    async def show_page(
            self,
            interaction: discord.Interaction,
            page: str,
    ) -> None:
        self._set_active_page(
            page
        )

        embed = build_character_embed(
            self.card,
            page,
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self,
        )

    async def on_timeout(
            self,
    ):
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
            (
                "Błąd podczas obsługi "
                "interaktywnej karty postaci"
            ),
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
