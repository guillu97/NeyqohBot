import discord
from discord.ext import commands
import asyncio
import random
import constant
from data_struct.bot import Bot

bot = Bot()


async def cupidon_turn():
    await bot.HISTORY_TEXT_CHANNEL.send(f'Cupidon a {constant.TIME_FOR_CUPIDON} secondes pour choisir les amoureux\n\n')
    bot.TURN = "CUPIDON"

    # search Cupidon
    cupidon = None
    for player in bot.ALIVE_PLAYERS:
        if(isinstance(player.role, Cupidon)):
            cupidon = player
            break

    if(cupidon == None):
        print("error in cupidon turn: cupidon = None")
        raise ValueError

    await cupidon.private_channel.send(f'Vous avez {constant.TIME_FOR_CUPIDON} secondes pour choisir les amoureux\n\n')

    message = ""
    num = 0
    for player in bot.ALIVE_PLAYERS:
        message += f'{num}:  {player}\n'
        num += 1
    message += '\ncommande: !vote <int>\n'
    message += 'exemple: !vote 5\n'
    await cupidon.private_channel.send(message)

    time_left = int(constant.TIME_FOR_CUPIDON)
    await asyncio.sleep(time_left - 5)
    time_left = 5
    await cupidon.private_channel.send(f'{time_left} secondes restantes')
    await asyncio.sleep(time_left)

    bot.TURN = "FIN_CUPIDON"

    if(len(cupidon.role.targets_choice) == 0):
        rand_index = random.randint(0, len(bot.ALIVE_PLAYERS) - 1)
        cupidon.role.targets_choice.append(
            bot.ALIVE_PLAYERS[rand_index])

        rand_index2 = rand_index
        while(rand_index2 == rand_index):
            rand_index2 = random.randint(0, len(bot.ALIVE_PLAYERS) - 1)

        cupidon.role.targets_choice.append(
            bot.ALIVE_PLAYERS[rand_index2])

    if(len(cupidon.role.targets_choice) == 1):
        target = cupidon.role.targets_choice[0]
        while(target in cupidon.role.targets_choice):
            rand_index = random.randint(0, len(bot.ALIVE_PLAYERS) - 1)
            target = bot.ALIVE_PLAYERS[rand_index]
        cupidon.role.targets_choice.append(bot.ALIVE_PLAYERS[rand_index])

    bot.AMOUREUX = cupidon.role.targets_choice

    # warn of the choice
    message = f'\n**Votre choix est fait, les amoureux sont: {bot.AMOUREUX[0]} et {bot.AMOUREUX[1]}**\n'
    await cupidon.private_channel.send(message)

    # send message to the amoureux
    message = f'\n**Vous êtes amoureux avec : {bot.AMOUREUX[1]}**\n'
    await bot.AMOUREUX[0].private_channel.send(message)
    message = f'\n**Vous êtes amoureux avec : {bot.AMOUREUX[0]}**\n'
    await bot.AMOUREUX[1].private_channel.send(message)

    await asyncio.sleep(4)
