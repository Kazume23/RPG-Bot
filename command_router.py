import discord

from config.settings import COMMAND_PREFIX
from core.command_context import CommandContext


def should_handle(message: discord.Message) -> bool:
    return message.content.strip().startswith(COMMAND_PREFIX)


async def process_message(message: discord.Message, bot):
    return await process_commands(CommandContext(bot, message))


async def process_commands(ctx: CommandContext):
    import commands

    parts = ctx.content.strip().split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1].strip() if len(parts) > 1 else ""

    if cmd == f"{COMMAND_PREFIX}dm":
        return await commands.dm_command(ctx, args)
    if cmd == f"{COMMAND_PREFIX}sesja":
        return await commands.sesja_command(ctx, args)
    if cmd == f"{COMMAND_PREFIX}purge":
        return await commands.purge_command(ctx, args)
    if cmd == f"{COMMAND_PREFIX}hello":
        return await commands.hello_command()
    if cmd == f"{COMMAND_PREFIX}ochlapus":
        return await commands.ochlapus_command(args)
    if cmd == f"{COMMAND_PREFIX}u":
        return await commands.umiejki_command(args)
    if cmd == f"{COMMAND_PREFIX}z":
        return await commands.zdolnosci_command(args)
    if cmd == f"{COMMAND_PREFIX}roll":
        return await commands.roll_command(args)
    if cmd == f"{COMMAND_PREFIX}ukryty":
        return await commands.ukryty_command(ctx, args)
    if cmd == f"{COMMAND_PREFIX}klnij":
        return await commands.klnij_command()
    if cmd == f"{COMMAND_PREFIX}help":
        return await commands.help_command()
    if cmd in (f"{COMMAND_PREFIX}wy", f"{COMMAND_PREFIX}wydarzenia"):
        return await commands.wydarzenia_command(ctx, args)
    if cmd in (f"{COMMAND_PREFIX}not", f"{COMMAND_PREFIX}notatki"):
        return await commands.notatka_command(ctx, args)
    if cmd == f"{COMMAND_PREFIX}npc":
        return await commands.npc_command(ctx, args)
    if cmd == f"{COMMAND_PREFIX}class":
        return await commands.classes_command(args)

    return f"Nieznana komenda. Wpisz `{COMMAND_PREFIX}help`, żeby zobaczyć dostępne komendy."
