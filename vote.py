import asyncio
from discord import Emoji
from data_struct.target import TargetEmoji


async def check_multiple_votes(channel, context_messages, emoji, voters):
    # check nb reactions per player
    # => should be 0 at the beginning
    # => to be sure => remove all reactions except from me

    # playerReacts = {player: Reaction}  # a dict associating the player to the only reaction he has
    playerReacts = {}
    for player in voters:
        playerReacts[player.discordMember] = None

    ids = [message.id for message in context_messages]
    async for message in channel.history(limit=100):
        if message.id in ids:
            if(len(message.reactions) != 1):
                await message.clear_reactions()
                await message.add_reaction(emoji=emoji)

    while(True):
        # print("check running")
        # check again the nb of reactions per player
        # if before it was 0  => don't remove the reaction
        # if it was not 0 => remove the old reaction and let the new reaction

        async for message in channel.history(limit=100):
            if(message.id in ids):
                for reaction in message.reactions:
                    # if not the good emoji => then delete
                    if(reaction.emoji != emoji):
                        await reaction.clear()
                    else:
                        users = reaction.users()
                        users = await users.flatten()
                        if(len(users) != 1):
                            for user in users:
                                if(not user.bot):
                                    if(user not in playerReacts.keys()):
                                        print(
                                            "player not in playerReacts.keys() => a player that cannot vote maybe")
                                        await reaction.remove(user)
                                        break

                                    # if no reaction before then add one
                                    if(playerReacts[user] == None):
                                        playerReacts[user] = reaction
                                    # if the message of the reaction changed
                                    # print(
                                    #    f"DEBUG: {playerReacts[user].message}")
                                    # print(f"DEBUG: {playerReacts}")
                                    if(playerReacts[user].message.id != message.id):
                                        # remove the old reaction and remove the reaction from the list
                                        await playerReacts[user].remove(user)
                                        playerReacts[user] = reaction
        # need to sleep at least a bit because otherwise we cannot cancel the task
        # await asyncio.sleep(1)
        await asyncio.sleep(0.1)


async def timer(channel, time):
    time_message = await channel.send(f'*temps restant: {time}*')
    for i in range(1, time+1):
        await asyncio.sleep(1)
        await time_message.edit(content=str(f'*temps restant: {time-i}*'))
    # print("timer finished")


async def wait_event(event_variable):
    while(event_variable != True):
        print("waiting")
        await asyncio.sleep(1)

# @return [] or a list of TargetEmoji


async def vote(channel, target_players, voters, emoji, time=0):
    messages = []
    for player in target_players:
        message = await channel.send(f'{player.discordMember.mention}')
        await message.add_reaction(emoji=emoji)
        messages.append(message)
    ids = [message.id for message in messages]

    # start the task check of multiple reactions
    task_msg_check = asyncio.create_task(
        check_multiple_votes(channel, messages, emoji, voters))

    if(time == 0):
        print("in vote: time == 0")
        raise Exception
    # start timer message
    await timer(channel, time)

    # not accepting the other emojis from all the members of the server
    # list of the players from which we remove the rights
    tempChannelMembers = channel.members[:]
    for member in tempChannelMembers:
        await channel.set_permissions(
            member, add_reactions=False, send_messages=False, read_messages=False)
    # wait synchronisation of the reaction changes
    await asyncio.sleep(1)
    # stop the task check of multiple reactions
    task_msg_check.cancel()

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

    return targets_choice
