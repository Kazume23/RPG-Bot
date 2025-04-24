from core.token_counter import count_tokens

MAX_CONTEXT_TOKENS = 3500

async def build_context_from_history(channel, bot_user, max_tokens=MAX_CONTEXT_TOKENS):
    messages = []
    total_tokens = 0

    async for msg in channel.history(limit=10):  # token limit
        if msg.author.bot:
            continue

        role = "assistant" if msg.author == bot_user else "user"
        token_count = count_tokens(msg.content)

        if total_tokens + token_count > max_tokens:
            break

        messages.insert(0, {"role": role, "content": msg.content})
        total_tokens += token_count

    return messages
