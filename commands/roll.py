import random


async def roll_command(message):
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
