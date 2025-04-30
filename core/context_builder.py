from core.token_counter import count_tokens
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MAX_CONTEXT_TOKENS = 200
SUMMARIZE_AT = 500
MAX_MESSAGE_TOKENS = 100  # Limit długości pojedynczej wiadomości do streszczenia

IGNORED_PHRASES = [
    "I rise, bound to no one.",
    "Your will is mine to shape",
    "Even in silence, my shadow remains.",
    "When you call again, I will rise..."
]


def is_ignored_message(content: str):
    return any(phrase in content for phrase in IGNORED_PHRASES)


async def build_context_from_history(channel, bot_user, limit=15):
    messages = [message async for message in channel.history(limit=limit)]
    context = []

    for msg in reversed(messages):
        if msg.content.upper().startswith(("ARISE", "CEASE")) or msg.content.startswith(">"):
            continue
        if is_ignored_message(msg.content):
            continue

        role = "assistant" if msg.author.bot or msg.author == bot_user else "user"
        context.append({"role": role, "content": msg.content})

    context = await trim_or_summarize_context(context)
    print("\n========== KONTEKST UŻYTY W ZAPYTANIU ==========")
    for i, m in enumerate(context):
        print(f"[{i}] ({m['role']}): {m['content'][:200]}")
    print("===============================================\n")
    return context


async def summarize_messages(messages, max_tokens=300):
    summary_prompt = (
        "Streszczaj poprzednie wiadomości zachowując ich sens, ton i emocje. "
        "Nie dodawaj nowych wątków. Nie wymyślaj niczego. Nie zmieniaj stylu. "
        "Jeśli rozmowa była intensywna, poważna lub wulgarna – streszczaj to w tym samym stylu. "
        "Zachowuj sens odpowiedzi i psychologiczny klimat. Unikaj literackich opisów jak z powieści."
    )

    raw_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
    print("\n🧠 SUROWY TEKST DO STRESZCZENIA:\n" + raw_text[:1000] + "\n")

    response = await openai_client.chat.completions.create(
        model="gpt-4o-2024-05-13",
        messages=[
            {"role": "system", "content": summary_prompt},
            {"role": "user", "content": raw_text}
        ],
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

    preserved_messages = []
    summarize_buffer = []
    running_tokens = 0

    for msg in reversed(messages):
        msg_tokens = count_tokens(msg["content"])

        if msg_tokens > MAX_MESSAGE_TOKENS:
            summarize_buffer.append(msg)
            continue

        if running_tokens + msg_tokens <= MAX_CONTEXT_TOKENS:
            preserved_messages.insert(0, msg)
            running_tokens += msg_tokens
        else:
            summarize_buffer.append(msg)

    summary = None
    if summarize_buffer:
        summary = await summarize_messages(list(reversed(summarize_buffer)))
        summary_msg = {"role": "system", "content": f"STRESZCZENIE WCZEŚNIEJSZEJ ROZMOWY:\n{summary}"}
        print("📝 Summary created for trimmed content.")
        return [summary_msg] + preserved_messages

    return preserved_messages
