import asyncio
import discord
from discord import Emoji
from data_struct.target import TargetEmoji
from data_struct.bot import Bot
from data_struct.player import Player
from data_struct.roles import *
from data_struct import roles
from roles_compute import calc_roles
import constant

bot = Bot()


async def check_roles(channel, roles_msg, add_msg, remove_msg, possible_roles):

    emojis = [role.emoji for role in possible_roles]

    old_content = ""

    time_between_loops = 0.1
    while(bot.GAME_STARTED != True):

        #print("check roles running")
        # print(bot.GAME_STARTED)
        two_messages_found = 0
        # check the people that have added an emoji to the message
        async for message in channel.history(limit=30):
            nb_to_change = 0  # add +1 or -1
            if(message.id == add_msg.id):
                nb_to_change = 1
                two_messages_found += 1
            elif(message.id == remove_msg.id):
                nb_to_change = -1
                two_messages_found += 1

            if(message.id == add_msg.id or message.id == remove_msg.id):
                for reaction in message.reactions:
                    if(reaction.emoji not in emojis):
                        # if not the good emoji => then delete
                        await reaction.clear()
                        continue
                    users = reaction.users()
                    users = await users.flatten()
                    # if(len(users) == 2): # bot + master_of_game reactions
                    master = None
                    for user in users:
                        if(user.bot == True):
                            continue
                        if(not discord.utils.get(user.roles, name=constant.MASTER_OF_THE_GAME)):
                            print(
                                "user == bot or user not game")
                            await reaction.remove(user)
                            continue
                        master = user
                    if(master != None):
                        index = emojis.index(reaction.emoji)
                        if(index < 0 or index >= len(emojis)):
                            print(f'bad emoji index in check roles : {index}')
                            raise IndexError
                        role = possible_roles[index]
                        if(nb_to_change == 1):
                            if(role.__class__.nb + 1 <= role.__class__.nb_max):
                                role.__class__.nb += nb_to_change
                                content = await calc_roles(verbose=True)
                        else:
                            role.__class__.nb += nb_to_change
                            content = await calc_roles(verbose=True)
                        await reaction.remove(master)
                        if(content != old_content):
                            await roles_msg.edit(content=content)
                            old_content = content

            if(two_messages_found == 2):  # no need to search through the other messages
                break
        """for role in possible_roles:
            print(str(role) + str(role.__class__.nb))"""
        # need to sleep at least a bit because otherwise we cannot cancel the task
        # await asyncio.sleep(1)
        await asyncio.sleep(time_between_loops)

    return bot.PLAYERS


# this will await bot.GAME_STARTED == True
async def choose_roles(channel):
    await asyncio.sleep(1)

    if(len(bot.PLAYERS) < constant.MINIMUM_PLAYER_NB):
        msg = await channel.send(f"**Nombre de joueurs inférieur au nombre de joueurs minimum : {constant.MINIMUM_PLAYER_NB}**")
        while(len(bot.PLAYERS) < constant.MINIMUM_PLAYER_NB):
            await asyncio.sleep(1)
        await msg.delete()

    add_msg = await channel.send("**\nAjouter**")
    remove_msg = await channel.send("**Enlever**")
    roles_msg = await channel.send(await calc_roles(verbose=True))

    tasks = []
    for role in roles.IMPLEMENTED_ROLES:
        tasks.append(add_msg.add_reaction(emoji=role.emoji))
        tasks.append(remove_msg.add_reaction(emoji=role.emoji))

    await asyncio.gather(*tasks)

    # if(bot.GAME_STARTED == False):
    await check_roles(channel=channel, roles_msg=roles_msg, add_msg=add_msg, remove_msg=remove_msg, possible_roles=roles.IMPLEMENTED_ROLES)
    # else:
    #    print("in vote: bot.GAME_STARTED was already True so why are you waiting for it : maybe change this")
    #    #raise Exception
