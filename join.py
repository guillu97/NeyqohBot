import asyncio
import discord
from discord import Emoji
from data_struct.target import TargetEmoji
from data_struct.bot import Bot
from data_struct.player import Player
from roles_compute import calc_roles
import constant

bot = Bot()


async def check_start(channel):
    if(bot.GAME_CREATED == False):
        await channel.send('aucune partie créée', delete_after=2)
        return False

    if(len(bot.PLAYERS) < bot.MINIMUM_PLAYER_NB):
        await channel.send(f"le nombre minimum de joueurs ({bot.MINIMUM_PLAYER_NB}) n'est pas atteint", delete_after=2)
        return False

    roles = await calc_roles(verbose=False)
    if(roles == False):
        await channel.send('\n**Le nombre de roles est inférieur au nombre de joueurs**\n', delete_after=2)
        return False

    if(not bot.ALLOW_MORE_ROLES):
        if(roles == None):
            await channel.send('\n**Le nombre de roles est supérieur au nombre de joueurs**\n', delete_after=2)
            return False

    bot.GAME_STARTED = True
    return True


async def check_players(channel, joining_msg, players_msg, emoji_join, emoji_start):
    # check nb reactions per player
    # => should be 0 at the beginning
    # => to be sure => remove all reactions except from me

    # players = []  # a list of discord Member of the users
    players_discord = []
    old_players_discord = []
    # clear reactions to be sure that there aren't any first
    msg_id = joining_msg.id
    async for message in channel.history(limit=30):
        if message.id == msg_id:
            if(len(message.reactions) != 1):
                await message.clear_reactions()
                await message.add_reaction(emoji=emoji_join)
                await message.add_reaction(emoji=emoji_start)
                break

    time_between_loops = 1
    while(bot.GAME_STARTED != True):
        #print("check running")
        # print(bot.GAME_STARTED)
        # check the people that have added an emoji to the message
        async for message in channel.history(limit=30):
            if(message.id == msg_id):
                for reaction in message.reactions:
                    if(reaction.emoji == emoji_start):
                        users = reaction.users()
                        users = await users.flatten()
                        users_discord = [
                            user for user in users if user.bot == False]
                        master = [user for user in users_discord if discord.utils.get(
                            user.roles, name=constant.MASTER_OF_THE_GAME) != None]
                        if(len(master) == 1):
                            if(await check_start(channel)):
                                break
                        for user in users_discord:
                            await reaction.remove(user)
                    # if not the good emoji => then delete
                    if(reaction.emoji != emoji_join and reaction.emoji != emoji_start):
                        await reaction.clear()
                    else:
                        users = reaction.users()
                        users = await users.flatten()
                        players_discord = [
                            user for user in users if user.bot == False]
                        if(len(players_discord) != 0 and players_discord != old_players_discord):
                            # from discord Members to Players obj
                            bot.PLAYERS = [Player(user)
                                           for user in players_discord]
                            await players_msg.edit(content=str(f'joueurs:\n {" ".join(map(str,bot.PLAYERS))} \n**nombre de joueurs :** {len(bot.PLAYERS)}\n'))
                            old_players_discord = players_discord
                break
        # need to sleep at least a bit because otherwise we cannot cancel the task
        # await asyncio.sleep(1)
        await asyncio.sleep(time_between_loops)

    return bot.PLAYERS


# this will fill bot.PLAYERS and await bot.GAME_STARTED == True
async def joining_process(channel, emoji_join, emoji_start):

    join_msg = await channel.send(f'**Ajoutez un {emoji_join} pour rejoindre la partie et appuyer sur {emoji_start} pour commencer la partie**')
    players_msg = await channel.send(f'joueurs: {" | ".join(map(str,bot.PLAYERS))}\n')
    # await join_msg.add_reaction(emoji=emoji)
    # await join_msg.add_reaction(emoji="⚔️")

    # if(bot.GAME_STARTED == False):
    await check_players(channel=channel, joining_msg=join_msg, players_msg=players_msg, emoji_join=emoji_join, emoji_start=emoji_start)
    # else:
    #    print("in join: bot.GAME_STARTED was already True so why are you waiting for it : maybe change this")
    #    #raise Exception
