from config.settings import settings


async def manual_send(bot, user_id: int, content: str) -> None:
    try:
        user = await bot.fetch_user(user_id)
        await user.send(content)
        print(f"[dm_sender] Wysłano DM do {user.name} ({user_id}): {content}")
    except Exception as e:
        print(f"[dm_sender][ERROR] Nie udało się wysłać DM do {user_id}: {e}")


async def send_admin_dm(bot, content: str) -> None:
    if settings.owner_id is None:
        print("[dm_sender][WARN] Brakuje BOT_OWNER_ID/ADMIN_ID — pomijam wiadomość do właściciela.")
        return
    try:
        admin = await bot.fetch_user(settings.owner_id)
        await admin.send(content)
        print(f"[dm_sender] Wysłano DM do Admina: {content}")

    except Exception as e:
        print(f"[dm_sender][ERROR] Nie udało się wysłać DM do właściciela: {e}")


async def send_user_dm(bot, user_id: int, content: str) -> None:
    try:
        user = await bot.fetch_user(user_id)
        await user.send(content)
        print(f"[dm_sender] Wysłano DM do {user.name} ({user_id}): {content}")
    except Exception as e:
        print(f"[dm_sender][ERROR] Nie udało się wysłać DM do {user_id}: {e}")


async def send_startup_dm(bot) -> None:
    if settings.owner_id is not None:
        await manual_send(bot, settings.owner_id, "Shadow: uruchomiony i gotowy do akcji.")
