import asyncio
from discord import Emoji
from data_struct.target import TargetEmoji


async def check_multiple_votes(channel, context_messages, emoji, voters, nb_votes_max=1):
    # check nb reactions per player
    # => should be 0 at the beginning
    # => to be sure => remove all reactions except from me

    # playerReacts = {player: Reaction}  # a dict associating the player to the only reaction he has
    playerReacts = {}
    for player in voters:
        playerReacts[player.discordMember] = []

    ids = [message.id for message in context_messages]
    async for message in channel.history(limit=30):
        if message.id not in ids:
            continue
        if(len(message.reactions) != 1):
            await message.clear_reactions()
            await message.add_reaction(emoji=emoji)

    while(True):
        # print("check running")
        # check again the nb of reactions per player
        # if before it was 0  => don't remove the reaction
        # if it was not 0 => remove the old reaction and let the new reaction


        async for message in channel.history(limit=30):
            if(message.id not in ids):
                continue
            for reaction in message.reactions:
                # if not the good emoji => then delete
                if(reaction.emoji != emoji):
                    await reaction.clear()
                    continue

                
                
                users = reaction.users()
                users = await users.flatten()

                # remove uncheked reactions from table
                for user,player_reactions in playerReacts.items():
                    for player_reaction in player_reactions:
                        if(player_reaction.message.id == reaction.message.id and user not in users):
                            player_reactions.remove(player_reaction)

                if(len(users) == 1):
                    continue
                for user in users:
                    if(user.bot):
                        continue
                    if(user not in playerReacts.keys()):
                        print(
                            "player not in playerReacts.keys() => a player that cannot vote maybe")
                        await reaction.remove(user)
                        continue
                    
                    

                    reaction_message_ids = [reaction.message.id for reaction in playerReacts[user]]
                    if(message.id not in reaction_message_ids):
                        playerReacts[user].append(reaction)
                        print(playerReacts)
                        if(len(playerReacts[user]) > nb_votes_max):
                            for _ in range(len(playerReacts[user]) - nb_votes_max):
                                # remove one reaction from the reactions
                                reaction_to_remove = playerReacts[user].pop(-1)
                                await reaction_to_remove.remove(user)

                    
                        

                    """
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
                    """
        # need to sleep at least a bit because otherwise we cannot cancel the task
        # await asyncio.sleep(1)
        await asyncio.sleep(0.1)


async def timer_and_validate(channel, time, voters):
    validate_emoji = "☑️"
    validate_msg = await channel.send(f"Validez votre choix en ajoutant un {validate_emoji}")
    await validate_msg.add_reaction(emoji=validate_emoji)

    time_message = await channel.send(f'*temps restant: {time}*')

    votersDiscord = [player.discordMember for player in voters]
    # if all voters validated the choice then break the timer
    voters_validated = False
    for i in range(1, time+1):
        await asyncio.sleep(1)
        await time_message.edit(content=str(f'*temps restant: {time-i}*'))
        # search validate message
        async for message in channel.history(limit=30):
            if(message.id == validate_msg.id):
                # check the reaction if reaction emoji == validate emoji
                for reaction in message.reactions:
                    if(reaction.emoji == validate_emoji):
                        # check the users that have validated, if all voters validated the stop the timer
                        users = reaction.users()
                        users = await users.flatten()
                        countVoters = 0
                        if(len(users) != 1):
                            for user in users:
                                if(not user.bot):
                                    if(user not in votersDiscord):
                                        await reaction.remove(user)
                                        continue

                                    countVoters += 1

                        if(countVoters == len(voters)):
                            voters_validated = True

                        break
                break
        # if all voters validated the choice then break the timer
        if(voters_validated):
            break
    # print("timer finished")


async def wait_event(event_variable):
    while(event_variable != True):
        print("waiting")
        await asyncio.sleep(1)

# @return [] or a list of TargetEmoji


async def vote(channel, target_players, voters, emoji, time=0, nb_votes_max=1):
    messages = []
    for player in target_players:
        message = await channel.send(f'{player.discordMember.mention}')
        await message.add_reaction(emoji=emoji)
        messages.append(message)
    ids = [message.id for message in messages]

    # start the task check of multiple reactions
    try:
        task_msg_check = asyncio.create_task(
            check_multiple_votes(channel, messages, emoji, voters, nb_votes_max))
    except Exception as e:
        print(e)

    if(time == 0):
        print("in vote: time == 0")
        raise Exception
    # start timer message
    await timer_and_validate(channel, time, voters)

    # TODO: search with Emoji.roles if there is another way to restrict emojis
    # not accepting the other emojis from all the members of the server
    # list of the players from which we remove the rights
    tempChannelMembers = channel.members[:]
    for member in tempChannelMembers:
        await channel.set_permissions(
            member, add_reactions=False, send_messages=False, read_messages=True)
        # await channel.set_permissions(
        #    member, add_reactions=False, send_messages=False, read_messages=False)
    # wait synchronisation of the reaction changes
    await asyncio.sleep(1)
    # stop the task check of multiple reactions
    try:
        task_msg_check.cancel()
    except Exception as e:
        print(e)

    # target = {player: [accusators:Player]}
    # emojisCount = {}
    targets_choice = []
    possible_accusators = voters[:]
    async for message in channel.history(limit=30):
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
                # print("unique_accusators")
                # print(unique_accusators)

                # from the discord members to the real players Obj
                accusators_player = []
                for player in possible_accusators:
                    for accusator in unique_accusators:
                        if(player.discordMember == accusator):
                            if(player not in accusators_player):
                                accusators_player.append(player)
                                # possible_accusators.remove(player)
                # print("accusators_player")
                # print(accusators_player)

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
        # await channel.set_permissions(
        #    member, add_reactions=True, send_messages=True, read_messages=True)
        await channel.set_permissions(
            member, add_reactions=True, send_messages=True, read_messages=True)

    return targets_choice
