import discord
from discord.ext import commands
import random
import constant
from data_struct.roles import *
from data_struct import roles
from data_struct.bot import Bot

bot = Bot()


async def calc_roles(verbose):

    nb_players = len(bot.PLAYERS)

    """
    if(LoupGarou.nb < nb_players or bot.ALLOW_MORE_ROLES == True):
        nb_loup = LoupGarou.nb
    else:
        nb_loup = int(nb_players/4)
        if nb_loup == 0:
            nb_loup = 1

    LoupGarou.nb = nb_loup
    """

    """
    nb_villageois = nb_players
    for role in roles.IMPLEMENTED_ROLES:
        nb_villageois -= role.__class__.nb


    SimpleVillageois.nb = nb_villageois
    

    if(nb_villageois < 0):
        print('nb_villageois < 0')
        # raise ValueError
    """

    roles_list = []

    for role in roles.IMPLEMENTED_ROLES:
        roles_list.extend([role.__class__() for _ in range(role.__class__.nb)])

    message = "\n"
    if(verbose):
        count = 0
        for role in roles.IMPLEMENTED_ROLES:
            if(role.__class__.nb < 0):
                role.__class__.nb = 0
            message += f"**| {role.__class__.emoji} {role}: {role.__class__.nb}**   "
            if(count % 2 == 0):
                message += "\n"
            count += 1

        if(len(roles_list) < nb_players):
            print('nb_roles < nb_players')
            message += '\n**Le nombre de roles est inférieur au nombre de joueurs dans la partie**\n'
        elif(not bot.ALLOW_MORE_ROLES and len(roles_list) > nb_players):
            print('nb_roles > nb_players')
            message += '\n**Le nombre de roles est supérieur au nombre de joueurs dans la partie**\n'

        message += f'\n**nombre de roles: {len(roles_list)}**\n'

        tempRoles = list(set(roles_list))
        for role in tempRoles:
            message += f"{role.emoji} {role} {role.nb} | "

        return message
    else:
        if(len(roles_list) < nb_players):
            print('nb_roles < nb_players')
            return False
        if(not bot.ALLOW_MORE_ROLES and len(roles_list) > nb_players):
            print('nb_roles > nb_players')
            return None
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
            # all players are now alive
            bot.ALIVE_PLAYERS.append(player)
