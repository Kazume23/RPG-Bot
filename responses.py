import random
import discord
from characters import display_character_stats, load_characters
from umiejki import skills, abilities
import wyzwiska


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

    if p_message.startswith(f'{prefix}dm'):  # DM
        if not has_admin_permissions(ctx):
            return "Spierdalaj. Nie masz nade mną władzy śmiertelniku"

        parts = message.split(maxsplit=2)
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

        if user_value >= random_value:
            responses = [
                "**Pół kufla to nie picie**\n„Nawet się nie rozgrzałem!” – Twój organizm przyjął alkohol jak wodę. Nic się nie dzieje… jeszcze.",
                "**Bełkot pijaka**\n„No… i… tego… ja tylko chciałem powiedzieć, że… że… HIC!” – Twoja mowa staje się niezrozumiała. Wszyscy traktują cię jak debila (-10 do testów Ogłady).",
                "**Łapy jak wory z piwem**\n„Ej… czemu ja mam cztery ręce?” – Masz problem z utrzymaniem równowagi. Każda akcja wymagająca precyzji dostaje -20 do testu.",
                "**Przewrót krasnoludzki**\n„A ja wam pokażę… O KURWA!” – Próbujesz wykonać popisowy taniec, ale lądujesz na plecach. Rzut na Zręczność - przy nieudanym dostajesz 1d3 obrażeń od upadku i hańby.",
                "**Mocny oddech**\n„Kto tu umarł?” – Twój smród wygania szczury i odstrasza ludzi. Wszyscy w promieniu 2 metrów mają -10 do testów Siły Woli oraz Wytrzymałości przeciwko mdłościom.",
                "**Widzę dwa kufle**\n„A który to mój?” – Masz podwójne widzenie. Trafienie wroga bronią dystansową jest w chuj utrudnione -30 do Umiejętności Strzeleckich",
                "**Nocne zwierzę**\n„Ja nie chcę spać, ja chcę pić!” – Nie możesz zasnąć przez całą noc. Rano masz -10 do wszystkich testów dopóki nie odeśpisz nocy.",
                "**Gdzie ja jestem?**\n„Ej… czy ja nie byłem w karczmie?” – Znikasz niepostrzeżenie. Budzisz się w przypadkowym miejscu. Może to środek ulicy, może więzienie, może łóżko nieznanej osoby.",
                "**Zaprawiony w boju**\n„Więcej nie piję… no chyba że jedno na drogę!” – Masz odporność na kaca, ale twój organizm wymaga podtrzymania efektu. Jeśli nie wypijesz alkoholu w ciągu godziny, masz -10 do Wszystkich testów.",
                "**Śpiew duszy**\n„Ej, znacie tę piosenkę?!” – Zaczynasz głośno śpiewać, nawet jeśli nikt tego nie chce. Musisz wykonać test Ogłady – jeśli oblejesz, miejscowi zaczynają się irytować.",
                "**Gorzałka Prawdy**\n„Ej, a wiecie, że ja tak naprawdę was wszystkich Kocham?” – Nie możesz powstrzymać się przed mówieniem na głos swoich myśli.",
                "**Kwaśny Bek**\nTwoje wnętrzności buntują się przeciwko alkoholowi – każdy, kto stoi obok ciebie, musi wykonać test Siły Woli, by nie odwrócić się z obrzydzeniem.",
                "**Śmiercionośny Łyk**\nCoś było nie tak z tą gorzałką... - Tracisz przytomność na 1d6 godzin.",
                "**Uderzenie Mocy**\nNagły przypływ energii po gorzale! Twoja pierwsza tura w walce jest z premią +10 do testów, ale potem masz -20 do kolejnych testów.",
                "**Szlachecki Wyrzyg**\nNie dałeś rady – treść twojego żołądka ląduje na ziemi (lub kimś innym). Wszyscy w promieniu 1 metra wykonują test Zręczności, by uniknąć zachlapania.",
                "**Karmazynowy Mściciel**\nZaczynasz odgrywać jakiegoś pojeba w pelerynie. Próbujesz uratować (porwać) najbliższą kobietę z rąk podłych bandytów",
                "**Walka z Cieniem**\nMasz wrażenie, że ktoś cię zaczepia... ale to tylko twój własny cień! Wykonujesz atak za siebie uderzając pierwszą napotkaną rzecz lub twarz.",
                "**Najlepszy Przyjaciel Owadów**\nCoś w twoim zapachu przyciąga roje much i komarów – od teraz do końca sesji masz karę -10 do testów Ukrywania się. Jebiesz",
                "**Filozof Po Pijaku**\nNagle stajesz się mędrcem i zaczynasz debatę na temat sensu życia, ku niezadowoleniu wszystkich w pobliżu.",
                "**Wielki Mówca**\nZaczynasz przemawiać jak charyzmatyczny przywódca, ale każde twoje słowo jest bełkotem. Testy Przekonywania masz z utrudnieniem -20",
                "**Upadek Legendy**\nPróbujesz efektownego popisu akrobacji, ale się wypierdalasz. Rzut na Zręczność - przy nieudanym teście otrzymujesz 1k3 obrażenia od uderzenia o twardą powierzchnię.",
                "**Piekielne Gazy Nurgla**\nCoś w alkoholu ci nie służyło... Każdy w promieniu 3 metrów musi wykonać test Wytrzymałości, by nie zwymiotować.",
                "**Szczurzy Instynkt**\nMasz przeczucie, że ktoś cię śledzi! Paranoicznie oglądasz się wokół siebie wypatrując podglądacza.",
                "**Mistrz Maskarady**\nMasz wrażenie, że jesteś najlepszym aktorem w Imperium. Wykonujesz losową scenę z dramatu, choć nikt nie prosił.",
                "**Karczemne Szepty**\nMoże zaatakujemy... albo się napijemy? - Zaczynasz tworzyć spisek nad rozpętaniem karczemnej bójki. Rzuć na SW, przy nieudanym teście zaczynasz karczemną bijatykę na pięści i mięso. (Twoi sojusznicy mogą cię powstrzymać)",
                "**Krasnolud nigdy nie przegrywa! **\n„Jeszcze jedno! Jeszcze jedno!” – Wchodzisz w tryb uporu. Musisz wykonać test Siły Woli – jeśli nie zdasz, pijesz dalej, niezależnie od konsekwencji.",
                "**Beczkowy Wojownik **\n„Pff… kto powiedział, że beczka to nie zbroja?” – Zakładasz na siebie elementy karczmy (beczkę, obrus, krzesło). Przy udanej czynności masz +2 do Pancerza, ale wszystkie testy Zręczności są utrudnione o -30. ",
                "**Zaklinacz Stołów**\n„To nie ja przewróciłem ten stół… on sam chciał!” – Stół przy którym pijesz magicznie wypierdala się do góry nogami zrzucając wszystko co na nim było. Rzuć na Ogładę żeby przekonać wszystkich pijanych że ty tego nie zrobiłeś. (Sam go wypierdoliłeś)",
                "**Cierpliwość Sigmara**\n„A wiesz, kto jeszcze miał brodę?! Twoja Matka!” – Zaczynasz opowiadać przypadkowym osobą niezliczone żarty o urodzie ich rodzicielek ",
                "**Thingrim... Co dodałeś do mojego wywaru?**\n„No i co, że śmierdzi? Alkohol to alkohol!” – Wypijasz coś, co nie do końca było tylko alkoholem. Rzuć na WT, jeśli oblejesz zaczynasz dostawać losowych halucynacji",
                "**Złodziej kufli**\n„Ej… czemu mam trzy kufle w rękach?” – Nieświadomy własnych czynów kradniesz alkohol innym biesiadnikom. Jeśli ktoś się zorientuje, może skończyć się bójką.",
                "**Karczemne Szachy**\n„Dobra… ustawiamy stoły w rządku! Bierzemy krzesła i… start!” – Namawiasz wszystkich do udziału w wyimaginowanej grze, która nie ma żadnych zasad. Rzuć na Przekonywanie – jeśli zdasz, masz swoją ligę głupców.",
                "**Krasnoludzki szantaż**\n„A pamiętasz, jak wtedy… oj, nie pamiętasz? To ja ci kurwa przypomnę!” – Wydobywasz siłą od losowej osoby kompromitujący fakt, który może być prawdziwy albo totalnie zmyślony. Jeśli się przeciwstawi to stajesz się agresywniejszy",
                "**Dziwne Przymierze**\n„TY! Tak, TY! Jesteś teraz moim najlepszym przyjacielem!” – Wybierasz losową osobę i traktujesz ją jak brata broni. Jeśli to wróg, przez 1k10 minut ignorujesz konflikt, próbując się z nim zaprzyjaźnić. ",
                "**Pusty Kufel, Puste Serce **\n„KTO MI KURWA WYPIŁ PIWO!?” – Ogarnia cię dzika furia na myśl, że ktoś ci ukradł alkohol. Wybierasz losową osobę i zaczynasz ją oskarżać, żądając rekompensaty.",
                "**Duch Przodków**\n„Dziadku, czy to ty!?” – Wydaje ci się, że widzisz ducha dawno zmarłego krewnego. Rozpoczynasz z nim długą, pełną wzruszeń i łez rozmowę… choć w rzeczywistości mówisz do beczki/piwnicy/końskiego zadka. ",
                "**Więcej Niż Towarzyski **\n„Ej… ty jesteś moim najlepszym przyjacielem, wiesz?” – Przygarniasz do serca pierwszą napotkaną osobę i traktujesz ją jak brata/bratową. Nie odchodzisz od niej na krok, nawet jeśli to absolutnie nie na miejscu. ",
                "**Krasnoludzki Taniec Wojenny **\n„JAK NA WESELU GRUMNIRA!” – Nagle ogarnia cię duch zabawy. Wykonujesz szalony taniec, który kończy się spektakularnym upadkiem. Test Zręczności – przy porażce leżysz na glebie i otrzymujesz 1k3 obrażenia.",
                "**Dłoń Karla Franza **\n„Błogosławieństwo Imperatora!” – Masz nagłe poczucie misji i zaczynasz błogosławić wszystkich wokół. Niestety, zamiast boskiej łaski, twój dotyk przesiąknięty jest alkoholem, smrodem i resztkami rzygów. Ludzie zaczynają się od ciebie odsuwać.",
                "**Przeklęty Łyk **\n„Coś mi się nie podoba w tym smaku…” – Alkohol miał podejrzany posmak. Rzuć k6: 1-3 – nie dzieje się nic; 4-5 – czujesz mdłości (-10 do testów Wytrzymałości przez godzinę); 6 – rzyg.",
                "**Bratnia Dusza w Kuflu **\n„Mów do mnie, kuflu…” – Znajdujesz w swoim kuflu doskonałego słuchacza. Prowadzisz z nim poważną rozmowę, zdradzając mu wszystkie swoje sekrety… na głos.",
                "**Niezniszczalny Bohater **\n„Nic mi nie jest, zobacz!” – Czujesz się absolutnie odporny na ból. Wykonujesz popisowy numer (np. rozbijasz butelkę na głowie), ale rzeczywistość okazuje się brutalna. Test Wytrzymałości – przy porażce dostajesz 1k3 obrażenia. ",
                "**Sztuka Krasnoludzkiej Oratorii **\n„Słuchajcie mnie, bo zaraz powiem coś mądrego!” – Masz nagłą potrzebę wygłoszenia krasomówczego przemówienia. Niezależnie od treści, publiczność jest podzielona: 50% uznaje cię za geniusza, 50% chce cię uciszyć. ",
                "**Przepowiednia Bełta **\n„Widzę… Widzę przyszłość!” – Bełkoczesz coś niezrozumiałego, ale wypada to tak przekonująco, że ktoś zaczyna w to wierzyć. Może to zwykły chłop, może miejscowy szlachcic… Może to mieć poważne konsekwencje. ",
                "**Efekt Krasnoludzkiej Syreny **\n„AAAAAaaaAAAAaaaAaa…” – Budzi się w tobie wewnętrzny bard. Bez względu na jakość, twój śpiew jest OGROMNYM problemem dla wszystkich w pobliżu. Test Ogłady – jeśli oblejesz, ktoś chce cię zdzielić kuflem po łbie. ",
                "**Urodzony Alchemik **\n„A co się stanie, jak to wymieszam…?” – Postanawiasz dodać do alkoholu losowy składnik (np. solonego śledzia, węgiel, proch strzelniczy). Efekty są absolutnie nieprzewidywalne.",
                "**Miłość od Pierwszego Łyka **\n„Czekaj… czekaj… KTO TO JEST!?” – Nagle wydaje ci się, że spotkałeś miłość swojego życia. Może to być piękna karczmarka, może to być koń. Nieważne – jesteś gotów walczyć o nią na śmierć i życie.",
                "**Zapomniane Obietnice **\n„Przysięgam na swój brodaty honor!” – Obiecujesz coś ważnego osobie, której nawet nie pamiętasz. Może to być udział w misji, spłata długu, a może ślub… Rano się okaże.",
                "**Wielki Krasnoludzki Pojedynek **\n„Wiesz co… chyba cię nie lubię!” – Znajdujesz losowego rywala i rzucasz mu wyzwanie. Może to być wyścig na czworaka, może to być pojedynek na plucie, a może regularna bijatyka.",
                "**Gdzie Jest Mój Kufel!? **\n„KTOŚ GO UKRADŁ!” – Przysięgasz na krasnoludzki honor, że ktoś zwinął twój kufel (choć sam go zgubiłeś). Dopóki go nie odzyskasz, traktujesz wszystkich wokół jak podejrzanych.",
                "**Ryk Grungniego **\n„RAAAAH! TO DLA CHWAŁY PRZODKÓW!” – Czujesz nagły przypływ siły i bojowego ducha. Wydajesz z siebie gromki ryk, który może: \n 1-3 – Przerazić pobliskie zwierzęta i dzieci. \n 4-5 – Sprawić, że wszyscy spojrzą na ciebie z szacunkiem (lub współczuciem). \n 6 – Spowodować natychmiastowe wyproszenie z karczmy.",
                "**Święta Woda **\n„To nie jest zwykły alkohol… TO ELITARNY BROWAR IMPERIUM!” – Uznałeś, że twój trunek to boski napój. Każesz wszystkim wokół go szanować, a każdy kto odmówi, budzi twój gniew.",
                "**Tajemnica Kufla **\n„Było pełne, teraz jest puste… Jak to możliwe!?” – Nie możesz zrozumieć, jak alkohol znika z twojego kufla. Przez następne 10 minut obserwujesz go podejrzliwie, nieświadomie odmawiając kolejnych łyków. ",
                "**Głód Krasnoluda **\n„POTRZEBUJĘ MIĘSA, TERAZ!” – Ogarnia cię nagła potrzeba konsumpcji ogromnych ilości jedzenia. Jeśli go nie dostaniesz w ciągu 5 minut, zaczynasz poważnie zastanawiać się nad zjedzeniem czegokolwiek… nawet własnego buta. ",
                "**Rzecz Krasnoluda **\n„Kto mi zabrał moją… moją… coś?” – Jesteś absolutnie pewien, że ktoś ukradł ci coś ważnego. Problem w tym, że nie pamiętasz, co to było. Nie spoczniesz, dopóki tego nie znajdziesz. ",
                "**Pijacki Poeta **\n„Czas na sonet o kuflu!” – Ogarnia cię nagła potrzeba recytowania poezji. Niestety, w twoim wykonaniu to głównie rymy typu „kufel – wór” i „bełt – śmierć”.",
                "**Magiczna Miedziakowa Moneta **\n„Jeśli rzucę monetą… to na pewno zdecyduję!” – Oddajesz wszystkie swoje ważne decyzje w ręce losu. Każda sytuacja, która wymaga decyzji, kończy się rzutem monetą – i trzymasz się wyniku niezależnie od konsekwencji.",
                "**Złota Rączka, Kurewski Problem **\n„Naprawię to, przyrzekam na moją brodę!” – Czujesz potrzebę naprawienia czegoś w pobliżu. Test Rzemiosła – sukces oznacza, że faktycznie to naprawiasz, porażka oznacza, że nieświadomie pogarszasz sytuację.",

            ]
            return f"🎲 Wylosowana wartość: **{random_value}** (twoja: {user_value})\n{random.choice(responses)}"
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

        return "Pisz jak człowiek, np. >kurwo albo >kurwo @user"

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
