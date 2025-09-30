import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))


async def manual_send(bot, user_id: int, content: str) -> None:
    try:
        user = await bot.fetch_user(user_id)
        await user.send(content)
        print(f"[dm_sender] Wysłano DM do {user.name} ({user_id}): {content}")
    except Exception as e:
        print(f"[dm_sender][ERROR] Nie udało się wysłać DM do {user_id}: {e}")


async def send_admin_dm(bot, content: str) -> None:
    try:
        admin = await bot.fetch_user(ADMIN_ID)
        await admin.send(content)
        print(f"[dm_sender] Wysłano DM do Admina: {content}")

    except Exception as e:
        print(f"[dm_sender][ERROR] Nie udało się wysłać DM do {ADMIN_ID}: {e}")


async def send_user_dm(bot, user_id: int, content: str) -> None:
    try:
        user = await bot.fetch_user(user_id)
        await user.send(content)
        print(f"[dm_sender] Wysłano DM do {user.name} ({user_id}): {content}")
    except Exception as e:
        print(f"[dm_sender][ERROR] Nie udało się wysłać DM do {user_id}: {e}")


async def send_startup_dm(bot) -> None:
    await manual_send(bot, ADMIN_ID, "Shadow: uruchomiony i gotowy do akcji.")
