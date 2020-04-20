from discord.ext.commands import command, Cog


class Bibliotekira(Cog):

    def __init__(self, bot):
        self.bot = bot

    async def add_translation(self, message):
        content = message.content
        if not message.edited_at:
            await message.edit(content=f'{content}\nEDIT')
