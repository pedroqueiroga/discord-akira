from discord.ext.commands import command, Cog

from ..utils import translation_book, is_int


class Bibliotekira(Cog):

    def __init__(self, bot):
        self.bot = bot

    async def add_translation(self, message):
        content = message.content
        if not message.edited_at:
            translation = translation_book[content]
            if is_int(translation):
                plural = 's' if int(translation) > 1 else ''
                translation = f'Preciso de mais {translation} voto{plural} para pular.'
            await message.edit(content=f'{content}\n  *{translation}*')

