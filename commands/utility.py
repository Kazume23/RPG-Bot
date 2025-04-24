def has_admin_permissions(ctx):
    return ctx.author.guild_permissions.administrator