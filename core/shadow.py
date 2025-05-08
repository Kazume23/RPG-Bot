import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

from core.personalities import load_personalities
from core.token_counter import count_tokens
from core.context_builder import build_context_from_history

# Ustawienia loggera
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s:%(message)s',
    handlers=[
        logging.FileHandler("shadow.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

session_active = False
total_tokens_used = 0
active_personality = None
TOKEN_LIMIT = 3000

PERSONALITIES = load_personalities()

active_sessions = {}


def toggle_session(state: str, personality: str = "none", channel_id=None):
    global session_active, total_tokens_used, active_personality

    personality = personality.lower()

    if state == "ARISE":
        if personality not in PERSONALITIES:
            active_personality = "none"
            logger.warning("Nieznana osobowość '%s'. Ustawiono 'none'", personality)
        else:
            active_personality = personality
            logger.info("Aktywowano osobowość: %s", active_personality)

        active_sessions[channel_id] = personality
        session_active = True
        total_tokens_used = 0
        logger.info("[ARISE] Sesja rozpoczęta.")
        return "I rise, bound to no one. Your will is mine to shape, your enemies, mine to destroy."

    elif state == "CEASE":
        if channel_id in active_sessions:
            del active_sessions[channel_id]
        session_active = False
        total_tokens_used = 0
        active_personality = None
        logger.info("[CEASE] Sesja zakończona.")
        return "Even in silence, my shadow remains. When you call again, I will rise..."


def is_session_active(channel_id):
    return channel_id in active_sessions


def build_personality_prompts(personality_data):
    prompts = []

    if "system" in personality_data:
        prompts.append({"role": "system", "content": personality_data["system"]})

    if "memory" in personality_data and personality_data["memory"]:
        memory_text = "\n".join(personality_data["memory"])
        prompts.append({"role": "system", "content": f"Wspomnienia i zasady:\n{memory_text}"})

    if "style" in personality_data:
        prompts.append({"role": "system", "content": f"Pisz stylem {personality_data['style']}"})

    prompts.append({"role": "system",
                    "content": "Odpowiadaj zwięźle na wiadomości i nie przedłużaj ich niepotrzebnie. Historię mają być rozbudowane ale odpowiedzi zwięzłe na temat które go wyczerpią. Możesz przeklinać"})

    return prompts


async def get_shadow_response(ctx):
    global total_tokens_used

    if not session_active:
        logger.info("Wiadomość zignorowana – sesja nieaktywna.")
        return None

    if total_tokens_used >= TOKEN_LIMIT:
        logger.warning("Przekroczono limit tokenów (%d)", TOKEN_LIMIT)
        return "Limit tokenów sesji został osiągnięty. CEASE, by zresetować."

    try:
        history = await build_context_from_history(ctx)
        logger.info("Zbudowano historię konwersacji (%d wpisów, %d tokenów)", len(history), count_tokens(history))
        # print("Historia przed zapytaniem:")
        # for message in history:
        #     print(f"Rola: {message['role']}, Treść: {message['content']}")

        if active_personality != "none":
            personality_data = PERSONALITIES.get(active_personality, {})
            personality_prompts = build_personality_prompts(personality_data)
            history = personality_prompts + history
            logger.info("Dodano systemową osobowość: %s", active_personality)

        # Trim historii, jeśli za długa
        max_context_tokens = TOKEN_LIMIT - 500
        while count_tokens(history) > max_context_tokens:
            if len(history) > 1:
                history.pop(1)
            else:
                break
        logger.debug("Historia przycięta do limitu tokenów (%d)", count_tokens(history))

        # Zapytanie do OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-2024-05-13",
            messages=history,
            max_tokens=500,
        )

        output = response.choices[0].message.content
        used_tokens = response.usage.total_tokens
        total_tokens_used += used_tokens

        logger.info("Odpowiedź od OpenAI (%d tokenów). Razem użyto: %d", used_tokens, total_tokens_used)

        return output

    except Exception as e:
        logger.exception("Błąd podczas kontaktu z OpenAI: %s", str(e))
        return f"Błąd podczas kontaktu z cieniem: {str(e)}"


async def process_commands(p_message, ctx):
    if p_message.startswith("ARISE"):
        parts = p_message.split()
        if len(parts) == 2:
            return toggle_session("ARISE", parts[1], ctx.channel.id)
        elif len(parts) == 1:
            return toggle_session("ARISE", "none", ctx.channel.id)
        else:
            return "Użycie: ARISE <osobowość>. Dostępne: shadow, pijak, bełcho"

    if p_message.startswith("CEASE"):
        return toggle_session("CEASE", channel_id=ctx.channel.id)

    return None
