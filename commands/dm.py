import discord
from commands.utility import has_admin_permissions


async def dm_command(ctx, args: str):
    if not has_admin_permissions(ctx):
        return "Spierdalaj. Nie masz nade mną władzy śmiertelniku"

    if not args:
        return "Użyj poprawnej składni: `>dm <nazwa kanału> <wiadomość>`"

    parts = args.split(maxsplit=1)
    if len(parts) < 2:
        return "Użyj poprawnej składni: `>dm <nazwa kanału> <wiadomość>`"

    channel_name, msg = parts[0], parts[1]
    target_channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)

    if target_channel:
        await target_channel.send(msg)
        return f"✅ Wiadomość wysłana na kanał **#{channel_name}**"
    else:
        return f"❌ Nie znaleziono kanału **#{channel_name}**"
