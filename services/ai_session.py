from core.shadow import toggle_session, admin


async def start_session_ai(bot, personality: str = "none"):
    user = await bot.fetch_user(admin)
    dm_channel = await user.create_dm()

    response = toggle_session("ARISE", personality=personality, message=MockMessage(admin, dm_channel.id))
    await dm_channel.send(response)


class MockMessage:
    def __init__(self, user_id, channel_id):
        self.author = type("obj", (object,), {"id": user_id})
        self.channel = type("obj", (object,), {"id": channel_id})
        self.guild = None
        self.content = ""
