"""Module with standalone commands"""
import datetime

from discord.ext.commands import command


@command()
async def echo(ctx, *args):
    """Ecoa os argumentos.

    :param str args: Texto que será ecoado.
    """
    response = ' '.join(args)
    await ctx.send(response)


@command()
async def uptime(ctx):
    """Uptime de Akira"""
    now = datetime.datetime.now(datetime.timezone.utc)
    td = now - ctx.bot.on_ready_time
    await ctx.send(f'Uptime: {td}')
