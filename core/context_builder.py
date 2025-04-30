from core.token_counter import count_tokens
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MAX_CONTEXT_TOKENS = 3500
SUMMARIZE_AT = 500


async def build_context_from_history(channel, bot_user, limit=15):
    messages = [message async for message in channel.history(limit=limit)]
    context = []

    for msg in reversed(messages):
        if msg.author.bot or msg.author == bot_user:
            if msg.content.upper().startswith(("ARISE", "CEASE")) or msg.content.startswith(">"):
                continue
            context.append({
                "role": "assistant",
                "content": msg.content
            })
        elif msg.author != bot_user:
            context.append({
                "role": "user",
                "content": msg.content
            })
    context = await trim_or_summarize_context(context)
    return context


async def summarize_messages(messages, max_tokens=300):
    summary_prompt = "Streszczaj rozmowę zachowując sens, emocje, kluczowe informacje i kontekst psychologiczny."

    raw_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

    response = await openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
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

    if total_tokens <= MAX_CONTEXT_TOKENS:
        return messages

    trimmed_messages = []
    preserved_messages = []

    running_tokens = 0
    for msg in reversed(messages):
        msg_tokens = count_tokens(msg["content"])
        if running_tokens + msg_tokens > SUMMARIZE_AT:
            trimmed_messages.insert(0, msg)
        else:
            preserved_messages.insert(0, msg)
            running_tokens += msg_tokens

    if not trimmed_messages:
        return preserved_messages

    summary = await summarize_messages(trimmed_messages)
    summary_message = {
        "role": "system",
        "content": f"STRESZCZENIE WCZEŚNIEJSZEJ ROZMOWY:\n{summary}"
    }

    return [summary_message] + preserved_messages
