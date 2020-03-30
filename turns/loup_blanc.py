import discord
from discord.ext import commands
import asyncio
import constant
from data_struct.singleton import Singleton

bot = Singleton()

async def loup_blanc_turn():
    # warn village
    await bot.HISTORY_TEXT_CHANNEL.send(f'\n\n**Le loup blanc a {constant.TIME_FOR_LOUP_BLANC} secondes pour choisir une victime parmi les loups ou non**\n\n')

    # search loup blanc
    loupBlanc = None
    for player in bot.ALIVE_PLAYERS:
        if(isinstance(player.role, LoupBlanc)):
            loupBlanc = player
            break

    if(loupBlanc == None):
        print("error in loup_blanc_turn: loupBlanc = None")
        raise ValueError

    await loupBlanc.private_channel.send(f'\n\n**Vous avez {constant.TIME_FOR_LOUP_BLANC} secondes pour choisir une victime parmi les loups ou non**\n\n')
    message = ""
    num = 0
    targets = [player for player in bot.LOUPS if(
        not isinstance(player.role, LoupBlanc))]
    print(targets)
    for player in targets:
        print(player)
    if(len(targets) > 0):
        bot.TURN = "LOUP_BLANC"
        for player in targets:
            message += f'{num}:  {player}\n'
            num += 1
        message += '\ncommande: !vote <int>\n'
        message += 'exemple: !vote 5\n'
        message += '\n\n**si vous ne votez pas, vous ne tuerez aucun loup cette nuit**\n\n'
    else:
        message += "\n\n**Tous les loups sont dejà morts, attendez la fin de votre tour**\n\n"
        bot.TURN = "FIN_LOUP_BLANC"
    await loupBlanc.private_channel.send(message)

    time_left = int(constant.TIME_FOR_LOUP_BLANC)
    await asyncio.sleep(time_left - 5)
    time_left = 5
    await loupBlanc.private_channel.send(f'{time_left} secondes restantes')
    await asyncio.sleep(time_left)

    bot.TURN = "FIN_LOUP_BLANC"

    # warn of the choice
    if(loupBlanc.role.target_choice != None):
        await loupBlanc.private_channel.send(f'\n**votre choix est fait, vous avez choisi de tuer cette personne: {loupBlanc.role.target_choice}**\n')
    else:
        if(len(targets) > 0):
            await loupBlanc.private_channel.send(f"\n**votre choix est fait, vous n'avez pas tuer de loup cette nuit**\n")
