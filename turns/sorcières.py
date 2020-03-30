import discord
from discord.ext import commands
import asyncio
import constant
from data_struct.singleton import Singleton

bot = Singleton()

async def sorcières_turn():
    await bot.HISTORY_TEXT_CHANNEL.send(f'La sorcière a {constant.TIME_FOR_SORCIERE} secondes pour choisir ses actions\n\n')

    # find the sorcière
    sorcières = [player for player in bot.ALIVE_PLAYERS if(
        isinstance(player.role, Sorcière))]

    tasks = []
    for sorcière in sorcières:
        tasks.append(asyncio.ensure_future(sorcière_play(sorcière)))
    await asyncio.gather(*tasks)


async def sorcière_play(sorcière):
    """for player in bot.ALIVE_PLAYERS:
        if(isinstance(player.role, Sorcière)):
            sorcière = player
    """

    if(sorcière == None):
        print('sorcière play but no sorcière alive')
        raise Exception

    # show the victim of the loups if still life potion
    if(sorcière.role.lifePotion):
        if(bot.LOUP_FINAL_TARGET):
            message = f'\n\n**{bot.LOUP_FINAL_TARGET}** va mourir ce soir\n\n'

            message += f'\n\n**Voulez vous utiliser votre potion de vie sur cette personne?**\n\n'

            message += f'\n\n**Vous avez {int(constant.TIME_FOR_SORCIERE/2)} secondes pour effectuer cette action**\n\n'

            bot.TURN = "SORCIERE_LIFE"

            num = 0
            message += f'{num}:  {bot.LOUP_FINAL_TARGET}\n'
            message += '\nsi vous voulez sauver cette personne tapez: !vote 0\n'
            message += "\n**sinon ne tapez rien si vous voulez garder votre potion de vie**"

            await sorcière.private_channel.send(message)

            time_left = int(constant.TIME_FOR_SORCIERE/2)
            await asyncio.sleep(time_left - 5)
            time_left = 5
            await sorcière.private_channel.send(f'{time_left} secondes restantes')
            await asyncio.sleep(time_left)

            bot.TURN = "FIN_SORCIERE_LIFE"

            # warn of the choice

            if(sorcière.role.lifePotion == True):
                await sorcière.private_channel.send("\n**vous n'avez pas choisi de sauver cette personne**\n")
            else:
                await sorcière.private_channel.send(f'\n**votre choix est fait, vous avez choisi de sauver cette personne: {bot.LOUP_FINAL_TARGET}**\n')
                bot.LOUP_FINAL_TARGET = None
        else:
            await sorcière.private_channel.send("\n\n**Personne n'est mort ce soir**\n\n")
            time_left = int(constant.TIME_FOR_SORCIERE/2)
            await sorcière.private_channel.send(f"attendez {time_left} secondes pour votre prochaine action")
            await asyncio.sleep(time_left)

    else:
        time_left = int(constant.TIME_FOR_SORCIERE/2)
        await sorcière.private_channel.send(f"attendez {time_left} secondes pour votre prochaine action")
        await asyncio.sleep(time_left)

    if(sorcière.role.deathPotion):

        message = f"\n\n**Voulez vous utiliser votre potion de mort sur quelqu'un?**\n\n"

        message += f'\n\n**Vous avez {int(constant.TIME_FOR_SORCIERE/2)} secondes pour effectuer cette action**\n\n'

        bot.TURN = "SORCIERE_DEATH"

        num = 0
        for player in bot.ALIVE_PLAYERS:
            message += f'{num}:  {player}\n'
            num += 1
        message += '\ncommande: !vote <int>\n'
        message += 'exemple: !vote 5\n'
        message += '**ne votez pas si vous ne voulez pas utiliser votre potion de mort**\n'
        await sorcière.private_channel.send(message)

        time_left = int(constant.TIME_FOR_SORCIERE/2)
        await asyncio.sleep(time_left - 5)
        time_left = 5
        await sorcière.private_channel.send(f'{time_left} secondes restantes')
        await asyncio.sleep(time_left)

        bot.TURN = "FIN_SORCIERE_DEATH"

        # warn of the choice

        if(sorcière.role.deathPotion):
            await sorcière.private_channel.send("\n**vous n'avez pas pas utiliser votre potion de mort**\n")
        else:
            await sorcière.private_channel.send(f'\n**votre choix est fait, vous avez choisi de tuer cette personne: {sorcière.role.target_choice}**\n')
            # sorcière.role.target_choice = None
    else:
        time_left = int(constant.TIME_FOR_SORCIERE/2)
        await asyncio.sleep(time_left)
