import discord
from discord.ext import commands
import asyncio
import constant
from data_struct.roles import EnfantSauvage
from data_struct.bot import Bot
from vote import vote

bot = Bot()


async def enfant_sauvage_turn():
    await bot.HISTORY_TEXT_CHANNEL.send(f"L'enfant sauvage a {constant.TIME_FOR_ENFANT_SAUVAGE} secondes pour choisir son maitre (ou plus jusqu'à ce qu'il choisisse) \n\n")
    # search enfant sauvage
    enfantSauvage = None
    for player in bot.ALIVE_PLAYERS:
        if(isinstance(player.role, EnfantSauvage)):
            enfantSauvage = player
            break
    if(enfantSauvage == None):
        print('error in enfant_sauvage_turn: enfantSauvage = None')
        raise Exception

    # warn enfantSauvage
    await enfantSauvage.private_channel.send(f'Vous avez {constant.TIME_FOR_ENFANT_SAUVAGE} secondes pour choisir votre maitre\n\n')

    all_players_but_enfant_sauvage = [
        player for player in bot.ALIVE_PLAYERS if player != enfantSauvage]
    targets_choice = []
    while(len(targets_choice) != 1):
        targets_choice = await vote(channel=enfantSauvage.private_channel, target_players=all_players_but_enfant_sauvage, voters=[enfantSauvage], emoji="👍", time=constant.TIME_FOR_ENFANT_SAUVAGE)

    target_choice = None
    target_player = None
    # warn of the choice
    if(len(targets_choice) == 1):
        target_choice = targets_choice[0]
        target_player = target_choice.player
        enfantSauvage.role.target_choice = target_player
        await enfantSauvage.private_channel.send(f'\nVous avez choisi **{target_player}** comme maitre\n')
    else:
        print(
            "error in enfant_sauvage_turn : not len(enfant_sauvage.targets) == 1")
        raise Exception
