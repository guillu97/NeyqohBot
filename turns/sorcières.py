import discord
from discord.ext import commands
import asyncio
import constant
from data_struct.bot import Bot
from data_struct.roles import Sorcière
from vote import vote

bot = Bot()


async def sorcières_turn():
    await bot.HISTORY_TEXT_CHANNEL.send(f'La sorcière a {constant.TIME_FOR_SORCIERE} secondes pour choisir ses actions\n\n')

    # find the sorcière
    sorcières = [player for player in bot.ALIVE_PLAYERS if(
        isinstance(player.role, Sorcière))]

    tasks = []
    for sorcière in sorcières:
        tasks.append(asyncio.ensure_future(sorcière_play(sorcière)))
    targets = await asyncio.gather(*tasks)
    targets = list(set(targets))
    targets = [target for target in targets if target != None]
    return targets


async def sorcière_play(sorcière):
    """for player in bot.ALIVE_PLAYERS:
        if(isinstance(player.role, Sorcière)):
            sorcière = player
    """

    """if(sorcière == None):
        print('sorcière play but no sorcière alive')
        raise Exception"""

    # show the victim of the loups if still life potion
    if(sorcière.role.lifePotion):
        if(bot.LOUP_FINAL_TARGET):

            message = '\nVoulez vous sauver cette personne?\n'

            await sorcière.private_channel.send(message)

            targets_choice = await vote(channel=sorcière.private_channel, target_players=[bot.LOUP_FINAL_TARGET], voters=[sorcière], emoji="👍", time=int(constant.TIME_FOR_SORCIERE/2))

            # warn of the choice
            if(len(targets_choice) == 0):
                await sorcière.private_channel.send("\n**vous n'avez pas choisi de sauver cette personne**\n")
            elif(len(targets_choice) == 1):
                await sorcière.private_channel.send(f'\n**votre choix est fait, vous avez choisi de sauver cette personne: {bot.LOUP_FINAL_TARGET}**\n')
                bot.LOUP_FINAL_TARGET = None
                sorcière.role.lifePotion = False
        else:
            await sorcière.private_channel.send("\n\n**Personne n'est mort ce soir**\n\n")
            time_left = int(constant.TIME_FOR_SORCIERE/2)
            await sorcière.private_channel.send(f"attendez {time_left} secondes pour votre prochaine action")
            await asyncio.sleep(time_left)

    else:
        time_left = int(constant.TIME_FOR_SORCIERE/2)
        await sorcière.private_channel.send(f"Vous avez déjà utilisé votre potion de vie, attendez {time_left} secondes pour votre prochaine action")
        await asyncio.sleep(time_left)

    target_choice = None
    target_player = None
    if(sorcière.role.deathPotion):

        message = f"\n\n**Voulez vous utiliser votre potion de mort sur quelqu'un?**\n\n"

        message += f'\n\n**Vous avez {int(constant.TIME_FOR_SORCIERE/2)} secondes pour effectuer cette action**\n\n'

        await sorcière.private_channel.send(message)

        targets_choice = await vote(channel=sorcière.private_channel, target_players=bot.ALIVE_PLAYERS, voters=[sorcière], emoji="👎", time=int(constant.TIME_FOR_SORCIERE/2))

        # warn of the choice
        if(len(targets_choice) == 0):
            await sorcière.private_channel.send("\n**vous n'avez pas pas utiliser votre potion de mort**\n")
        elif(len(targets_choice) == 1):
            target_choice = targets_choice[0]
            target_player = target_choice.player
            await sorcière.private_channel.send(f'\n**votre choix est fait, vous avez choisi de tuer cette personne: {target_player}**\n')
            # sorcière.role.target_choice = None
    else:
        time_left = int(constant.TIME_FOR_SORCIERE/2)
        await sorcière.private_channel.send(f"Vous avez déjà utilisé votre potion de mort, attendez {time_left} secondes la fin de votre tour")
        await asyncio.sleep(time_left)

    return target_player
