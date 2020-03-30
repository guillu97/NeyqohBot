from data_struct.singleton import Singleton
from discord.ext import commands
bot = Singleton()

# on ready function: when the bot connects to the server
@bot.event
async def on_ready():
    # the bot user is connected to Discord
    print(f'{bot.user.name} has connected to Discord!')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')
    print(error)
    # raise
