import tiktoken

encoding = tiktoken.encoding_for_model("gpt-4")


def count_tokens(text):
    if isinstance(text, list):
        text = flatten_history_to_text(text)
    return len(encoding.encode(text))


def flatten_history_to_text(history):
    return "\n".join([f"{m['role']}: {m.get('content', '[BRAK CONTENTU]')}" for m in history])
