import discord
from discord.ext import commands
import random
import constant
from data_struct.roles import *
from data_struct.bot import Bot

bot = Bot()


async def calc_roles(verbose):
    if(len(bot.PLAYERS) < constant.MINIMUM_PLAYER_NB):
        nb_players = constant.MINIMUM_PLAYER_NB  
    else:
        nb_players = len(bot.PLAYERS)

    if(LoupGarou.nb < nb_players or bot.ALLOW_MORE_ROLES == True):
        nb_loup = LoupGarou.nb
    else:
        nb_loup = int(nb_players/4)
        if nb_loup == 0:
            nb_loup = 1

    roles = []

    for _ in range(nb_loup):
        roles.append(LoupGarou())

    # TODO: here add the number of the special roles
    nb_voyante = Voyante.nb
    for _ in range(nb_voyante):
        roles.append(Voyante())

    nb_ange = Ange.nb
    for _ in range(nb_ange):
        roles.append(Ange())

    nb_sorcière = Sorcière.nb
    for _ in range(nb_sorcière):
        roles.append(Sorcière())

    nb_chasseur = Chasseur.nb
    for _ in range(nb_chasseur):
        roles.append(Chasseur())

    nb_cupidon = Cupidon.nb
    for _ in range(nb_cupidon):
        roles.append(Cupidon())

    nb_loupBlanc = LoupBlanc.nb
    for _ in range(nb_loupBlanc):
        roles.append(LoupBlanc())

    # TODO: Here add the substraction of the nb of special role
    nb_villageois = nb_players - nb_loup - nb_voyante - \
        nb_ange - nb_sorcière - nb_chasseur - nb_cupidon - nb_loupBlanc
    

    if(nb_villageois < 0):
        print('nb_villageois < 0')
        # raise ValueError

    for _ in range(nb_villageois):
        roles.append(Villageois())

    message = ""
    if(not bot.ALLOW_MORE_ROLES):
        if(len(roles) > nb_players):
            print('nb_roles > nb_players')
            if(verbose):
                message += '\n**nombre de roles supérieur au nombre de joueurs dans la partie**\n\n'
            else:
                return None

    Villageois.nb = nb_villageois

    if(verbose):
        message += f"**nombre de joueurs :** {nb_players}\n"

        if(nb_villageois != 0):
            message += f"**villageois:** {nb_villageois}\n"
        if(nb_loup != 0):
            message += f"**loups :** {nb_loup}\n"
        # TODO: add here for the special roles
        if(nb_loupBlanc != 0):
            message += f"**loup blanc:** {nb_loupBlanc}\n"
        if(nb_cupidon != 0):
            message += f'**cupidon:** {nb_cupidon}\n'
        if(nb_voyante != 0):
            message += f"**voyante:** {nb_voyante}\n"
        if(nb_sorcière != 0):
            message += f'**sorcière:** {nb_sorcière}\n'
        if(nb_ange != 0):
            message += f"**ange:** {nb_ange}\n"
        if(nb_chasseur != 0):
            message += f'**chasseur:** {nb_chasseur}\n'

        return message
    else:
        return roles


async def assign_roles():

    roles = await calc_roles(verbose=False)

    bot.LOUPS.clear()
    bot.ALIVE_PLAYERS.clear()

    if(bot.ALLOW_MORE_ROLES):
        at_least_one_loup = False
        while(at_least_one_loup == False):
            random.shuffle(roles)
            for player, role in zip(bot.PLAYERS, roles):
                player.role = role
                if(isinstance(role, LoupGarou)):
                    bot.LOUPS.append(player)
                    at_least_one_loup = True
                # all players are now alive
                bot.ALIVE_PLAYERS.append(player)
    else:
        random.shuffle(bot.PLAYERS)
        for player, role in zip(bot.PLAYERS, roles):
            player.role = role
            if(isinstance(role, LoupGarou)):
                bot.LOUPS.append(player)
                at_least_one_loup = True
            # all players are now alive
            bot.ALIVE_PLAYERS.append(player)
