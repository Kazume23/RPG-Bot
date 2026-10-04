import discord

from config.settings import COMMAND_PREFIX
from core import shadow
from core.shadow_context import ShadowContext


async def get_response(message: discord.Message):
    p_message = message.content.strip()
    parts = p_message.split()
    command = parts[0].lower() if parts else ""

    if command == f"{COMMAND_PREFIX}arise":
        if len(parts) == 1:
            return shadow.toggle_session("ARISE", "none", message)
        elif len(parts) == 2:
            return shadow.toggle_session("ARISE", parts[1], message)
        else:
            return (
                f"Użycie: {COMMAND_PREFIX}arise <osobowość>. Dostępne: "
                + ", ".join(shadow.PERSONALITIES.keys())
            )

    if command == f"{COMMAND_PREFIX}cease":
        if len(parts) != 1:
            return f"Użycie: {COMMAND_PREFIX}cease"
        return shadow.toggle_session("CEASE", message=message)

    if p_message.startswith(COMMAND_PREFIX):
        ctx = ShadowContext(message._state._get_client(), message)
        return await process_commands(ctx)

    if shadow.is_session_active(message.channel.id):
        return await shadow.get_shadow_response(message)

    return None


def should_handle(message: discord.Message) -> bool:
    content = message.content.strip()
    parts = content.split(maxsplit=1)
    command = parts[0].lower() if parts else ""
    return (
        content.startswith(COMMAND_PREFIX)
        or command in {f"{COMMAND_PREFIX}arise", f"{COMMAND_PREFIX}cease"}
        or shadow.is_session_active(message.channel.id)
    )


async def process_commands(ctx: ShadowContext):
    import commands
    parts = ctx.content.split(maxsplit=1)
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
