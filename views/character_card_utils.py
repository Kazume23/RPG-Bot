import discord

FIELD_VALUE_LIMIT = 1024
FIELD_NAME_LIMIT = 256
MAX_FIELDS = 25
MAX_EMBED_LENGTH = 5800


def safe(value) -> str:
    return discord.utils.escape_markdown(
        str(value).strip()
    )


def inline_code(value) -> str:
    safe_value = str(value).replace(
        "`",
        "'",
    )

    return f"`{safe_value}`"


def embed_length(
        embed: discord.Embed,
) -> int:
    total = len(
        embed.title or ""
    )

    total += len(
        embed.description or ""
    )

    footer_text = getattr(
        embed.footer,
        "text",
        None,
    )

    if footer_text:
        total += len(footer_text)

    for field in embed.fields:
        total += len(field.name)
        total += len(field.value)

    return total


def split_text(
        text: str,
        limit: int = FIELD_VALUE_LIMIT,
) -> list[str]:
    if len(text) <= limit:
        return [text]

    chunks = []
    current = ""

    for line in text.splitlines():
        if len(line) > limit:
            if current:
                chunks.append(current)
                current = ""

            for start in range(
                    0,
                    len(line),
                    limit,
            ):
                chunks.append(
                    line[
                    start:
                    start + limit
                    ]
                )

            continue

        candidate = line

        if current:
            candidate = (
                f"{current}\n{line}"
            )

        if len(candidate) <= limit:
            current = candidate
            continue

        chunks.append(current)
        current = line

    if current:
        chunks.append(current)

    return chunks


def add_field(
        embed: discord.Embed,
        name: str,
        value: str,
        inline: bool = False,
) -> bool:
    if len(embed.fields) >= MAX_FIELDS:
        return False

    name = name[:FIELD_NAME_LIMIT]

    remaining = (
            MAX_EMBED_LENGTH
            - embed_length(embed)
            - len(name)
    )

    if remaining <= 0:
        return False

    max_value_length = min(
        FIELD_VALUE_LIMIT,
        remaining,
    )

    value = value[:max_value_length]

    if not value:
        return False

    embed.add_field(
        name=name,
        value=value,
        inline=inline,
    )

    return True


def add_section(
        embed: discord.Embed,
        title: str,
        values: list[str],
        bullets: bool = True,
) -> None:
    if not values:
        return

    if bullets:
        lines = [
            f"• {safe(value)}"
            for value in values
        ]
    else:
        lines = values

    text = "\n".join(lines)

    for index, chunk in enumerate(
            split_text(text)
    ):
        field_name = (
            title
            if index == 0
            else f"{title} (cd.)"
        )

        if not add_field(
                embed,
                field_name,
                chunk,
        ):
            return
