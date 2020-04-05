from data_struct.bot import Bot
from discord.ext import commands
import random
import asyncio
from data_struct.roles import *

from turns.voyantes import voyantes_turn
from turns.cupidon import cupidon_turn
from turns.loups import loups_turn
from turns.loup_blanc import loup_blanc_turn
from turns.sorcières import sorcières_turn
from turns.chasseur import chasseur_turn
from turns.election import election
from turns.lynchage import lynch
from turns.mayor import mayor_give_up
from turns.salvateur import salvateur_turn

from channels_process import delete_game_category


import constant
bot = Bot()


async def game_process(ctx):

    await bot.HISTORY_TEXT_CHANNEL.send(
        f'\n\n**Vous avez {constant.TIME_FOR_ROLES_REVEAL} secondes pour regarder vos rôles avant que la partie commence**\n\n')
    bot.TURN = "ROLES"
    # wait the time that the people check their roles
    await asyncio.sleep(constant.TIME_FOR_ROLES_REVEAL)

    # while(not someone win or draw)
    while(True):
        await asyncio.sleep(constant.TIME_BETWEEN_TURNS)
        await bot.HISTORY_TEXT_CHANNEL.send(f'la nuit **{bot.NB_NIGHTS}** tombe')
        await asyncio.sleep(constant.TIME_BETWEEN_TURNS)

        # cupidon's turn
        # only for the first night
        if(bot.NB_NIGHTS == 1):
            if(Cupidon.nb > 0):
                bot.AMOUREUX = (await cupidon_turn())[:]

        # voyante's turn
        if(await still_something(Voyante)):
            await voyantes_turn()

        salvateur_target_player = None
        # salvateur's turn
        if(Salvateur.nb > 0):
            if(await still_something(Salvateur)):
                salvateur_target_player = await salvateur_turn()

        # TODO : do a gather to make the above roles play at the same time

        await asyncio.sleep(constant.TIME_BETWEEN_TURNS)

        ### wake loups ###
        # for the moment but TODO: replace this by a local variable that you send to the loupBlanc and then the sorcière
        if(await still_something(LoupGarou)):
            target = await loups_turn()
            # if the target is not the salvateur's one then we add the target to kill it
            if(target != salvateur_target_player):
                bot.LOUP_FINAL_TARGET = target
            # else the loups' target is None beacause the salvateur saved the target
            else:
                bot.LOUP_FINAL_TARGET = None

        await asyncio.sleep(constant.TIME_BETWEEN_TURNS)

        ### wake loup blanc ###
        if(bot.NB_NIGHTS % 2 == 0):
            if(LoupBlanc.nb > 0):
                if(await still_something(LoupBlanc)):
                    target = await loup_blanc_turn()
                    # add the kill if there is one
                    if(target != None):
                        bot.DEADS_OF_NIGHT.append(target)

        await asyncio.sleep(constant.TIME_BETWEEN_TURNS)

        ### wake sorcière ###
        sorcières_targets = []
        if(await still_something(Sorcière)):
            sorcières_targets = (await sorcières_turn())[:]

        await asyncio.sleep(constant.TIME_BETWEEN_TURNS)

        ### wake villageois ###
        await bot.HISTORY_TEXT_CHANNEL.send('\n\n**Le village se réveille**\n\n')
        bot.TURN = "DAY"

        ### compute deads over night ###
        if(bot.LOUP_FINAL_TARGET != None):
            bot.DEADS_OF_NIGHT.append(bot.LOUP_FINAL_TARGET)
            # the loup final_target can be reset to None
            bot.LOUP_FINAL_TARGET = None

        # if a sorciere killed add this kill to the deads of night
        for target in sorcières_targets:
            bot.DEADS_OF_NIGHT.append(target)

        ### display the night deads ###
        message = ""
        if(len(bot.DEADS_OF_NIGHT) == 0):
            message += "\n\n**personne n'est mort ce soir**\n\n"
        else:
            for player in bot.DEADS_OF_NIGHT:
                if(player not in bot.DEADS):
                    message += f"\n**{player}** est mort ce soir, son role : {player.role.emoji} **{player.role}**\n"
                    # now put it in the table for all the deads
                    bot.DEADS.append(player)
                    # remove the dead from the alive player table
                    bot.ALIVE_PLAYERS.remove(player)
        bot.DEADS_OF_NIGHT.clear()
        await bot.HISTORY_TEXT_CHANNEL.send(message)

        await asyncio.sleep(constant.TIME_BETWEEN_TURNS)

        # TODO: remove the permissions to write in history text channel of the deads : do this in a function that you are gonna paste multiple times

        await check_amoureux()

        await asyncio.sleep(constant.TIME_BETWEEN_TURNS)

        ### check someone wins or draw ###
        # check if only one player left
        print("check_win")
        print(await check_win())
        if(await check_win()):
            break

        # chasseur if killed then kill someone:
        await check_chasseur()

        await asyncio.sleep(constant.TIME_BETWEEN_TURNS)

        await check_amoureux()

        await asyncio.sleep(constant.TIME_BETWEEN_TURNS)

        ### check someone wins or draw ###
        # check if only one player left
        print("check_win")
        print(await check_win())
        if(await check_win()):
            break

        # if mayor killed, give his mayorship
        for player in bot.DEADS:
            if(player == bot.MAYOR):
                bot.MAYOR = await mayor_give_up(bot.MAYOR)
                break

        ### display deads ###
        message = "\n**morts:**\n"
        for player in bot.DEADS:
            message += f"**{player}**: {player.role.emoji} {player.role} \n"

        ### display alive ###
        message += "\n**vivants:**\n"
        for player in bot.ALIVE_PLAYERS:
            message += f"**{player}**\n"

        ### display roles in games ###
        message += "\n**roles restants:**\n"
        roles = [player.role for player in bot.ALIVE_PLAYERS]
        random.shuffle(roles)
        for role in roles:
            message += f'{role.emoji} **{role}** \n'
        message += '\n'
        await bot.HISTORY_TEXT_CHANNEL.send(message)

        await asyncio.sleep(constant.TIME_BETWEEN_TURNS)

        ### vote for maire ###
        if(bot.MAYOR == None):
            # result
            bot.MAYOR = await election()
            # warn players of the choice
            await bot.HISTORY_TEXT_CHANNEL.send(f'\n\nVotre choix est fait, le maire est **{bot.MAYOR}**\n\n')
            await asyncio.sleep(1)
        else:
            await bot.HISTORY_TEXT_CHANNEL.send(f'\n\nMaire: **{bot.MAYOR}** \n')

        await asyncio.sleep(constant.TIME_BETWEEN_TURNS)

        ### vote for day kill ###
        victim = await lynch()

        ### compute dead of the day ###
        # if(bot.VICTIM != None):
        if(victim != None):
            # bot.DEADS_OF_DAY.append(bot.VICTIM)
            bot.DEADS_OF_DAY.append(victim)
            # bot.VICTIM can be reset to None
            #bot.VICTIM = None

        await asyncio.sleep(constant.TIME_BETWEEN_TURNS)

        if(await check_ange_win(bot.DEADS_OF_DAY)):
            break

        ### display kill of the day ###
        message = ""
        if(len(bot.DEADS_OF_DAY) == 0):
            message += "\n\n**personne n'est mort**\n"
        else:
            for player in bot.DEADS_OF_DAY:
                if(player not in bot.DEADS):
                    message += f"\n**{player}** est mort aujourd'hui, son role : {player.role.emoji} **{player.role}**\n"
                    # now put it in the table for all the deads
                    bot.DEADS.append(player)
                    # remove the dead from the alive player table
                    bot.ALIVE_PLAYERS.remove(player)
        bot.DEADS_OF_DAY.clear()
        await bot.HISTORY_TEXT_CHANNEL.send(message)

        await asyncio.sleep(constant.TIME_BETWEEN_TURNS)

        await check_amoureux()

        await asyncio.sleep(constant.TIME_BETWEEN_TURNS)

        # chasseur if killed then kill someone:
        await check_chasseur()

        await asyncio.sleep(constant.TIME_BETWEEN_TURNS)

        ### check amoureux ###
        await check_amoureux()

        await asyncio.sleep(constant.TIME_BETWEEN_TURNS)

        ### check if village wins or lovers or loups ###
        print("check_win")
        print(await check_win())
        if(await check_win()):
            break

        # if mayor killed, give his mayorship
        for player in bot.DEADS:
            if(player == bot.MAYOR):
                bot.MAYOR = await mayor_give_up(bot.MAYOR)
                break

        ### remove loups that have been killed from the loups table ###
        for player in bot.DEADS:
            if(player in bot.LOUPS):
                bot.LOUPS.remove(player)

        bot.NB_NIGHTS += 1

    ### display winners ###
    message = f"\n\n**Vainqueur(s) après la nuit {bot.NB_NIGHTS}: {bot.WINNER}**\n\n"
    message += f"\n\n**Les channels vont s'auto-détruire dans {constant.TIME_AUTO_DESTRUCT} secondes**\n\n"
    await bot.HISTORY_TEXT_CHANNEL.send(message)

    await asyncio.sleep(constant.TIME_AUTO_DESTRUCT)
    await stop_game(ctx)


async def stop_game(ctx):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie en cours')
        return

    await bot.BEGINNING_CHANNEL.send('arret de la partie en cours')
    await delete_game_category(ctx)
    bot.default_values(bot)


async def check_amoureux():
    # check if amoureux in deads
    for player in bot.DEADS:
        if(player in bot.AMOUREUX):
            bot.AMOUREUX.remove(player)
            message = f"\n**{player}** était amoureux avec : **{bot.AMOUREUX[0]}**"
            message += f"\n**{bot.AMOUREUX[0]}** est donc également mort, son role : {bot.AMOUREUX[0].role.emoji} **{bot.AMOUREUX[0].role}**\n"
            await bot.HISTORY_TEXT_CHANNEL.send(message)
            bot.DEADS.append(bot.AMOUREUX[0])
            bot.ALIVE_PLAYERS.remove(bot.AMOUREUX[0])
            bot.AMOUREUX.clear()
            break


async def check_chasseur():
    for player in bot.DEADS:
        if(isinstance(player.role, Chasseur)):
            target = await chasseur_turn(player)
            if(target != None):
                bot.DEADS.append(target)
                bot.ALIVE_PLAYERS.remove(target)
                break


async def still_something(check_class):
    # check if no more loup in game
    still = False
    for player in bot.ALIVE_PLAYERS:
        if(isinstance(player.role, check_class)):
            still = True
            break
    return still


async def check_ange_win(table_deads_of_day):
    if(len(table_deads_of_day) == 1 and isinstance(table_deads_of_day[0].role, Ange)):
        bot.WINNER = "Ange"
        return True
    return False


async def check_win():

    still_loups = await still_something(LoupGarou)
    still_loups_blanc = await still_something(LoupBlanc)
    still_villageois = await still_something(Villageois)
    still_people = await still_something(Role)

    if(len(bot.ALIVE_PLAYERS) == 1):
        bot.WINNER = bot.ALIVE_PLAYERS[0].role
        return True
    elif(len(bot.ALIVE_PLAYERS) == 2 and bot.ALIVE_PLAYERS[0] in bot.AMOUREUX and bot.ALIVE_PLAYERS[0] in bot.AMOUREUX):
        bot.WINNER = "Amoureux"
        return True
    elif(not still_loups):
        # TODO: change this in funct of roles
        bot.WINNER = "Villageois"
        return True
    elif(not still_villageois and not still_loups_blanc):
        # TODO: if lovers only left then lovers win
        bot.WINNER = "Loups Garous"
        return True
    elif(not still_people):
        bot.WINNER = "Dieus"
        return True

    return False
