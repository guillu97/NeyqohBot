import discord
from discord.ext import commands
import asyncio
import constant
from data_struct.bot import Bot
from data_struct.target import Target
from turns.mayor import mayor_choice

bot = Bot()


async def lynch():
    # find the target:
    # print(bot.LOUP_TARGETS)
    targets_choice = []

    ### warn village ###
    message = f'\n\n**Les villageois ont {constant.TIME_FOR_VICTIM_ELECTION} secondes pour choisir la victime du jour:**\n\n'
    bot.TURN = "VICTIME_ELECTION"

    ### vote ###

    time_left = constant.TIME_FOR_VICTIM_ELECTION

    num = 0
    for player in bot.ALIVE_PLAYERS:
        message += f'{num}:  {player}\n'
        num += 1
    message += '\ncommande: !vote <int>\n'
    message += 'exemple: !vote 5\n'
    await bot.HISTORY_TEXT_CHANNEL.send(message)

    await asyncio.sleep(time_left - 30)
    time_left = 30
    await bot.HISTORY_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
    await asyncio.sleep(time_left - 20)
    time_left = 20
    await bot.HISTORY_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
    await asyncio.sleep(time_left - 10)
    time_left = 10
    await bot.HISTORY_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
    await asyncio.sleep(time_left - 5)
    time_left = 5
    await bot.HISTORY_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
    await asyncio.sleep(time_left)

    # if no target
    if(len(bot.VICTIM_TARGETS) == 0):
        # no mayor choice from the players
        await bot.HISTORY_TEXT_CHANNEL.send("\n**Vous n'avez pas choisi de victime, le maire va choisir**\n")
    else:
        targets_choice.clear()
        max_accusator = max([len(target.accusators)
                             for target in bot.VICTIM_TARGETS])
        targets_choice = [target for target in bot.VICTIM_TARGETS if len(
            target.accusators) == max_accusator]

    bot.VICTIM_TARGETS.clear()

    target_choice = None
    # draw for the votes if equality
    if(len(targets_choice) > 1):
        # choose the target where the mayor is in accusators
        for victim_target in targets_choice:
            if(bot.MAYOR in victim_target.accusators):
                target_choice = victim_target.player
                break
    elif(len(targets_choice) == 1):
        target_choice = targets_choice[0].player

    elif(len(targets_choice) == 0):  # if no target at all
        num = 0
        # add all the alive players as targets for the mayor to choose
        for player in bot.ALIVE_PLAYERS:
            targets_choice.append(Target(actual_num=num, player=player))
            num += 1

    # else:
    # print(target_choice)
    # print(len(target_choice))
    # print("error in lynch: not len(targets_choice) > 1, not len(targets_choice) == 1")
    # raise Exception

    # if target_choice is still None then the mayor need to choose the victim
    if(target_choice == None):
        bot.MAYOR_ONLY_CHOICES = targets_choice
        target_choice = await mayor_choice()
        bot.MAYOR_ONLY_CHOICES.clear()

    bot.TURN = "FIN_VICTIME_ELECTION"

    # results
    # warn players of the choice
    await bot.HISTORY_TEXT_CHANNEL.send(f'votre choix est fait, vous avez choisi {target_choice}')
    await asyncio.sleep(1)
    bot.VICTIM = target_choice
    bot.VICTIM_TARGETS.clear()
