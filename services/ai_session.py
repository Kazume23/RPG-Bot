from config.settings import settings
from core.shadow import toggle_session


async def start_session_ai(bot, personality: str = "none"):
    if settings.owner_id is None:
        print("[ai_session][WARN] Brakuje BOT_OWNER_ID/ADMIN_ID — nie uruchamiam sesji AI.")
        return

    user = await bot.fetch_user(settings.owner_id)
    dm_channel = await user.create_dm()

    response = toggle_session(
        "ARISE",
        personality=personality,
        message=MockMessage(settings.owner_id, dm_channel.id),
    )

    if response and response.strip():
        await dm_channel.send(response)
    else:
        print("[WARN] Nie wysłano wiadomości – response był pusty lub None.")


class MockMessage:
    def __init__(self, user_id, channel_id):
        self.author = type("obj", (object,), {"id": user_id})
        self.channel = type("obj", (object,), {"id": channel_id})
        self.guild = None
        self.content = ""
