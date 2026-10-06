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

        for (
                page,
                label,
                emoji,
        ) in PAGE_DEFINITIONS:
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
