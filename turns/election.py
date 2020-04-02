import discord
from discord.ext import commands
import asyncio
import random
import constant
from data_struct.bot import Bot

bot = Bot()


async def election():

    # find the target:
    # print(bot.LOUP_TARGETS)
    counter_max_elections = constant.NB_MAX_MAYOR_ELECTIONS
    targets_choice = []
    while(len(targets_choice) != 1 and counter_max_elections > 0):

        ### warn village ###
        message = f'\n\n**Les villageois ont {constant.TIME_FOR_MAYOR_ELECTION} secondes pour choisir le maire:**\n\n'
        bot.TURN = "MAYOR_ELECTION"

        ### vote ###

        time_left = constant.TIME_FOR_MAYOR_ELECTION

        num = 0
        for player in bot.ALIVE_PLAYERS:
            message += f'{num}:  {player}\n'
            num += 1
        message += '\ncommande: !vote <int>\n'
        message += 'exemple: !vote 5\n'
        await bot.HISTORY_TEXT_CHANNEL.send(message)

        await asyncio.sleep(time_left - 30)
        time_left = 30
        await bot.HISTORY_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
        await asyncio.sleep(time_left - 20)
        time_left = 20
        await bot.HISTORY_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
        await asyncio.sleep(time_left - 10)
        time_left = 10
        await bot.HISTORY_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
        await asyncio.sleep(time_left - 5)
        time_left = 5
        await bot.HISTORY_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
        await asyncio.sleep(time_left)

        # if no target
        if(len(bot.MAYOR_TARGETS) == 0 and counter_max_elections != 0):
            # no mayor choice from the players
            await bot.HISTORY_TEXT_CHANNEL.send("\n\n**Vous n'avez pas choisi de maire, une nouvelle election va avoir lieu**\n\n")
        else:
            targets_choice.clear()
            max_accusator = max([len(target.accusators)
                                 for target in bot.MAYOR_TARGETS])
            targets_choice = [target for target in bot.MAYOR_TARGETS if len(
                target.accusators) == max_accusator]

        bot.MAYOR_TARGETS.clear()

        counter_max_elections -= 1

    # no mayor have been choose
    if(len(targets_choice) == 0):
        rand_index = random.randint(0, len(bot.ALIVE_PLAYERS) - 1)
        target_choice = bot.ALIVE_PLAYERS[rand_index]
    # draw for the votes
    elif(len(targets_choice) > 1):
        # choose the target randomly
        rand_index = random.randint(0, len(targets_choice) - 1)
        target_choice = targets_choice[rand_index].player
    elif(len(targets_choice) == 1):
        target_choice = targets_choice[0].player
    else:
        print(
            "error in election: not len(targets_choice) > 1, not len(targets_choice) == 1")
        raise Exception

    bot.TURN = "FIN_MAYOR_ELECTION"

    # results
    # warn players of the choice
    await bot.HISTORY_TEXT_CHANNEL.send(f'\n\nvotre choix est fait, le maire est **{target_choice}**\n\n')
    await asyncio.sleep(1)
    bot.MAYOR = target_choice
    bot.MAYOR_TARGETS.clear()
