from umiejki import skills, abilities, ochlapus
import commands


def has_admin_permissions(ctx):
    return ctx.author.guild_permissions.administrator


async def get_response(message: str, ctx):
    p_message = message.lower()
    prefix = '>'

    if not p_message.startswith(prefix):
        return None

    if p_message.startswith(f'{prefix}dm'):
        return await commands.dm_command(ctx, message)

    if p_message.startswith(f'{prefix}purge'):
        return await commands.purge_command(ctx, message)

    if p_message == f'{prefix}hello':
        return await commands.hello_command()

    if p_message.startswith(f'{prefix}ochlapus'):
        return await commands.ochlapus_command(message)

    if p_message.startswith(f'{prefix}u'):
        return await commands.umieki_command(message)

    if p_message.startswith(f'{prefix}z'):
        return await commands.zdolnosci_command(message)

    if p_message.startswith(f'{prefix}roll'):
        return await commands.roll_command(message)

    if p_message.startswith(f'{prefix}klnij'):
        return await commands.klnij_command()

    if p_message.startswith(f'{prefix}help'):
        return await commands.help_command()

    if p_message.startswith(f'{prefix}wy' or f'{prefix}wydarzenia'):
        return await commands.wydarzenia_command(message, ctx)

    if p_message.startswith(f'{prefix}not' or f'{prefix}notatki'):
        return await commands.notatka_command(message, ctx)

    if p_message.startswith(f'{prefix}npc'):
        return await commands.npc_command(message, ctx)

    return "Naucz się w końcu tych komend KURWAAAȀ̷̢̺͚̣̮͉̬͔̺̎̍̃̾̿̽̿͐͑͆͂ͅU̵̧̙͍̹͂̈́͑̉͑̍̏̇̑̾́̾̕͘͜͠R̵͈̥̻͍̫̈́̕ͅẀ̶̡͈͉͚̌Ą̶̛̹̊̒̀̇̔̒̅̅͆A̴̦̰̯̯͎̝͒̎̅̃̿̌͂Ą̸̡̛̭͉̼͙̻̰̤̺̪͎̲͓͆̏̔̏̈́͂̂̒̋̾̐̍͜͝Å̷̪͓͊͝A̶͙̭̮̻͇͖͎̫̥͒̐̇̈̇̈̏̾͘͝͝Ḁ̷̖̦̈͒͋̾̉͑̃̑̿̕̕͝Ǎ̶̖̐͗̉͗̽͒͝A̵̢͔̒̉͆Ã̶̡̡̩͖̦̪̥̈́́̊̽͒̀̕͠ͅA̴̛̛̝̞̎̓͛͐̉̍͗̏̀͗̑͝Ą̸̧̜̫͉̟̹̭̰̹̯̠͐͆͗̇̇̿͆͗̃͗͝A̴͕͓̩͖̣̎̃̏̿͐̋́̋͠A̷̢̭̙͓̤̞͈̖̯̭̋ "
