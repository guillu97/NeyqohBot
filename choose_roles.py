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

    while(bot.GAME_STARTED != True):
        #print("check roles running")
        #print(bot.GAME_STARTED)
        two_messages_found = 0
        # check the people that have added an emoji to the message
        async for message in channel.history(limit=30):
            nb_to_change = 0 # add +1 or -1
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
                        break
                    users = reaction.users()
                    users = await users.flatten()
                    #if(len(users) == 2): # bot + master_of_game reactions
                    master = None
                    for user in users:
                        if(user.bot == True):
                            break
                        if(not discord.utils.get(user.roles, name=constant.MASTER_OF_THE_GAME)):
                            print(
                                "user == bot or user not game")
                            await reaction.remove(user)
                            break
                        master = user
                    if(master != None):
                        for role in possible_roles:
                            if(role.emoji == reaction.emoji):
                                role.__class__.nb += nb_to_change
                                content = await calc_roles(verbose=True)
                                await reaction.remove(master)
                                if(content != old_content):
                                    await roles_msg.edit(content=content)
                                    old_content = content
                                break
                            
            if(two_messages_found == 2): # no need to search through the other messages
                break
        for role in possible_roles:
            print(str(role) + str(role.__class__.nb))
        # need to sleep at least a bit because otherwise we cannot cancel the task
        # await asyncio.sleep(1)
        await asyncio.sleep(0.5)

    return bot.PLAYERS


# this will await bot.GAME_STARTED == True
async def choose_roles(channel):
    await asyncio.sleep(1)
    
    roles_msg = await channel.send(await calc_roles(verbose=True))

    add_msg = await channel.send("**Ajouter**")
    for role in roles.IMPLEMENTED_ROLES:
        await add_msg.add_reaction(emoji=role.emoji)

    remove_msg = await channel.send("**Enlever**")
    for role in roles.IMPLEMENTED_ROLES:
        await remove_msg.add_reaction(emoji=role.emoji)

    possible_roles = ""
    for role in roles.IMPLEMENTED_ROLES:
        possible_roles += f"{role.emoji} " + str(role) + "  |  "
    await channel.send("\n" + possible_roles)


    

    if(bot.GAME_STARTED == False):
        await check_roles(channel=channel,roles_msg=roles_msg, add_msg=add_msg, remove_msg=remove_msg, possible_roles=roles.IMPLEMENTED_ROLES)
    else:
        print("in vote: bot.GAME_STARTED was already True so why are you waiting for it : maybe change this")
        raise Exception
