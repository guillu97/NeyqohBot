import discord
from discord.ext import commands
import asyncio
import random
import constant
from data_struct.bot import Bot
from data_struct.target import Target
from turns.mayor import mayor_choice

from vote import vote

bot = Bot()


async def lynch():
    ### warn village ###
    await bot.HISTORY_TEXT_CHANNEL.send(f'\n\n**Les villageois ont {constant.TIME_FOR_VICTIM_ELECTION} secondes pour choisir la victime du jour:**\n\n')

    ### vote ###
    targets_choice = await vote(channel=bot.HISTORY_TEXT_CHANNEL, target_players=bot.ALIVE_PLAYERS, voters=bot.ALIVE_PLAYERS, emoji="👎", time=constant.TIME_FOR_VICTIM_ELECTION)

    target_choice = None
    target_player = None
    if(len(targets_choice) == 1):
        target_choice = targets_choice[0]
        target_player = target_choice.player
        await bot.HISTORY_TEXT_CHANNEL.send(f'**{target_choice.nb_accusators()}** votes pour **{target_choice.player}**: | *{"* | *".join(map(str,target_choice.accusators))}* |')
    elif(len(targets_choice) > 1):
        # check if mayor in accusators:
        check_mayor_in = False
        for target in targets_choice:
            for accusator in target.accusators:
                if(accusator == bot.MAYOR):
                    await bot.HISTORY_TEXT_CHANNEL.send("**Le maire a fait pencher la balance**")
                    target_choice = target
                    target_player = target.player
                    await bot.HISTORY_TEXT_CHANNEL.send(f'**{target_choice.nb_accusators()}** votes pour **{target_choice.player}**: | *{"* | *".join(map(str,target_choice.accusators))}* |')
                    check_mayor_in = True
                    break
        if(check_mayor_in == False):
            # if mayor not in accusators then the mayor choose
            await bot.HISTORY_TEXT_CHANNEL.send("**Vous ne vous êtes pas décidés**")
            await asyncio.sleep(1)
            await bot.HISTORY_TEXT_CHANNEL.send(f"Le maire **{bot.MAYOR}** va choisir")

            # choix du maire
            # if multiple choices then targets = all alive players for the mayor to choose from
            if(len(targets_choice) == 0):
                target_players = bot.ALIVE_PLAYERS
            else:
                target_players = [target.player for target in targets_choice]
            targets_choice = await vote(channel=bot.HISTORY_TEXT_CHANNEL, target_players=target_players, voters=[bot.MAYOR], emoji="👎", time=constant.TIME_FOR_MAYOR_FINAL_CHOICE)
            target_choice = None
            if(len(targets_choice) == 1):
                target_choice = targets_choice[0]
                target_player = target_choice.player
                await bot.HISTORY_TEXT_CHANNEL.send(f'**{target_choice.nb_accusators()}** votes pour **{target_choice.player}**: | *{"* | *".join(map(str,target_choice.accusators))}* |')
            elif(len(targets_choice) == 0):  # if no targets then kill no one
                pass
                #targets_choice = bot.ALIVE_PLAYERS
                #target_choice = random.choice(targets_choice)
                #target_player = target_choice.player
                # await bot.HISTORY_TEXT_CHANNEL.send(f'**Les dieux RNG ont choisi {target_choice.player}**')
            else:
                print(
                    "error mayor has choosen multiple targets for the final choice, it should not be possible")
                raise Exception
                await bot.HISTORY_TEXT_CHANNEL.send(f'**{target_choice.nb_accusators()}** votes pour **{target_choice.player}**: | *{"* | *".join(map(str,target_choice.accusators))}* |')
    elif(len(targets_choice) == 0):  # if no choice made then nobody dies
        await bot.HISTORY_TEXT_CHANNEL.send(f"Vous n'avez pas fait de choix, personne ne va mourrir aujourd'hui")
        await asyncio.sleep(1)

    await asyncio.sleep(1)
    return target_player
