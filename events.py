from data_struct.bot import Bot
from discord.ext import commands
from create_emojis import create_emojis
from create_discord_role import create_discord_role
import constant

bot = Bot()

# on ready function: when the bot connects to the server
@bot.event
async def on_ready():
    # the bot user is connected to Discord
    print(f'{bot.user.name} has connected to Discord!')
    await create_emojis()
    await create_discord_role()


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send(f"Vous n'avez pas le bon rôle discord pour cette action ({constant.MASTER_OF_THE_GAME})", delete_after=3)
    print(error)
    # raise

"""
@bot.event
async def on_reaction_add(reaction, user):
    print("an emoji has been sent:")
    print(reaction.emoji)
"""
