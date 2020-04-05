import discord
from discord.ext import commands
import asyncio
import random
import constant
from data_struct.bot import Bot
from vote import vote

bot = Bot()


async def loups_turn():

    # warn village
    await bot.HISTORY_TEXT_CHANNEL.send(f'\n\n**Les loups garous ont {constant.TIME_FOR_LOUPS} secondes pour choisir leur victime de la nuit**\n\n')
    bot.TURN = "LOUPS"

    ### find loups alive ###
    loups_alive = list(set(bot.LOUPS).intersection(bot.ALIVE_PLAYERS))
    # equivalent
    #loups_alive = [loup for loup in bot.LOUPS if loup in bot.ALIVE_PLAYERS]

    # make channel accessible
    for player in loups_alive:
        member = player.discordMember
        # overwrites[member] = discord.PermissionOverwrite(read_messages=True)
        await bot.LOUPS_TEXT_CHANNEL.set_permissions(
            member, send_messages=True, read_messages=True)

    # warn loups garou
    message = f'Vous avez {constant.TIME_FOR_LOUPS} secondes pour choisir votre victime de la nuit\n'
    message += f'Les loups vivants sont : ' + \
        ' ** '.join(map(str, bot.LOUPS)) + '**\n'
    #time_left = constant.TIME_FOR_LOUPS

    # equivalent
    #loups_alive = [loup for loup in bot.LOUPS if loup in bot.ALIVE_PLAYERS]

    ### vote ###
    targets_choice = await vote(channel=bot.LOUPS_TEXT_CHANNEL, target_players=bot.ALIVE_PLAYERS, voters=loups_alive, emoji="👎", time=constant.TIME_FOR_LOUPS)

    target_choice = None
    target_player = None
    if(len(targets_choice) == 1):
        target_choice = targets_choice[0]
        target_player = target_choice.player
        await bot.LOUPS_TEXT_CHANNEL.send(f'**{target_choice.nb_accusators()}** votes pour **{target_choice.player}**: | *{"* | *".join(map(str,target_choice.accusators))}* |')
    elif(len(targets_choice) > 1):
        target_choice = random.choice(targets_choice)
        target_player = target_choice.player
        await bot.LOUPS_TEXT_CHANNEL.send(f'**Les dieux RNG ont choisi {target_choice.player}**')
    elif(len(targets_choice) == 0):  # if no choice made then nobody dies
        await bot.LOUPS_TEXT_CHANNEL.send(f"**Vous n'avez pas fait de choix, personne ne va mourrir aujourd'hui**")

    await asyncio.sleep(1)

    # make channel inacessible
    for player in loups_alive:
        member = player.discordMember
        # overwrites[member] = discord.PermissionOverwrite(read_messages=True)
        await bot.LOUPS_TEXT_CHANNEL.set_permissions(
            member, send_messages=False, read_messages=False)

    return target_player
