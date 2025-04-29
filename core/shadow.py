import os
from openai import OpenAI
from dotenv import load_dotenv

from core.personalities import load_personalities
from core.token_counter import count_tokens
from core.context_builder import build_context_from_history

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

session_active = False
total_tokens_used = 0
active_personality = None
TOKEN_LIMIT = 3000

PERSONALITIES = load_personalities()


def toggle_session(state: str, personality: str = "none"):
    global session_active, total_tokens_used, active_personality

    personality = personality.lower()

    if state == "ARISE":
        if personality not in PERSONALITIES:
            active_personality = "none"
            session_active = True
            total_tokens_used = 0
            return f"I rise, bound to no one. Your will is mine to shape, your enemies, mine to destroy."

        active_personality = personality
        session_active = True
        total_tokens_used = 0

        print(f"[ARISE] Aktywna osobowość: {active_personality}")

        return f"I rise, bound to no one. Your will is mine to shape, your enemies, mine to destroy."

    elif state == "CEASE":
        session_active = False
        total_tokens_used = 0
        active_personality = None
        print("[CEASE] Sesja zakończona.")
        return "Even in silence, my shadow remains. When you call again, I will rise..."


async def get_shadow_response(message: str, ctx):
    global total_tokens_used

    if total_tokens_used >= TOKEN_LIMIT:
        return "Limit tokenów sesji został osiągnięty. CEASE, by zresetować."

    try:
        history = await build_context_from_history(ctx.channel, ctx.guild.me)

        if active_personality != "none":
            history.insert(0, {
                "role": "system",
                "content": PERSONALITIES[active_personality]["system"]
            })

        print("Historia przed zapytaniem:")
        for message in history:
            print(f"Rola: {message['role']}, Treść: {message['content']}")

        response = client.chat.completions.create(
            model="gpt-4o-2024-05-13",
            messages=history,
            max_tokens=500,
        )
        output = response.choices[0].message.content
        total_tokens_used += response.usage.total_tokens
        return output

    except Exception as e:
        return f"Błąd podczas kontaktu z cieniem: {str(e)}"


async def process_commands(p_message, ctx):
    if p_message.startswith("ARISE"):
        parts = p_message.split()
        if len(parts) == 2:
            return toggle_session("ARISE", parts[1])
        elif len(parts) == 1:
            return toggle_session("ARISE", "none")
        else:
            return "Użycie: ARISE <osobowość>. Dostępne: shadow, pijak, bełcho"
