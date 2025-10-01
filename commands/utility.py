import os

ADMIN_ID = int(os.getenv("ADMIN_ID"))


def has_admin_permissions(ctx):
    if ctx.guild:
        return ctx.author.guild_permissions.administrator
    else:
        return ctx.author.id == ADMIN_ID
