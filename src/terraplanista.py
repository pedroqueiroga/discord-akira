from discord.ext.commands import Bot
from . import commands


class Terraplanista(Bot):

    def __init__(self, command_prefix='$'):
        self.__test_channel_id = 398636498112741376
        self.__command_prefix=command_prefix
        super().__init__(command_prefix)
    
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

    async def on_message(self, message):
        print('on_message with message:')
        print(message)
        if message.author.id == self.user.id:
            # messages sent by me
            print('on_message sent by me')
            return

        if message.channel.id == self.__test_channel_id:
            if message.content.startswith(self.__command_prefix):
                # it is a command
                await self.process_commands(message)
                return
            
            channel = message.channel
            await channel.send('esse vírus é propaganda *cof cof* comunista!!!')

    def add_commands(self):
        self.add_command(commands.echo)
