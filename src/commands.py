from discord.ext.commands import command


@command()
async def echo(ctx, arg):
    await ctx.send(arg)
