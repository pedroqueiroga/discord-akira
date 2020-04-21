from discord.ext.commands import Bot
import random

from . import commands, translation
from .cogs import deejay


class Akira(Bot):
    """Bot que fala em miau. Contém módulo de tradução embutido."""

    def __init__(self, command_prefix='$'):
        self.__test_channel_id = 398636498112741376
        self.__command_prefix = command_prefix
        super().__init__(command_prefix)
    
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

    async def on_message(self, message):
        channel = message.channel

        if message.author.id == self.user.id:
            # messages sent by me
            return
        
        if message.content.startswith(self.__command_prefix):
            # it is a command
            if random.random() < 0.07:
                meow = translation.pt_to_miau(translation.InfoMessages.LATER)
                await translation.send_with_reaction(channel.send, meow)
            else:
                await self.process_commands(message)

    async def on_raw_reaction_add(self, payload):
        if payload.member == self.user:
            # reaction added by me
            return

        if not payload.emoji.name in '❔':
            # the emoji is not one of these
            return

        channel = self.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        if message.author.id != self.user.id:
            # message isn't mine
            return

        if message.edited_at:
           # this message already has a translation
            return

        trans = translation.miau_to_pt(message.content)
        content_translated = f'{message.content}\n  *{trans}*'
        await message.edit(content=content_translated)
        
    def add_commands(self):
        self.add_command(commands.echo)
        self.add_cog(deejay.Deejay(self))
