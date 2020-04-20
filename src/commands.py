import discord
from discord.ext.commands import command


@command()
async def echo(ctx, *args):
    """
    Ecoa os argumentos.
    """
    response = ' '.join(args)
    message = await ctx.send(response)
    await message.add_reaction('❔')
