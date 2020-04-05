import discord
from discord.ext import commands
import random
import asyncio
import constant
from data_struct.bot import Bot
from data_struct.roles import Chasseur
from vote import vote

bot = Bot()


async def chasseur_turn(chasseur):

    #bot.TURN = "CHASSEUR"

    await bot.HISTORY_TEXT_CHANNEL.send(f'\n\n**Le chasseur {chasseur} a {constant.TIME_FOR_CHASSEUR} secondes pour choisir sa victime**\n\n')

    targets_choice = await vote(channel=bot.HISTORY_TEXT_CHANNEL, target_players=bot.ALIVE_PLAYERS, voters=[chasseur], emoji="🔫", time=constant.TIME_FOR_CHASSEUR)

    target_choice = None
    target_player = None
    if(len(targets_choice) == 0):
        await bot.HISTORY_TEXT_CHANNEL.send("\n**vous n'avez choisi personne**\n")
    elif(len(targets_choice) == 1):
        target_choice = targets_choice[0]
        target_player = target_choice.player
        # warn of the choice
        await bot.HISTORY_TEXT_CHANNEL.send(f'\n**votre choix est fait, vous avez choisi de tuer cette personne: {target_player}**\n')
    else:
        print(
            "error in chasseur_turn")
        raise Exception

    return target_player
