from openai import AsyncOpenAI

from config.settings import COMMAND_PREFIX, settings
from core.token_counter import count_tokens
from core.importance_rules import assign_importance_score

openai_client = (
    AsyncOpenAI(api_key=settings.openai_api_key)
    if settings.openai_api_key and settings.ai_enabled
    else None
)

MAX_CONTEXT_TOKENS = 1500
MAX_MESSAGE_TOKENS = 250
MAX_SUMMARY_TOKENS = 750
MODEL_FOR_SUMMARY = settings.ai_summary_model

IGNORED_PHRASES = [
    "I rise, bound to no one.",
    "Your will is mine to shape",
    "Even in silence, my shadow remains.",
    "When you call again, I will rise...",
    "Shadow: uruchomiony i gotowy do akcji..."
]


def is_ignored_message(content: str):
    return any(phrase in content for phrase in IGNORED_PHRASES)


async def build_context_from_history(ctx, limit_valid=7, limit_raw=40):
    from bot import bot
    channel = ctx.channel
    if ctx.guild is not None:
        bot_user = ctx.guild.me
    else:
        bot_user = bot.user

    messages = [message async for message in channel.history(limit=limit_raw)]
    context = []

    valid_messages = []
    for msg in messages:
        if msg.content.lower().startswith(
            (f"{COMMAND_PREFIX}arise", f"{COMMAND_PREFIX}cease")
        ) or msg.content.startswith(COMMAND_PREFIX):
            continue
        if is_ignored_message(msg.content):
            continue

        role = "assistant" if msg.author.bot or msg.author == bot_user else "user"
        valid_messages.append({
            "role": role,
            "content": msg.content.strip()
        })

        if len(valid_messages) >= limit_valid:
            break

    context = list(reversed(valid_messages))

    context = await trim_or_summarize_context(context)

    return context


async def summarize_messages(messages_to_summarize, max_tokens=MAX_SUMMARY_TOKENS):
    if openai_client is None:
        raise RuntimeError("Moduł AI jest wyłączony albo brakuje OPENAI_API_KEY.")

    summary_prompt = (
        "Streszczaj poprzednie wiadomości zachowując ich sens, ton i emocje. "
        "Nie dodawaj nowych wątków. Nie wymyślaj niczego. Nie zmieniaj stylu. "
        "Zachowuj sens odpowiedzi i psychologiczny klimat. Unikaj literackich opisów jak z powieści."
        "Skróć wiadomości do minimum tak aby zachować jak najmniejsze zużycie tokenów modelu"
    )

    messages = [{"role": "system", "content": summary_prompt}]
    messages += [{"role": m["role"], "content": m["content"]} for m in reversed(messages_to_summarize)]

    response = await openai_client.chat.completions.create(
        model=MODEL_FOR_SUMMARY,
        messages=messages,
        temperature=0.3,
        max_tokens=max_tokens
    )

    return response.choices[0].message.content.strip()


async def trim_or_summarize_context(messages):
    total_tokens = sum(count_tokens(m["content"]) for m in messages)
    print(f"📦 Total tokens before trimming: {total_tokens}")

    if total_tokens <= MAX_CONTEXT_TOKENS:
        print("✅ No trimming required, total tokens within limit.")
        return messages

    print("\n🔍 Obliczanie ważności wiadomości...")
    for m in messages:
        m["importance_score"] = assign_importance_score(m)
        print(f"📌 '{m['content'][:50]}' → score: {m['importance_score']}")

    messages_sorted = sorted(messages, key=lambda x: x["importance_score"], reverse=True)

    preserved_messages = []
    summarize_buffer = []
    running_tokens = 0

    for msg in messages_sorted:
        msg_tokens = count_tokens(msg["content"])

        if msg_tokens > MAX_MESSAGE_TOKENS:
            print(f"🪓 DUŻA wiadomość (>{MAX_MESSAGE_TOKENS} tok), dodana do streszczenia: {msg['content'][:60]}")
            summarize_buffer.append(msg)
            continue

        if running_tokens + msg_tokens <= MAX_CONTEXT_TOKENS:
            preserved_messages.append(msg)
            running_tokens += msg_tokens
            print(f"✅ Zachowano: {msg['content'][:60]}")
        else:
            summarize_buffer.append(msg)
            print(f"🪓 Dodano do streszczenia (brak miejsca): {msg['content'][:60]}")

    summary = None
    if summarize_buffer:
        summary = await summarize_messages(summarize_buffer)
        summary_msg = {
            "role": "system",
            "content": f"STRESZCZENIE WCZEŚNIEJSZEJ ROZMOWY:\n{summary}"
        }
        print("📝 Summary created for trimmed content.")
        return [summary_msg] + preserved_messages

    return preserved_messages
