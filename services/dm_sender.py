import os

admin = int(os.getenv("ADMIN_ID"))


async def send_startup_dm(bot):
    user_admin = await bot.fetch_user(admin)
    try:
        await user_admin.send("test test")
    except Exception as e:
        print(f"Nie mogę wysłać wiadomości: {e}")
