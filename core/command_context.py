class CommandContext:
    def __init__(self, bot, message):
        self.bot = bot
        self.message = message
        self.author = message.author
        self.channel = message.channel
        self.guild = message.guild
        self.content = message.content
