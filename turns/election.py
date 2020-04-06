import discord
from discord.ext import commands
import asyncio
import random
import constant
from data_struct.bot import Bot
from vote import vote
from data_struct.roles import Mayor
bot = Bot()


async def election():

    # find the target:
    # print(bot.LOUP_TARGETS)
    counter_max_elections = constant.NB_MAX_MAYOR_ELECTIONS
    targets_choice = []
    while(len(targets_choice) != 1 and counter_max_elections > 0):

        ### warn village ###
        await bot.HISTORY_TEXT_CHANNEL.send(f'\n\n**Les villageois ont {constant.TIME_FOR_MAYOR_ELECTION} secondes pour choisir le maire:**\n\n')

        targets_choice = await vote(channel=bot.HISTORY_TEXT_CHANNEL, target_players=bot.ALIVE_PLAYERS, voters=bot.ALIVE_PLAYERS, emoji=Mayor.emoji, time=constant.TIME_FOR_MAYOR_ELECTION)

        counter_max_elections -= 1

    target_choice = None
    target_player = None
    # no mayor has been chosen
    if(len(targets_choice) == 0):
        target_player = random.choice(bot.ALIVE_PLAYERS)
    # draw for the votes
    elif(len(targets_choice) > 1):
        # choose the target randomly
        target_choice = random.choice(targets_choice)
        target_player = target_choice.player
    elif(len(targets_choice) == 1):
        target_choice = targets_choice[0]
        target_player = target_choice.player
    else:
        print(
            "error in election: not len(targets_choice) > 1, not len(targets_choice) == 1")
        raise Exception

    return target_player
