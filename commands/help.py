from config.settings import COMMAND_PREFIX


async def help_command():
    p = COMMAND_PREFIX
    return f"""**Komendy:**
            `{p}roll 2d6` — rzut kośćmi
            `{p}ukryty 1d100` — wynik rzutu wysłany do MG
            `{p}u [nazwa]` — opis umiejętności
            `{p}z [nazwa]` — opis zdolności
            `{p}ochlapus <Odp>` — test mocnej głowy
            `{p}klnij` — krasnoludzkie przekleństwo
            `{p}class [nazwa]` — lista lub opis profesji
            `{p}npc <rasa> <m/f> <klasa>` — generator NPC (MG)
            `{p}notatki <dodaj/usun/zmien/daj>` — notatki MG
            `{p}wydarzenia <dodaj/usun/zmien/daj>` — wydarzenia MG
            `{p}sesja <kanał>` — ankieta terminu sesji (MG)
            `{p}dm <kanał> <tekst>` — wiadomość na wskazany kanał (MG)
            `{p}purge <1-100>` — usuwanie wiadomości (MG)"""
