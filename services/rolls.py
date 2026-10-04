import random
import re


ROLL_PATTERN = re.compile(r"^(?:(\d+))?[dD](\d+)$")


def parse_roll(expr: str):
    match = ROLL_PATTERN.fullmatch(expr.strip())
    if not match:
        raise ValueError("oczekiwany format to NdM, np. 2d6 albo d100")

    number_dice = int(match.group(1) or 1)
    number_sides = int(match.group(2))

    if not 1 <= number_dice <= 50:
        raise ValueError("liczba kości musi mieścić się w zakresie 1–50")
    if not 2 <= number_sides <= 10000:
        raise ValueError("liczba ścian musi mieścić się w zakresie 2–10000")

    return number_dice, number_sides


def roll_logic(ctx, expr: str) -> str:
    try:
        number_dice, number_sides = parse_roll(expr)
        rolls = [random.randint(1, number_sides) for _ in range(number_dice)]
        total = sum(rolls)
        return f"Rzucił: {ctx.author.display_name}\nWyniki rzutów: {', '.join(map(str, rolls))}\n**Suma**: {total}"
    except (TypeError, ValueError) as exc:
        if str(exc) == "liczba kości musi mieścić się w zakresie 1–50":
            return "No chyba cię coś pojebało"
        return "Ty chuju. Pisz jak człowiek np: 5d6"
