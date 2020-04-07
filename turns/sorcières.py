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

    # show the victim of the loups
    if(bot.LOUP_FINAL_TARGET != None):
        await sorcière.private_channel.send(f"Cette personne est morte ce soir: **{bot.LOUP_FINAL_TARGET}**")

    if(sorcière.role.lifePotion):
        if(bot.LOUP_FINAL_TARGET):

            await sorcière.private_channel.send('Voulez vous sauver cette personne?')

            targets_choice = await vote(channel=sorcière.private_channel, target_players=[bot.LOUP_FINAL_TARGET], voters=[sorcière], emoji="👍", time=int(constant.TIME_FOR_SORCIERE/2))

            # warn of the choice
            if(len(targets_choice) == 0):
                await sorcière.private_channel.send("**vous n'avez pas choisi de sauver cette personne**")
            elif(len(targets_choice) == 1):
                await sorcière.private_channel.send(f'**votre choix est fait, vous avez choisi de sauver cette personne: {bot.LOUP_FINAL_TARGET}**')
                bot.LOUP_FINAL_TARGET = None
                sorcière.role.lifePotion = False
        else:
            await sorcière.private_channel.send("**Personne n'est mort ce soir**")
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

        message = f"**Voulez vous utiliser votre potion de mort sur quelqu'un?**\n"

        message += f'**Vous avez {int(constant.TIME_FOR_SORCIERE/2)} secondes pour effectuer cette action**'

        await sorcière.private_channel.send(message)

        targets_choice = await vote(channel=sorcière.private_channel, target_players=bot.ALIVE_PLAYERS, voters=[sorcière], emoji="👎", time=int(constant.TIME_FOR_SORCIERE/2))

        # warn of the choice
        if(len(targets_choice) == 0):
            await sorcière.private_channel.send("**vous n'avez pas pas utiliser votre potion de mort**")
        elif(len(targets_choice) == 1):
            target_choice = targets_choice[0]
            target_player = target_choice.player
            await sorcière.private_channel.send(f'**votre choix est fait, vous avez choisi de tuer cette personne: {target_player}**')
            # sorcière.role.target_choice = None
    else:
        time_left = int(constant.TIME_FOR_SORCIERE/2)
        await sorcière.private_channel.send(f"Vous avez déjà utilisé votre potion de mort, attendez {time_left} secondes la fin de votre tour")
        await asyncio.sleep(time_left)

    return target_player
