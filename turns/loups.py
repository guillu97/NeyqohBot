import discord
from discord.ext import commands
import asyncio
import random
import constant
from data_struct.bot import Bot

bot = Bot()


async def loups_turn():

    # warn village
    await bot.HISTORY_TEXT_CHANNEL.send(f'\n\n**Les loups garous ont {constant.TIME_FOR_LOUPS} secondes pour choisir leur victime de la nuit**\n\n')
    bot.TURN = "LOUPS"

    # make channel accessible
    for player in bot.LOUPS:
        member = player.discordMember
        # overwrites[member] = discord.PermissionOverwrite(read_messages=True)
        await bot.LOUPS_TEXT_CHANNEL.set_permissions(
            member, send_messages=True, read_messages=True)

    # warn loups garou
    message = f'Vous avez {constant.TIME_FOR_LOUPS} secondes pour choisir votre victime de la nuit\n\n'
    time_left = constant.TIME_FOR_LOUPS

    num = 0
    for player in bot.ALIVE_PLAYERS:
        member = player.discordMember
        message += f'{num}:  {member.display_name}\n'
        num += 1
    message += '\ncommande: !vote <int>\n'
    message += 'exemple: !vote 5\n'
    await bot.LOUPS_TEXT_CHANNEL.send(message)

    await asyncio.sleep(time_left - 10)
    time_left = 10
    await bot.LOUPS_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
    await asyncio.sleep(time_left - 5)
    time_left = 5
    await bot.LOUPS_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
    await asyncio.sleep(time_left)

    # find the target:
    print(bot.LOUP_TARGETS)
    # if no target
    if(len(bot.LOUP_TARGETS) == 0):
        # no dead from the loups
        await bot.LOUPS_TEXT_CHANNEL.send("\n**vous n'avez pas choisi de victime**\n")
    else:
        targets_choice = None
        max_accusator = max([len(target.accusators)
                             for target in bot.LOUP_TARGETS])
        targets_choice = [target for target in bot.LOUP_TARGETS if len(
            target.accusators) == max_accusator]

        # draw for the votes
        if(len(targets_choice) > 1):
            # choose the target randomly
            rand_index = random.randint(0, len(targets_choice) - 1)
            target_choice = targets_choice[rand_index].player
        elif(len(targets_choice) == 1):
            target_choice = targets_choice[0].player
        else:
            print(
                "error loups_turn: not len(targets_choice) > 1 ,  not len(targets_choice) == 1")
            raise Exception

        bot.TURN = "FIN_LOUPS"

        # make channel inacessible in write only
        for player in bot.LOUPS:
            member = player.discordMember
            # overwrites[member] = discord.PermissionOverwrite(read_messages=True)
            await bot.LOUPS_TEXT_CHANNEL.set_permissions(
                member, send_messages=False, read_messages=True)

        # warn loups of the choice
        await bot.LOUPS_TEXT_CHANNEL.send(f'**votre choix est fait, vous avez choisi {target_choice}**')
        await asyncio.sleep(1)
        bot.LOUP_FINAL_TARGET = target_choice
        bot.LOUP_TARGETS.clear()

    # make channel inacessible
    for player in bot.LOUPS:
        member = player.discordMember
        # overwrites[member] = discord.PermissionOverwrite(read_messages=True)
        await bot.LOUPS_TEXT_CHANNEL.set_permissions(
            member, send_messages=False, read_messages=False)
