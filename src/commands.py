from discord.ext.commands import command


@command()
async def echo(ctx, *args):
    """
    Ecoa os argumentos
    """
    response = ' '.join(args)
    await ctx.send(response)


@command()
async def toca(ctx, *, args):
    """
    Toca a música no canal de voz do invocador. Continua tocando no canal de voz
    em que estiver.
    """
    
