import datetime
import random

from discord.ext.commands import Bot, MissingRequiredArgument

from . import commands, translation
from .cogs.deejay import deejay
from .cogs.jogodavelha import jogodavelha


class Akira(Bot):
    """Bot que fala em miau. Contém módulo de tradução embutido."""

    def __init__(self, command_prefix='$'):
        self.__test_channel_id = 398636498112741376
        self.__command_prefix = command_prefix
        super().__init__(command_prefix)

    async def on_ready(self):
        self.on_ready_time = datetime.datetime.now(datetime.timezone.utc)
        print(f'{self.user} has connected to Discord!')

    async def on_message(self, message):
        channel = message.channel

        if self.is_myself(message.author.id):
            # messages sent by me
            return

        if self.is_command(message.content):
            # it is a command
            if self.should_ignore():
                meow = translation.pt_to_miau(translation.InfoMessages.LATER)
                await translation.send_with_reaction(channel.send, meow)
            else:
                await self.process_commands(message)

    async def on_raw_reaction_add(self, payload):
        if self.is_myself(payload.user_id):
            # reaction added by me
            return

        if not self.is_emoji_control(payload.emoji.name):
            # the reaction's emoji is not a control
            return

        channel = self.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        if not self.is_myself(message.author.id):
            # message isn't mine
            return

        if message.edited_at:
            # this message already has a translation
            return

        trans = translation.miau_to_pt(message.content)
        content_translated = f'{message.content}\n  *{trans}*'
        await message.edit(content=content_translated)

    async def on_command_error(self, ctx, exception):
        if isinstance(exception, MissingRequiredArgument):
            miau = translation.pt_to_miau(
                translation.InfoMessages.COMMAND_MISUSE
            )
            await translation.send_with_reaction(ctx.send, miau)
        else:
            raise exception

    def add_commands(self):
        self.add_command(commands.echo)
        self.add_command(commands.uptime)
        self.add_command(commands.codiguis)
        self.add_cog(deejay.Deejay(self))
        self.add_cog(jogodavelha.JogoDaVelha(self))

    def is_myself(self, id):
        """Decides if id is myself's id"""
        return self.user.id == id

    def is_command(self, msg):
        """Decides if a message is a command"""
        return msg.startswith(self.__command_prefix)

    def is_emoji_control(self, emoji):
        """Decides if an emoji is a control"""
        return emoji == '❔'

    def should_ignore(self):
        """Decides if should ignore a command"""
        return random.random() < 0.07
