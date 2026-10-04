from services.character_classes import show_all_classes, show_class_info


async def classes_command(args: str):
    class_name = args.strip()
    if not class_name:
        return await show_all_classes()

    try:
        return await show_class_info(class_name)
    except KeyError:
        return "Naucz się dobrze wpisywać klasy przyczłapie"
