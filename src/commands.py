import discord
from discord.ext.commands import command


@command()
async def echo(ctx, *args):
    """Ecoa os argumentos.

    :param str args: Texto que será ecoado.
    """
    response = ' '.join(args)
    await ctx.send(response)
