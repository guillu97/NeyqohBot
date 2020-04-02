import discord
from discord.ext import commands
import random
import asyncio
import constant
from data_struct.bot import Bot

bot = Bot()


async def chasseur_turn():
    await bot.HISTORY_TEXT_CHANNEL.send(f'\n\n**Le chasseur a {constant.TIME_FOR_CHASSEUR} secondes pour choisir sa victime**\n\n')
    bot.TURN = "CHASSEUR"

    # search chasseur
    chasseur = None
    for player in bot.DEADS:
        if(isinstance(player.role, Chasseur)):
            chasseur = player
            break

    if(chasseur == None):
        print("error in chasseur turn: chasseur = None")
        raise ValueError

    message = ""
    num = 0
    for player in bot.ALIVE_PLAYERS:
        message += f'{num}:  {player}\n'
        num += 1
    message += '\ncommande: !vote <int>\n'
    message += 'exemple: !vote 5\n'
    await bot.HISTORY_TEXT_CHANNEL.send(message)

    time_left = int(constant.TIME_FOR_CHASSEUR)
    await asyncio.sleep(time_left - 5)
    time_left = 5
    await bot.HISTORY_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
    await asyncio.sleep(time_left)

    bot.TURN = "FIN_CHASSEUR"

    if(chasseur.role.target_choice == None):
        rand_index = random.randint(0, len(bot.ALIVE_PLAYERS) - 1)
        chasseur.role.target_choice = bot.ALIVE_PLAYERS[rand_index]

    # warn of the choice
    await bot.HISTORY_TEXT_CHANNEL.send(f'\n**votre choix est fait, vous avez choisi de tuer cette personne: {chasseur.role.target_choice}**\n')
