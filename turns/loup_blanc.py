import discord
from discord.ext import commands
import asyncio
import constant
from data_struct.bot import Bot
from data_struct.roles import LoupBlanc
from vote import vote

bot = Bot()


async def loup_blanc_turn():
    # warn village
    await bot.HISTORY_TEXT_CHANNEL.send(f'\n\n**Le loup blanc a {constant.TIME_FOR_LOUP_BLANC} secondes pour choisir une victime parmi les loups ou non**\n\n')

    # search loup blanc
    loupBlanc = None
    for player in bot.LOUPS:
        if(isinstance(player.role, LoupBlanc)):
            loupBlanc = player
            break

    if(loupBlanc == None):
        print("error in loup_blanc_turn: loupBlanc = None")
        raise ValueError

    await loupBlanc.private_channel.send(f'\n\n**Vous avez {constant.TIME_FOR_LOUP_BLANC} secondes pour choisir une victime parmi les loups ou aucune victime**\n\n')

    target_choice = None
    target_player = None
    if(len(bot.LOUPS) == 1):
        await loupBlanc.private_channel.send("Tous les autres loups sont déjà morts")
    else:
        targets_choice = await vote(channel=loupBlanc.private_channel, target_players=bot.LOUPS, voters=[loupBlanc], emoji="👎", time=constant.TIME_FOR_LOUP_BLANC)

        # warn of the choice
        if(len(targets_choice) == 0):
            await loupBlanc.private_channel.send(f"\n**Vous n'avez pas tuer de loup cette nuit**\n")
        elif(len(targets_choice) == 1):
            target_choice = targets_choice[0]
            target_player = target_choice.player
            await loupBlanc.private_channel.send(f'\n**votre choix est fait, vous avez choisi de tuer cette personne: {target_player}**\n')

    return target_player
