from discord.ext.commands import Bot
from . import commands
from .cogs import deejay, bibliotekira
import random

class Terraplanista(Bot):

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
                await channel.send('Isso aí é a tua opinião só.')
            else:
                await self.process_commands(message)
        elif random.random() < 0.13:
            await channel.send('Esse vírus é propaganda *cof cof* comunista!!!')

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
        bibliotekira = self.get_cog('Bibliotekira')
        await bibliotekira.add_translation(message)

    def add_commands(self):
        self.add_command(commands.echo)
        self.add_cog(deejay.Deejay(self))
        self.add_cog(bibliotekira.Bibliotekira(self))
