import discord
from discord.ext import commands
import random
import constant
from data_struct.roles import *
from data_struct import roles
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
    
    LoupGarou.nb = nb_loup

    nb_villageois = nb_players
    for role in roles.IMPLEMENTED_ROLES:
        nb_villageois -= role.__class__.nb

    Villageois.nb = nb_villageois

    if(nb_villageois < 0):
        print('nb_villageois < 0')
        # raise ValueError

    roles_list = []

    for role in roles.IMPLEMENTED_ROLES:
        roles_list.extend([role.__class__() for _ in range(role.__class__.nb)])


    message = ""
    if(not bot.ALLOW_MORE_ROLES):
        if(len(roles_list) > nb_players):
            print('nb_roles > nb_players')
            if(verbose):
                message += '\n**nombre de roles supérieur au nombre de joueurs dans la partie**\n\n'
            else:
                return None

    if(verbose):
        message += f"**nombre de joueurs :** {nb_players}\n"

        for role in roles.IMPLEMENTED_ROLES:
            if(role.__class__.nb > 0):
                message += f"**{role}**: {role.__class__.nb}  |  "
            else:
                role.__class__.nb = 0
        return message
    else:
        return roles_list


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
