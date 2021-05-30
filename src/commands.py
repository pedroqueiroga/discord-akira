"""Module with standalone commands"""
import datetime

from discord.ext.commands import Context, command


@command()
async def echo(ctx: Context, *args) -> None:
    """Ecoa os argumentos.

    :param str args: Texto que será ecoado.
    """
    response = ' '.join(args)
    await ctx.send(response)


@command()
async def uptime(ctx: Context) -> None:
    """Uptime de Akira"""
    now = datetime.datetime.now(datetime.timezone.utc)
    td = now - ctx.bot.on_ready_time
    await ctx.send(f'Uptime: {td}')


@command()
async def codiguis(ctx: Context) -> None:
    """Informa onde o código de Akira está hospedado"""
    localizacao = 'https://github.com/pedroqueiroga/discord-akira'
    await ctx.send(localizacao)


@command()
async def ajuda(ctx: Context, *args) -> None:
    await ctx.send_help(*args)
