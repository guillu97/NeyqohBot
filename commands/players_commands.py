import discord
from discord.ext import commands
import asyncio
import constant
from data_struct.bot import Bot
from data_struct.player import Player
from data_struct.roles import *
from roles_compute import calc_roles, assign_roles
from turns.vote import vote_mecanism
from data_struct.target import Target

bot = Bot()


@bot.command(name='join', help='rejoindre une partie')
# @commands.has_role(MASTER_OF_THE_GAME)
async def join_game(ctx):
    name = ctx.author.display_name
    print(f'{name} tried to joined')

    if(bot.GAME_CREATED == False):
        await ctx.send(f'aucune partie en cours')
        return

    if(bot.GAME_STARTED == True):
        await ctx.send(f'la partie a déjà commencé')
        return

    if(ctx.message.channel != bot.BEGINNING_CHANNEL):
        await ctx.send('message envoyé dans le mauvais channel')
        return

    print(bot.GAME_CREATED, bot.GAME_STARTED)

    # print(ctx.__dict__)
    memberList = [player.discordMember for player in bot.PLAYERS]
    if(ctx.author in memberList):
        await ctx.send(f'{name} vous êtes déjà dans la partie')
        return

    bot.PLAYERS.append(Player(ctx.author))

    roles = await calc_roles(verbose=True)
    message_content = f'**{name} a rejoint la partie**\n\n'
    if(roles != None):
        print(roles)
        message_content += f'joueurs: {" ".join(map(str,bot.PLAYERS))}\n\n'
        message_content += f'{roles}\n'

    message = await ctx.send(message_content)
    # await asyncio.sleep(constant.TIME_DELETE_MSG)
    # await message.delete()
    # await ctx.message.delete()


@bot.command(name='vote', help='vote pendant la partie')
# @commands.has_role(MASTER_OF_THE_GAME)
async def vote(ctx, choice: int):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie créée')
        return
    if(bot.GAME_STARTED == False):
        await ctx.send("la partie n'a pas commencé")
        return

    currentPlayer = None
    # test with bot.players
    for player in bot.PLAYERS:
        if(player.discordMember == ctx.message.author):
            currentPlayer = player
            break

    if(bot.TURN == "CHASSEUR"):
        # if current_player is a chasseur
        if(isinstance(currentPlayer.role, Chasseur)):
            if(currentPlayer.role.target_choice == None):
                if(choice >= 0 and choice < len(bot.ALIVE_PLAYERS)):
                    currentPlayer.role.target_choice = bot.ALIVE_PLAYERS[choice]
                    await bot.HISTORY_TEXT_CHANNEL.send(
                        f"\n\n**Vous avez choisi {currentPlayer.role.target_choice}**\n\n")
                    return

    if(bot.TURN == "MAYOR_GIVE_UP"):
        # if current_player is the mayor
        if(currentPlayer == bot.MAYOR):
            if(choice >= 0 and choice < len(bot.ALIVE_PLAYERS)):
                await vote_mecanism(choice, currentPlayer, bot.HISTORY_TEXT_CHANNEL, bot.MAYOR_CHOICES)
                return

    if(currentPlayer not in bot.ALIVE_PLAYERS):
        print('current player is not in the alive players')
        return

    # if vote during TURN="LOUPS"
    if(bot.TURN == "LOUPS"):
        if(currentPlayer in bot.LOUPS):
            # if vote dans channel loup
            if(ctx.message.channel == bot.LOUPS_TEXT_CHANNEL):
                # if choice is valid
                if(choice >= 0 and choice < len(bot.ALIVE_PLAYERS)):
                    await vote_mecanism(choice, currentPlayer, bot.LOUPS_TEXT_CHANNEL, bot.LOUP_TARGETS)
                    return

    if(bot.TURN == "LOUP_BLANC"):
        # if current_player is a loupBlanc
        if(isinstance(currentPlayer.role, LoupBlanc)):
            targets = [player for player in bot.LOUPS if(
                not isinstance(player.role, LoupBlanc))]
            if(choice >= 0 and choice < len(targets)):
                currentPlayer.role.target_choice = targets[choice]
                await currentPlayer.private_channel.send(
                    f"\n\n**Vous avez choisi {currentPlayer.role.target_choice}**\n\n")
                return

    if(bot.TURN == "MAYOR_ELECTION"):
        # if choice is valid
        if(choice >= 0 and choice < len(bot.ALIVE_PLAYERS)):
            await vote_mecanism(choice, currentPlayer, bot.HISTORY_TEXT_CHANNEL, bot.MAYOR_TARGETS)
            return

    if(bot.TURN == "VICTIME_ELECTION"):
        # if player is alive
        # if choice is valid
        if(choice >= 0 and choice < len(bot.ALIVE_PLAYERS)):
            await vote_mecanism(choice, currentPlayer, bot.HISTORY_TEXT_CHANNEL, bot.VICTIM_TARGETS)
            return

    if(bot.TURN == "MAYOR_CHOICE"):
        # if current_player is the mayor
        if(currentPlayer == bot.MAYOR):
            if(choice >= 0 and choice < len(bot.MAYOR_ONLY_CHOICES)):
                await vote_mecanism(choice, currentPlayer, bot.HISTORY_TEXT_CHANNEL, bot.MAYOR_ONLY_CHOICES)
                return

    if(bot.TURN == "CUPIDON"):
        # if current_player is a chasseur
        if(isinstance(currentPlayer.role, Cupidon)):
            if(len(currentPlayer.role.targets_choice) < 2):
                if(choice >= 0 and choice < len(bot.ALIVE_PLAYERS) and bot.ALIVE_PLAYERS[choice] not in currentPlayer.role.targets_choice):
                    currentPlayer.role.targets_choice.append(
                        bot.ALIVE_PLAYERS[choice])
                    await currentPlayer.private_channel.send(
                        f"\n\n**Vous avez choisi {bot.ALIVE_PLAYERS[choice]}**\n\n")
                    return

    if(bot.TURN == "VOYANTE"):
        # if current_player is a voyante
        if(isinstance(currentPlayer.role, Voyante)):
            if(choice >= 0 and choice < len(bot.ALIVE_PLAYERS)):
                await vote_mecanism(choice, currentPlayer, currentPlayer.private_channel, currentPlayer.role.targets)
                return
    if(bot.TURN == "SORCIERE_LIFE"):
        # if current_player is a sorciere
        if(isinstance(currentPlayer.role, Sorcière)):
            if(currentPlayer.role.lifePotion):
                if(choice == 0):
                    currentPlayer.role.lifePotion = False
                    await currentPlayer.private_channel.send(f"\n\n**Vous avez choisi de sauver {bot.LOUP_FINAL_TARGET}**\n\n")
                    return
    if(bot.TURN == "SORCIERE_DEATH"):
        # if current_player is a sorciere
        if(isinstance(currentPlayer.role, Sorcière)):
            if(currentPlayer.role.deathPotion):
                if(choice >= 0 and choice < len(bot.ALIVE_PLAYERS)):
                    currentPlayer.role.target_choice = bot.ALIVE_PLAYERS[choice]
                    currentPlayer.role.deathPotion = False
                    await currentPlayer.private_channel.send(f"\n\n**Vous avez choisi d'empoisonner {currentPlayer.role.target_choice}**\n\n")
                    return


@bot.command(name='players', help="montre les joueurs actuellement dans la partie")
# @commands.has_role(constant.MASTER_OF_THE_GAME)
async def show_players(ctx):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie créée')
        return
    await ctx.send("\n".join(map(str, bot.PLAYERS)))

# TODO : create a command to known which roles are left


@bot.command(name='players-alive', help="montre les joueurs vivants actuellement dans la partie")
# @commands.has_role(constant.MASTER_OF_THE_GAME)
async def show_players_alive(ctx):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie créée')
        return
    if(bot.GAME_STARTED == False):
        await ctx.send("la partie n'a pas commencée")
        return

    await ctx.send("\n".join(map(str, bot.ALIVE_PLAYERS)))
