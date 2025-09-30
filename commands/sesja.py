import discord
from commands.utility import has_admin_permissions

async def send_sesja_message(ctx, channel):
    text = """
    @everyone
    Kiedy sesja kurwy?
    
    Poniedziałek \N{PARTY POPPER}
    Wtorek \N{EGG}
    Środa \N{PEOPLE HUGGING}
    Czwartek \N{CLINKING BEER MUGS}
    Piątek \N{FLEXED BICEPS}
    Sobota \N{EYE}
    Niedziela \N{FIRE}
    """

    message = await channel.send(text)

    emojis = ["\N{PARTY POPPER}", "\N{EGG}", "\N{PEOPLE HUGGING}", "\N{CLINKING BEER MUGS}", "\N{FLEXED BICEPS}",
              "\N{EYE}", "\N{FIRE}"]

    for emoji in emojis:
        try:
            await message.add_reaction(emoji)
        except discord.errors.HTTPException as e:
            print(f"Error adding emoji {emoji}: {e}")


async def sesja_command(ctx):
    if not has_admin_permissions(ctx):
        return "Spierdalaj. Nie masz nade mną władzy śmiertelniku"

    channel_name = ctx.content[len(">sesja"):].strip()

    channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)

    if channel:
        await send_sesja_message(ctx, channel)
        return f"Sesja została zaplanowana na kanale #{channel_name}!"
    else:
        return "Nie udało się znaleźć kanału o podanej nazwie."
