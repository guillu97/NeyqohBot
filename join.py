import asyncio
from discord import Emoji
from data_struct.target import TargetEmoji
from data_struct.bot import Bot
from data_struct.player import Player

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

    while(bot.GAME_STARTED != True):
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


# this will fill bot.PLAYERS and await bot.GAME_STARTED == True
async def joining_process(channel, emoji):

    join_msg = await channel.send(f'\n\n**Ajoutez un {emoji} pour rejoindre la partie**')
    players_msg = await channel.send(f'joueurs: {" | ".join(map(str,bot.PLAYERS))}\n')
    await join_msg.add_reaction(emoji=emoji)

    if(bot.GAME_STARTED == False):
        await check_players(channel=channel, joining_msg=join_msg, players_msg=players_msg, emoji=emoji)
    else:
        print("in vote: bot.GAME_STARTED was already True so why are you waiting for it : maybe change this")
        raise Exception

    """
    # target = {player: [accusators:Player]}
    # emojisCount = {}
    targets_choice = []
    possible_accusators = voters[:]
    async for message in channel.history(limit=100):
        if message.id in ids:
            # with the mention get back the player
            current_player = None
            for player in target_players:
                if(player.discordMember.mentioned_in(message)):
                    current_player = player
                    break
            if(current_player != None):
                accusators = []
                for reaction in message.reactions:
                    if(reaction.emoji == emoji):
                        users = reaction.users()
                        users = await users.flatten()
                        voters_discord_member = [
                            player.discordMember for player in possible_accusators]
                        users_without_me = [
                            user for user in users if user in voters_discord_member]
                        accusators.extend(users_without_me)
                        break

                unique_accusators = (list(set(accusators)))

                # from the discord members to the real players Obj
                accusators_player = []
                for player in possible_accusators:
                    for accusator in unique_accusators:
                        if(player.discordMember == accusator):
                            if(player not in accusators_player):
                                accusators_player.append(player)
                                possible_accusators.remove(player)

                if(len(accusators_player) != 0):
                    targets_choice.append(TargetEmoji(
                        player=current_player, accusators=accusators_player))
                # await message.delete()

    # get back only the max
    numbers = [target.nb_accusators() for target in targets_choice]
    if(len(numbers) != 0):
        max_vote = max(numbers)
        targets_choice = [
            target for target in targets_choice if target.nb_accusators() == max_vote]

    # accepting the other emojis from the temp members of the channel
    for member in tempChannelMembers:
        await channel.set_permissions(
            member, add_reactions=True, send_messages=True, read_messages=True)
    """
