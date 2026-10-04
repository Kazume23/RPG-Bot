from functools import lru_cache

import tiktoken


@lru_cache(maxsize=1)
def _encoding():
    # Ładowanie jest opóźnione, aby brak cache tiktoken nie blokował startu bota.
    return tiktoken.get_encoding("cl100k_base")


def count_tokens(text):
    if isinstance(text, list):
        text = flatten_history_to_text(text)
    return len(_encoding().encode(text))


def flatten_history_to_text(history):
    return "\n".join([f"{m['role']}: {m.get('content', '[BRAK CONTENTU]')}" for m in history])
