import discord
import asyncio
import constant
import random
from data_struct.roles import Salvateur
from data_struct.bot import Bot
from vote import vote


bot = Bot()


async def salvateur_turn():
    # find salvateur
    salvateur = None
    for player in bot.ALIVE_PLAYERS:
        if(isinstance(player.role, Salvateur)):
            salvateur = player
            break

    if(salvateur == None):
        print("error in salvateur_turn: salvateur = None")
        raise ValueError

    # warn village
    await bot.HISTORY_TEXT_CHANNEL.send(f"Le salvateur a {constant.TIME_FOR_SALVATEUR} secondes pour choisir le joueur qu'il veut protéger des loups-garous pendant la nuit\n")
    # warn salvateur
    await salvateur.private_channel.send(f'Vous avez {constant.TIME_FOR_SALVATEUR} secondes pour choisir le joueur que vous voulez protéger des loups-garous cette nuit\n\n')

    all_players_but_salvateur_last_target = [
        player for player in bot.ALIVE_PLAYERS if player != salvateur.role.target_choice]
    targets_choice = await vote(channel=salvateur.private_channel, target_players=all_players_but_salvateur_last_target, voters=[salvateur], emoji="🛡️", time=constant.TIME_FOR_SALVATEUR)

    target_choice = None
    target_player = None
    # warn of the choice
    if(len(targets_choice) == 0):
        await salvateur.private_channel.send("\n**vous n'avez choisi personne**\n")
    elif(len(targets_choice) == 1):
        target_choice = targets_choice[0]
        target_player = target_choice.player
        await salvateur.private_channel.send(f'\nVous avez choisi de protéger **{target_player}** \n')
        salvateur.role.target_choice = target_player
    elif(len(targets_choice) > 0):
        target_choice = random.choice(targets_choice)
        target_player = target_choice.player
        await salvateur.private_channel.send(f'\nVous avez choisi de protéger **{target_player}** \n')
        salvateur.role.target_choice = target_player
    return target_player
