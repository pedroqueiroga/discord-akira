from config import settings
from src.bot import Terraplanista
import os

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

br = Terraplanista()

@br.command()
async def echo(ctx, arg):
    await ctx.send(arg)

br.run(DISCORD_TOKEN)

print('fim?')
