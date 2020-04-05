import discord
from discord.ext import commands
import asyncio
import random
import constant
from data_struct.bot import Bot
from data_struct.roles import Mayor
from vote import vote

bot = Bot()


async def mayor_give_up(mayor):

    await bot.HISTORY_TEXT_CHANNEL.send(f'\n\n**Le maire **{mayor}** a {constant.TIME_FOR_MAYOR_GIVE_UP} secondes pour désigner le nouveau maire:**\n\n')

    targets_choice = await vote(channel=bot.HISTORY_TEXT_CHANNEL, target_players=bot.ALIVE_PLAYERS, voters=[mayor], emoji=Mayor.emoji, time=constant.TIME_FOR_MAYOR_GIVE_UP)

    target_choice = None
    target_player = None
    # if no target
    if(len(targets_choice) == 0):
        # choose the target randomly
        target_choice = random.choice(bot.ALIVE_PLAYERS)
        target_player = target_choice.player
    elif(len(targets_choice) == 1):
        target_choice = targets_choice[0]
        target_player = target_choice.player
    else:
        print(
            "error in election: not len(targets_choice) > 1, not len(targets_choice) == 1")
        raise Exception
    #bot.TURN = "FIN_MAYOR_GIVE_UP"
    # results
    # warn players of the choice
    await bot.HISTORY_TEXT_CHANNEL.send(f'votre choix est fait, vous avez choisi **{target_player}** comme nouveau Maire')
    await asyncio.sleep(1)
    #bot.MAYOR = target_choice
    # bot.MAYOR_CHOICES.clear()
    return target_player


async def mayor_choice():

    message = f'Le Maire a {constant.TIME_FOR_MAYOR_FINAL_CHOICE} secondes pour choisir la victime finale\n\n'

    num = 0
    for target in bot.MAYOR_ONLY_CHOICES:
        message += f'{num}:  {target.player}\n'
        num += 1
    message += '\ncommande: !vote <int>\n'
    message += 'exemple: !vote 5\n'

    bot.TURN = "MAYOR_CHOICE"
    await bot.HISTORY_TEXT_CHANNEL.send(message)

    time_left = constant.TIME_FOR_MAYOR_FINAL_CHOICE
    await asyncio.sleep(time_left - 10)
    time_left = 10
    await bot.LOUPS_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
    await asyncio.sleep(time_left - 5)
    time_left = 5
    await bot.LOUPS_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
    await asyncio.sleep(time_left)

    # there were targets from the whole village
    # there was no target from the village => bot.MAYOR_ONLY_CHOICES = all alive_players as Targets

    # the mayor have chosen one
    # the mayor havn't chosen one

    # find the target:
    targets_choice = []
    max_accusator = max([len(target.accusators)
                         for target in bot.MAYOR_ONLY_CHOICES])
    targets_choice = [target for target in bot.MAYOR_ONLY_CHOICES if len(
        target.accusators) == max_accusator]

    target_choice = None
    # if still target
    if(len(targets_choice) > 1):
        # no dead from the loups
        await bot.HISTORY_TEXT_CHANNEL.send("\n**vous n'avez pas choisi de victime, la victime va être aléatoire**\n")
        # choose the target randomly
        rand_index = random.randint(0, len(targets_choice) - 1)
        target_choice = targets_choice[rand_index].player
    elif(len(targets_choice) == 1):
        target_choice = targets_choice[0].player
    else:
        print("error mayor_choice: len(targets_choice) < 1")
        raise Exception

    if(target_choice == None):
        print("error mayor_choice: target_choice == None")
        raise Exception

    bot.MAYOR_ONLY_CHOICES.clear()

    bot.TURN = "FIN_MAYOR_CHOICE"
    return target_choice
