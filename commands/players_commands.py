import discord
from discord.ext import commands
import asyncio
import constant
from data_struct.bot import Bot
from data_struct.player import Player
from data_struct.roles import *
from roles_compute import calc_roles, assign_roles

from data_struct.target import Target

bot = Bot()


@bot.command(name='join', help='rejoindre une partie')
# @commands.has_role(MASTER_OF_THE_GAME)
async def join_game(ctx):
    name = ctx.author.display_name
    print(f'{name} tried to joined')

    if(bot.GAME_CREATED == False):
        await ctx.send(f'aucune partie en cours')
        return

    if(bot.GAME_STARTED == True):
        await ctx.send(f'la partie a déjà commencé')
        return

    if(ctx.message.channel != bot.BEGINNING_CHANNEL):
        await ctx.send('message envoyé dans le mauvais channel')
        return

    print(bot.GAME_CREATED, bot.GAME_STARTED)

    # print(ctx.__dict__)
    memberList = [player.discordMember for player in bot.PLAYERS]
    if(ctx.author in memberList):
        await ctx.send(f'{name} vous êtes déjà dans la partie')
        return

    bot.PLAYERS.append(Player(ctx.author))

    roles = await calc_roles(verbose=True)
    message_content = f'**{name} a rejoint la partie**\n\n'
    if(roles != None):
        print(roles)
        message_content += f'joueurs: {" ".join(map(str,bot.PLAYERS))}\n\n'
        message_content += f'{roles}\n'

    message = await ctx.send(message_content)
    # await asyncio.sleep(constant.TIME_DELETE_MSG)
    # await message.delete()
    # await ctx.message.delete()


@bot.command(name='players', help="montre les joueurs actuellement dans la partie")
# @commands.has_role(constant.MASTER_OF_THE_GAME)
async def show_players(ctx):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie créée', delete_after=2)
        return
    await ctx.send("\n".join(map(str, bot.PLAYERS)))

# TODO : create a command to known which roles are left


@bot.command(name='players-alive', help="montre les joueurs vivants actuellement dans la partie")
# @commands.has_role(constant.MASTER_OF_THE_GAME)
async def show_players_alive(ctx):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie créée', delete_after=2)
        return
    if(bot.GAME_STARTED == False):
        await ctx.send("la partie n'a pas commencée")
        return

    await ctx.send("\n".join(map(str, bot.ALIVE_PLAYERS)))
