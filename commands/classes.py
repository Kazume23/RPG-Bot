from services.character_classes import show_all_classes, show_class_info


async def classes_command(ctx):
    parts = ctx.content.split(maxsplit=2)

    if len(parts) == 1:
        return await show_all_classes()

    if len(parts) > 2:
        return "Naucz się dobrze wpisywać klasy przyczłapie"

    char_class = parts[1]

    return await show_class_info(char_class)
