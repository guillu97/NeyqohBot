import discord
from discord.ext import commands
import asyncio
import constant
from data_struct.roles import Voyante
from data_struct.bot import Bot
from vote import vote

bot = Bot()


async def voyantes_turn():
    await bot.HISTORY_TEXT_CHANNEL.send(f'La voyante a {constant.TIME_FOR_VOYANTE} secondes pour choisir un joueur\n\n')
    bot.TURN = "VOYANTE"

    # find the voyante(s)
    voyantes = [player for player in bot.ALIVE_PLAYERS if(
        isinstance(player.role, Voyante))]

    tasks = []
    for voyante in voyantes:
        tasks.append(asyncio.ensure_future(voyante_play(voyante)))
    await asyncio.gather(*tasks)


async def voyante_play(voyante):
    # warn voyante
    message = f'Vous avez {constant.TIME_FOR_VOYANTE} secondes pour choisir le joueur dont le role vous intéresse\n\n'

    all_players_but_voyante = [
        player for player in bot.ALIVE_PLAYERS if player != voyante]
    targets_choice = await vote(channel=voyante.private_channel, target_players=all_players_but_voyante, voters=[voyante], emoji="👍", time=constant.TIME_FOR_VOYANTE)
    """
    time_left = constant.TIME_FOR_VOYANTE

    num = 0
    for player in bot.ALIVE_PLAYERS:
        message += f'{num}:  {player}\n'
        num += 1
    message += '\ncommande: !vote <int>\n'
    message += 'exemple: !vote 5\n'

    await voyante.private_channel.send(message)

    await asyncio.sleep(time_left - 10)
    time_left = 10
    await voyante.private_channel.send(f'{time_left} secondes restantes')
    await asyncio.sleep(time_left - 5)
    time_left = 5
    await voyante.private_channel.send(f'{time_left} secondes restantes')
    await asyncio.sleep(time_left)

    bot.TURN = "FIN_VOYANTE"
    """

    target_choice = None
    target_player = None
    # warn of the choice
    if(len(targets_choice) == 0):
        await voyante.private_channel.send("\n**vous n'avez choisi personne**\n")
    elif(len(targets_choice) == 1):
        target_choice = targets_choice[0]
        target_player = target_choice.player
        await voyante.private_channel.send(f'\nVous avez choisi **{target_player}** qui est **{target_player.role}** {target_player.role.emoji}\n')
    else:
        print(
            "error in voyante_turn : not len(voyante.targets) == 0  and not len(voyante.targets) == 1")
        raise Exception
