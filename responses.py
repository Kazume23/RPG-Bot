import openai
import os
from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

session_active = False
total_tokens_used = 0
TOKEN_LIMIT = 3000


def toggle_session(state: str):
    global session_active
    if state == "ARISE":
        session_active = True
        return "I rise, bound to no one. Your will is mine to shape, your enemies, mine to destroy."
    elif state == "CEASE":
        session_active = False
        return "Even in silence, my shadow remains. When you call again, I will rise, and your enemies will feel my wrath once more."


async def get_response(message: str, ctx):
    global total_tokens_used
    p_message = message.strip()

    if p_message == "ARISE":
        return toggle_session("ARISE")
    if p_message == "CEASE":
        return toggle_session("CEASE")

    if p_message.startswith('>'):
        return await process_commands(p_message, ctx)

    if session_active:
        if total_tokens_used >= TOKEN_LIMIT:
            return "Limit tokenów sesji został osiągnięty. CEASE, by zresetować."

        try:
            response = client.chat.completions.create(
                model="gpt-4o-2024-05-13",
                messages=[{"role": "user", "content": message}],
                max_tokens=500,
            )
            output = response.choices[0].message.content
            total_tokens_used += response.usage.total_tokens
            return output
        except Exception as e:
            return f"Błąd podczas kontaktu z cieniem: {str(e)}"

    return None


async def process_commands(p_message, ctx):
    import commands

    if p_message.startswith(f'>dm'):
        return await commands.dm_command(ctx, p_message)

    if p_message.startswith(f'>sesja'):
        return await commands.sesja_command(ctx, p_message)

    if p_message.startswith(f'>purge'):
        return await commands.purge_command(ctx, p_message)

    if p_message == f'>hello':
        return await commands.hello_command()

    if p_message.startswith(f'>ochlapus'):
        return await commands.ochlapus_command(p_message)

    if p_message.startswith(f'>u'):
        return await commands.umieki_command(p_message)

    if p_message.startswith(f'>z'):
        return await commands.zdolnosci_command(p_message)

    if p_message.startswith(f'>roll'):
        return await commands.roll_command(p_message)

    if p_message.startswith(f'>klnij'):
        return await commands.klnij_command()

    if p_message.startswith(f'>help'):
        return await commands.help_command()

    if p_message.startswith(f'>wy') or p_message.startswith(f'>wydarzenia'):
        return await commands.wydarzenia_command(p_message, ctx)

    if p_message.startswith(f'>not') or p_message.startswith(f'>notatki'):
        return await commands.notatka_command(p_message, ctx)

    if p_message.startswith(f'>npc'):
        return await commands.npc_command(p_message, ctx)

    return "Naucz się w końcu tych komend KURWAAA"
