import asyncio
from discord import Emoji
from data_struct.target import TargetEmoji
from data_struct.bot import Bot
from data_struct.player import Player
from roles_compute import calc_roles
import constant

bot = Bot()


async def check_players(channel, joining_msg, players_msg, emoji):
    # check nb reactions per player
    # => should be 0 at the beginning
    # => to be sure => remove all reactions except from me

    # players = []  # a list of discord Member of the users
    players_discord = []

    # clear reactions to be sure that there aren't any first
    msg_id = joining_msg.id
    async for message in channel.history(limit=100):
        if message.id == msg_id:
            if(len(message.reactions) != 1):
                await message.clear_reactions()
                await message.add_reaction(emoji=emoji)
                break

    while(bot.ROLES_CHOOSEN != True):
        print("check running")
        print(bot.GAME_STARTED)
        # check the people that have added an emoji to the message
        async for message in channel.history(limit=100):
            if(message.id == msg_id):
                for reaction in message.reactions:
                    # if not the good emoji => then delete
                    if(reaction.emoji != emoji):
                        await reaction.clear()
                    else:
                        users = reaction.users()
                        users = await users.flatten()
                        players_discord = [
                            user for user in users if user.bot == False]
                        # from discord Members to Players obj
                        bot.PLAYERS = [Player(user)
                                       for user in players_discord]
                        await players_msg.edit(content=str(f'joueurs: {" ".join(map(str,bot.PLAYERS))}\n'))
                break
        # need to sleep at least a bit because otherwise we cannot cancel the task
        # await asyncio.sleep(1)
        await asyncio.sleep(0.01)

    return bot.PLAYERS


# this will await bot.ROLES_CHOOSEN == True
async def choose_roles(channel):
    await channel.send(f'\n\n**Le maitre du jeu choisit les roles**')
    roles = await calc_roles(verbose=True)
    roles_msg = await channel.send(roles)

    for role in constant.IMPLEMENTED_ROLES:
        await roles_msg.add_reaction(emoji=role.emoji)

    if(bot.ROLES_CHOOSEN == False):
        await check_players(channel=channel, joining_msg=roles_msg, players_msg=players_msg, emoji=emoji)
    else:
        print("in vote: bot.ROLES_CHOOSEN was already True so why are you waiting for it : maybe change this")
        raise Exception
