import discord
from discord.ext import commands
import asyncio
import random
import constant
from data_struct.bot import Bot
from data_struct.roles import Cupidon
from vote import vote
bot = Bot()

# return [Players] len()==2


async def cupidon_turn():
    # search Cupidon
    cupidon = None
    for player in bot.ALIVE_PLAYERS:
        if(isinstance(player.role, Cupidon)):
            cupidon = player
            break

    if(cupidon == None):
        print("error in cupidon turn: cupidon = None")
        raise ValueError

    amoureux = []

    await bot.HISTORY_TEXT_CHANNEL.send(f"Cupidon a {constant.TIME_FOR_CUPIDON} secondes pour choisir les amoureux (et plus s'il n'arrive pas à choisir)\n\n")
    #bot.TURN = "CUPIDON"

    await cupidon.private_channel.send(f'**Vous avez {constant.TIME_FOR_CUPIDON} secondes pour choisir les amoureux**\n**Vous allez choisir les amoureux un par un**\n')

    ### vote ###
    targets_choice = []
    tempTable = []
    while(len(tempTable) != 1):
        await cupidon.private_channel.send(f'**Amoureux 1:**')
        tempTable = await vote(channel=cupidon.private_channel, target_players=bot.ALIVE_PLAYERS, voters=[cupidon], emoji="💘", time=int(constant.TIME_FOR_CUPIDON/2))

    targets_choice.append(tempTable[0].player)
    tempTable.clear()
    await cupidon.private_channel.send(f'\nVous avez choisi **{targets_choice[0]}**\n')

    all_players_without_first_lover = [
        player for player in bot.ALIVE_PLAYERS if player not in targets_choice]
    while(len(tempTable) != 1):
        await cupidon.private_channel.send(f'Amoureux 2:')
        tempTable = await vote(channel=cupidon.private_channel, target_players=all_players_without_first_lover, voters=[cupidon], emoji="💘", time=int(constant.TIME_FOR_CUPIDON/2))

    targets_choice.append(tempTable[0].player)
    await cupidon.private_channel.send(f'\nVous avez choisi **{targets_choice[1]}**\n')

    # warn of the choice
    await cupidon.private_channel.send(f'\n**Votre choix est fait, les amoureux sont: {targets_choice[0]} et {targets_choice[1]}**\n')

    # send message to the amoureux
    await targets_choice[0].private_channel.send(f'\n**Vous êtes amoureux avec : {targets_choice[1]}**\n')
    await targets_choice[1].private_channel.send(f'\n**Vous êtes amoureux avec : {targets_choice[0]}**\n')

    await asyncio.sleep(4)
    return targets_choice
