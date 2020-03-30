import discord
from discord.ext import commands
import asyncio
import constant
from data_struct.singleton import Singleton
from data_struct.target import Target

bot = Singleton()

async def vote_mecanism(choice, currentPlayer, channel, targets_table):

    # if the player has a previous target
    # is player in accusator of all targets

    previous_target = None
    for target in targets_table:
        for accusator in target.accusators:
            if(accusator != None):
                if(currentPlayer.discordMember == accusator.discordMember):
                    # the player is already an accusator
                    previous_target = target
                    break
    if(previous_target):
        previous_target.accusators.remove(currentPlayer)
        # check if target is now at 0 accusator to remove it from the targets
        if(len(previous_target.accusators) == 0):
            targets_table.remove(previous_target)

    targets = [target.actual_num for target in targets_table]
    # if the choice is not already a target
    if(choice not in targets):
        currentTarget = Target(
            choice, bot.ALIVE_PLAYERS[choice], currentPlayer)
        targets_table.append(currentTarget)
    else:
        # else we add the new accusator to the list
        current_target = None
        for target in targets_table:
            if(target.actual_num == choice):
                current_target = target
                break
        if(current_target == None):
            raise IndexError
        current_target.add_accusator(currentPlayer)

    message_content = ""
    for target in targets_table:
        message_content += f"{target}\n"
    message = await channel.send(message_content)

    # await asyncio.sleep(TIME_DELETE_MSG)
    # await ctx.message.delete()
