import random


def roll_logic(expr: str) -> str:
    parts = expr.split()
    if len(parts) != 1 or 'd' not in parts[0]:
        return "Ty chuju. Pisz jak człowiek np: 5d6"

    try:
        if parts[0].startswith('d'):
            numberDice = 1
            numberSide = int(parts[0][1:])
        else:
            numberDice, numberSide = map(int, parts[0].split('d'))

        if numberDice > 50:
            return "No chyba cię coś pojebało"

        rolls = [random.randint(1, numberSide) for _ in range(numberDice)]
        total = sum(rolls)
        return f"Wyniki rzutów: {', '.join(map(str, rolls))}\n**Suma**: {total}"
    except ValueError:
        return "Ty chuju. Pisz jak człowiek np: 5d6"
