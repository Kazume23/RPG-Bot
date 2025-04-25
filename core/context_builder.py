from core.token_counter import count_tokens

MAX_CONTEXT_TOKENS = 3500


async def build_context_from_history(channel, bot_user, limit=15):
    messages = [message async for message in channel.history(limit=limit)]
    context = []

    for msg in reversed(messages):
        if msg.author.bot or msg.author == bot_user:
            if any(msg.content.upper().startswith(cmd) for cmd in ["ARISE", "CEASE", ">HELP"]):
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

    return context

