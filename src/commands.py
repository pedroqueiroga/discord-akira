from discord.ext.commands import command


@command()
async def echo(ctx, *args):
    """ecoa os argumentos"""
    response = ' '.join(args)
    await ctx.send(response)
