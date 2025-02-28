import random
import discord
from characters import display_character_stats, load_characters
from umiejki import skills, abilities, ochlapus
import wyzwiska
import commands

ochlapus_copy = set(ochlapus)


def has_admin_permissions(ctx):
    return ctx.author.guild_permissions.administrator


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


async def get_response(message: str, ctx):
    p_message = message.lower()
    prefix = '>'

    if not p_message.startswith(prefix):
        return None

    if p_message.startswith(f'{prefix}dm'):
        return await commands.dm_command(ctx, message)

    if p_message.startswith(f'{prefix}sesja'):  # SESJA

        if not has_admin_permissions(ctx):
            return "Spierdalaj. Nie masz nade mną władzy śmiertelniku"

        channel_name = p_message[len(prefix) + len("sesja"):].strip()

        channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)

        if channel:
            await send_sesja_message(ctx, channel)
            return f"Sesja została zaplanowana na kanale #{channel_name}!"
        else:
            return "Nie udało się znaleźć kanału o podanej nazwie."

    if p_message.startswith(f'{prefix}purge'):  # PURGE
        if not has_admin_permissions(ctx):
            return "Spierdalaj. Nie masz uprawnień administratora do tej komendy."

        parts = message.split()
        if len(parts) == 2 and parts[1].isdigit():
            try:
                amount = int(parts[1])
                if amount > 100:
                    return "Nie możesz usunąć więcej niż 100 wiadomości naraz, debilu."
                await ctx.channel.purge(limit=amount + 1)
                return None
            except Exception as e:
                return f"Coś poszło nie tak: {e}"
        else:
            return "Pisz jak człowiek, np: >purge 20"

    if p_message == f'{prefix}hello':  # HELLO
        return 'Spierdalaj'

    if p_message.startswith(f'{prefix}ochlapus'):  # OCHLAPUS
        parts = message.split()
        if len(parts) != 2 or not parts[1].isdigit():
            return "Użyj poprawnej składni: `>ochlapus X`, gdzie X to liczba."

        user_value = int(parts[1])
        random_value = random.randint(1, 100)

        global ochlapus_copy
        if not ochlapus_copy:
            ochlapus_copy = set(ochlapus)

        effect = random.choice(list(ochlapus_copy))
        ochlapus_copy.remove(effect)

        if user_value >= random_value:
            return f"🎲 Wylosowana wartość: **{random_value}** (twoja: {user_value}) (Efekty: {len(ochlapus_copy)}) \n{effect}"
        else:
            return f"🎲 Wylosowana wartość: **{random_value}** (twoja: {user_value})\nTym razem udało ci się nie najebać"

    if p_message.startswith(f'{prefix}u'):  # UMIEJKI
        parts = message.split(maxsplit=1)
        if len(parts) < 2:
            return "Użyj poprawnej składni: >umiejki {nazwa_umiejętności}"

        skill_name = parts[1].lower()
        if skill_name in skills:
            return skills[skill_name]
        else:
            return "Naucz się kurwo szukać umiejek."

    if p_message.startswith(f'{prefix}z'):  # ZDOLNOSCI
        parts = message.split(maxsplit=1)
        if len(parts) < 2:
            return "Użyj poprawnej składni: >zdolnosci {nazwa_zdolności}"

        ability_name = parts[1].lower()
        if ability_name in abilities:
            return abilities[ability_name]
        else:
            return "Weź ty kurwa się naucz wpisywać dobrze te gówna."

    if p_message.startswith(f'{prefix}roll'):
        parts = message.split()
        if len(parts) == 2 and 'd' in parts[1]:
            try:
                if parts[1].startswith('d'):
                    numberDice = 1
                    numberSide = int(parts[1][1:])
                else:
                    numberDice, numberSide = map(int, parts[1].split('d'))

                if numberDice > 50:
                    return "No chyba cie cos pojebało"
                rolls = [random.randint(1, numberSide) for _ in range(numberDice)]
                total = sum(rolls)
                return f"Wyniki rzutów: {', '.join(map(str, rolls))}\n**Suma**: {total}"
            except ValueError:
                return "Ty chuju. Pisz jak człowiek np: 5d6"

    if p_message.startswith(f'{prefix}klnij'):  # KLNIJ
        parts = message.split()

        if len(parts) == 1:
            return wyzwiska.losuj_przeklenstwo()

        return "Pisz jak na jebanego krasnoluda przystało >klnij"

    if p_message.startswith(f'{prefix}help'):
        return """
        **Komendy:**
        
        1. **`>ochlapus {WT}`**  
           Na brodę Grungniego, jego młot i synów, dzisiaj wieczorem napierdolimy się jak przodkowie przykazali!
        
        2. **`>u {nazwa_umiejętności}`**  
           Sprawdź szczegóły na temat umiejętności swojej postaci. Podaj nazwę umiejętności, aby uzyskać opis i jak wpływa na twoje działania w grze.
        
        3. **`>z {nazwa_zdolności}`**  
           Dowiedz się więcej o zdolnościach swojej postaci. Podaj nazwę zdolności, by poznać szczegóły na temat jej działania w grze.
        
        4. **`>roll {ilość}d{strona}`**  
           Hazard! Wpisz np. `>roll 2d6`.
        
        \n5. **`>klnij`**     
    Popularne krasnoludzkie wyzwiska które pomogą wam zdobyć XP na sesji.
        """

    return "Naucz się w końcu tych komend KURWAAAȀ̷̢̺͚̣̮͉̬͔̺̎̍̃̾̿̽̿͐͑͆͂ͅU̵̧̙͍̹͂̈́͑̉͑̍̏̇̑̾́̾̕͘͜͠R̵͈̥̻͍̫̈́̕ͅẀ̶̡͈͉͚̌Ą̶̛̹̊̒̀̇̔̒̅̅͆A̴̦̰̯̯͎̝͒̎̅̃̿̌͂Ą̸̡̛̭͉̼͙̻̰̤̺̪͎̲͓͆̏̔̏̈́͂̂̒̋̾̐̍͜͝Å̷̪͓͊͝A̶͙̭̮̻͇͖͎̫̥͒̐̇̈̇̈̏̾͘͝͝Ḁ̷̖̦̈͒͋̾̉͑̃̑̿̕̕͝Ǎ̶̖̐͗̉͗̽͒͝A̵̢͔̒̉͆Ã̶̡̡̩͖̦̪̥̈́́̊̽͒̀̕͠ͅA̴̛̛̝̞̎̓͛͐̉̍͗̏̀͗̑͝Ą̸̧̜̫͉̟̹̭̰̹̯̠͐͆͗̇̇̿͆͗̃͗͝A̴͕͓̩͖̣̎̃̏̿͐̋́̋͠A̷̢̭̙͓̤̞͈̖̯̭̋ "
