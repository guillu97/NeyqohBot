from data_struct.bot import Bot
import constant
import discord
from discord import Colour

bot = Bot()


async def create_discord_role():
    for guild in bot.guilds:
        if(not discord.utils.get(guild.roles, name=constant.MASTER_OF_THE_GAME)):
            await guild.create_role(name=constant.MASTER_OF_THE_GAME, colour=Colour.dark_red(), hoist=True)
