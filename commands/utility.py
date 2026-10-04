from config.settings import COMMAND_PREFIX, settings


def has_admin_permissions(ctx):
    if settings.owner_id is not None and ctx.author.id == settings.owner_id:
        return True

    if ctx.guild is None:
        return False

    if settings.gm_role_id is not None:
        return any(role.id == settings.gm_role_id for role in getattr(ctx.author, "roles", []))

    return False


def command_usage(syntax: str) -> str:
    return f"`{COMMAND_PREFIX}{syntax}`"
