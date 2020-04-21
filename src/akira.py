from discord.ext.commands import Bot
import random

from . import commands
from .cogs import deejay, bibliotekira
from .utils import translation_book, send_with_reaction


class Akira(Bot):

    def __init__(self, command_prefix='$'):
        self.__test_channel_id = 398636498112741376
        self.__command_prefix = command_prefix
        super().__init__(command_prefix)
    
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

    async def on_message(self, message):
        # test channel only for now
        #if message.channel.id != self.__test_channel_id:
        #    return

        channel = message.channel

        if message.author.id == self.user.id:
            # messages sent by me
            return
        
        if message.content.startswith(self.__command_prefix):
            # it is a command
            if random.random() < 0.17:
                meow = translation_book.inverse['Talvez mais tarde.']
                await send_with_reaction(channel.send, meow)
            else:
                await self.process_commands(message)

    async def on_raw_reaction_add(self, payload):
        if payload.member == self.user:
            # reaction added by me
            return
        emoji = payload.emoji
        if not emoji.name in '❔':
            # the emoji is not one of these
            return

        channel = self.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        if message.author.id != self.user.id:
            # message isn't mine
            return

        bibliotekira = self.get_cog('Bibliotekira')
        await bibliotekira.add_translation(message)

    def add_commands(self):
        self.add_command(commands.echo)
        self.add_cog(bibliotekira.Bibliotekira(self))
        self.add_cog(deejay.Deejay(self))
