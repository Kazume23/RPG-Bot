import discord
from commands.utility import has_admin_permissions


async def dm_command(ctx):
    if not has_admin_permissions(ctx):
        return "Spierdalaj. Nie masz nade mną władzy śmiertelniku"

    parts = ctx.content.split(maxsplit=2)
    if len(parts) < 3:
        return "Użyj poprawnej składni: `>dm <nazwa kanału> <wiadomość>`"

    channel_name = parts[1]
    msg = parts[2]

    target_channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)

    if target_channel:
        await target_channel.send(msg)
        return f"✅ Wiadomość wysłana na kanał **#{channel_name}**"
    else:
        return f"❌ Nie znaleziono kanału **#{channel_name}**"
