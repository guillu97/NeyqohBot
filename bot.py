# bot.py
import os
import random

import time
import asyncio

import discord
from discord.ext import commands
from dotenv import load_dotenv

from player import Player
from roles import *

from target import Target


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

### CONSTANTS ###
MASTER_OF_THE_GAME = 'Maitre du jeu'

GAME_CATEGORY_NAME = "Neyqoh_Game"
GAME_VOICE_CHANNEL_NAME = "Place du village"
HISTORY_TEXT_CHANNEL_NAME = "Histoire"
PRIVATE_TEXT_CHANNEL_NAME = 'Ton role et actions'
LOUPS_TEXT_CHANNEL_NAME = 'Loups Garous'

TIME_FOR_ROLES = 10
TIME_FOR_LOUPS = 10
TIME_FOR_MAYOR_ELECTION = 10  # TODO: 120 in prod

TIME_FOR_VICTIM_ELECTION = 10  # TODO: 120 in prod
TIME_FOR_MAYOR_FINAL_CHOICE = 10  # TODO: 10 - 20 secs in prod

TIME_FOR_MAYOR_GIVE_UP = 10  # TODO in prod 30 s

TIME_FOR_VOYANTE = 10  # TODO 20 - 30 secs in prod

TIME_DELETE_MSG = 0

TIME_AUTO_DESTRUCT = 10  # TODO: 30 in prod

NB_MAX_MAYOR_ELECTIONS = 3

NB_MAX_VICTIM_ELECTIONS = 3

MINIMUM_PLAYER_NB = 2  # TODO: in prod : 4 players min

DEFAULT_NB_LOUP = 1000  # if nb > nb_players => nb = nb_players/4

DEFAULT_NB_VOYANTE = 1

DEFAULT_NB_ANGE = 1
###


def default_values(bot):
    bot.GAME_CREATED = False
    bot.GAME_STARTED = False
    bot.PLAYERS = []
    bot.DEADS_OF_NIGHT = []
    bot.DEADS_OF_DAY = []
    bot.DEADS = []
    bot.LOUPS = []
    bot.ALIVE_PLAYERS = []
    bot.LOUP_TARGETS = []
    bot.MAYOR_TARGETS = []
    bot.MAYOR_CHOICES = []
    bot.MAYOR_ONLY_CHOICES = []
    bot.VICTIM_TARGETS = []

    bot.WINNER = None

    bot.LOUP_FINAL_TARGET = None
    bot.MAYOR = None
    bot.VICTIM = None

    bot.MINIMUM_PLAYER_NB = MINIMUM_PLAYER_NB

    bot.NB_LOUP = DEFAULT_NB_LOUP

    bot.NB_VOYANTE = DEFAULT_NB_VOYANTE

    bot.NB_ANGE = DEFAULT_NB_ANGE

    bot.NB_NIGHTS = 1

    bot.TURN = ""


bot = commands.Bot(command_prefix='!')

default_values(bot)


# on ready function: when the bot connects to the server
@bot.event
async def on_ready():
    # the bot user is connected to Discord
    print(f'{bot.user.name} has connected to Discord!')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')
    print(error)
    # raise


@bot.command(name='99', help='Responds with a random quote from Brooklyn 99')
async def nine_nine(ctx):
    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    response = random.choice(brooklyn_99_quotes)
    await ctx.send(response)


@bot.command(name='roll_dice', help='Simulates rolling dice. !roll_dice <NB_OF_DICES> <NB_OF_SIDES>')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))


@bot.command(name='create-channel', help='create a channel')
@commands.has_role('admin')
async def create_channel(ctx, channel_name='real-python'):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)


@bot.command(name='new', help='crée une nouvelle partie')
@commands.has_role(MASTER_OF_THE_GAME)
async def new_game(ctx):
    if(bot.GAME_CREATED == True):
        await ctx.send('Une partie est déjà créée')
        return
    if(bot.GAME_STARTED == True):
        await ctx.send('Une partie est déjà en cours')
        return

    bot.PLAYERS.append(Player(ctx.author))
    nameList = [player.discordMember.display_name for player in bot.PLAYERS]
    bot.GAME_CREATED = True

    message = 'Nouvelle partie créée, utiliser la commande !join pour rejoindre la partie\n\n'
    message += f'{ctx.author.display_name} a rejoint la partie\n\n'
    message += f'joueurs: {nameList}\n'
    await ctx.send(message)

    # save the channel where the new was typed
    bot.BEGINNING_CHANNEL = ctx.message.channel


@bot.command(name='join', help='rejoindre une partie')
# @commands.has_role(MASTER_OF_THE_GAME)
async def join_game(ctx):
    name = ctx.author.display_name
    print(f'{name} tried to joined')

    if(ctx.message.channel != bot.BEGINNING_CHANNEL):
        await ctx.send('message envoyé dans le mauvais channel')
        return

    if(bot.GAME_CREATED == False):
        await ctx.send(f'aucune partie en cours')
        return

    if(bot.GAME_STARTED == True):
        await ctx.send(f'la partie a déjà commencé')
        return

    print(bot.GAME_CREATED, bot.GAME_STARTED)

    # print(ctx.__dict__)
    memberList = [player.discordMember for player in bot.PLAYERS]
    if ctx.author in memberList:
        await ctx.send(f'{name} vous êtes déjà dans la partie')
        return

    bot.PLAYERS.append(Player(ctx.author))
    nameList = [
        player.discordMember.display_name for player in bot.PLAYERS]

    roles = await assign_roles()
    print(roles)

    message_content = f'{name} a rejoint la partie\n\n'
    message_content += f'joueurs: {nameList}\n\n'
    message_content += f'{roles}\n'
    message = await ctx.send(message_content)

    # await asyncio.sleep(TIME_DELETE_MSG)
    # await message.delete()
    # await ctx.message.delete()

    print(nameList)


@bot.command(name='stop', help='stop la partie en cours')
@commands.has_role(MASTER_OF_THE_GAME)
async def stop_game(ctx):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie en cours')
        return

    await ctx.send('arret de la partie en cours')
    await delete_game_category(ctx)
    default_values(bot)


@bot.command(name='delete', help="supprime les categrory du jeu si aucune partie n'est en cours")
@commands.has_role(MASTER_OF_THE_GAME)
async def delete_channels(ctx):
    if(bot.GAME_CREATED == True):
        await ctx.send('une partie a été créée')
        return
    if(bot.GAME_STARTED == True):
        await ctx.send('une partie est en cours')
        return

    await ctx.send('suppression des channels de jeu')
    await delete_game_category(ctx)


@bot.command(name='start', help='commence la partie avec toutes les personnes ayant effectuées !join')
@commands.has_role(MASTER_OF_THE_GAME)
async def start_game(ctx):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie créée')
        return

    if(len(bot.PLAYERS) < bot.MINIMUM_PLAYER_NB):
        await ctx.send(f"le nombre minimum de joueurs ({bot.MINIMUM_PLAYER_NB}) n'est pas atteint")
        return

    await ctx.send('la partie commence!')
    bot.GAME_STARTED = True
    await create_game_category(ctx)
    guild = ctx.guild
    game_voice_channel = bot.GAME_VOICE_CHANNEL

    # move the player to the game voice channel
    for player in bot.PLAYERS:
        member = player.discordMember
        print(member.display_name)
        try:
            await member.move_to(game_voice_channel)
        except Exception as e:
            print(e)

    await game_process(ctx)

    # beginningChannel = None
    # search for the beginning voice channel
    # discord.utils.get(guild.categories, name=GAME_CATEGORY_NAME)
    # print(beginningChannel.members)


async def game_process(ctx):
    await bot.HISTORY_TEXT_CHANNEL.send(
        'vous avez 10 secondes avant que la partie commence')
    bot.TURN = "ROLES"
    # wait the time that the people check their roles
    await asyncio.sleep(TIME_FOR_ROLES)
    # while(not someone win or draw)
    while(True):
        await bot.HISTORY_TEXT_CHANNEL.send(f'la nuit {bot.NB_NIGHTS} tombe')
        await asyncio.sleep(1)

        # voyante's turn
        if(still_something(Voyante)):
            await voyante_turn()

        ### wake loups ###
        await loups_turn()

        ### wake villageois ###
        await bot.HISTORY_TEXT_CHANNEL.send('Le village se réveille')
        bot.TURN = "DAY"

        ### compute deads over night ###
        if(bot.LOUP_FINAL_TARGET != None):
            bot.DEADS_OF_NIGHT.append(bot.LOUP_FINAL_TARGET)
            # the loup final_target can be reset to None
            bot.LOUP_FINAL_TARGET = None

        ### display the night deads ###
        message = ""
        if(len(bot.DEADS_OF_NIGHT) == 0):
            message += "personne n'est mort ce soir"
        else:
            for player in bot.DEADS_OF_NIGHT:
                message += f"{player} est mort ce soir, son role : {player.role}\n"
                # now put it in the table for all the deads
                bot.DEADS.append(player)
                # remove the dead from the alive player table
                bot.ALIVE_PLAYERS.remove(player)
        bot.DEADS_OF_NIGHT.clear()
        await bot.HISTORY_TEXT_CHANNEL.send(message)

        # if mayor killed, give his mayorship
        for player in bot.DEADS:
            if(player == bot.MAYOR):
                await mayor_give_up()
                break

        ### display deads ###
        message = "\nmorts:\n"
        for player in bot.DEADS:
            message += f"{player}: {player.role}\n"

        ### display alive ###
        message += "\nvivants:\n"
        for player in bot.ALIVE_PLAYERS:
            message += f"{player}\n"

        ### display mayor ###
        if(bot.MAYOR != None):
            message += f"\nMaire: {bot.MAYOR}\n"

        ### display roles in games ###
        message += "\nroles restants:\n"
        roles = [player.role for player in bot.ALIVE_PLAYERS]
        random.shuffle(roles)
        for role in roles:
            message += f'{role}\n'
        await bot.HISTORY_TEXT_CHANNEL.send(message)

        ### check someone wins or draw ###
        # check if only one player left
        print("check_win")
        print(check_win())
        if(check_win()):
            break

        ### vote for maire ###
        if(bot.MAYOR == None):
            await election()
        else:
            await bot.HISTORY_TEXT_CHANNEL.send(f'\nMaire: {bot.MAYOR} \n')

        ### vote for day kill ###
        await lynch()

        ### compute dead of the day ###
        if(bot.VICTIM != None):
            bot.DEADS_OF_DAY.append(bot.VICTIM)
            # bot.VICTIM can be reset to None
            bot.VICTIM = None

        ### display kill of the day ###
        message = ""
        if(len(bot.DEADS_OF_DAY) == 0):
            message += "personne n'est mort"
        else:
            for player in bot.DEADS_OF_DAY:
                message += f"{player} est mort aujourd'hui, son role : {player.role}\n"
                # now put it in the table for all the deads
                bot.DEADS.append(player)
                # remove the dead from the alive player table
                bot.ALIVE_PLAYERS.remove(player)
        bot.DEADS_OF_DAY.clear()
        await bot.HISTORY_TEXT_CHANNEL.send(message)

        # if mayor killed, give his mayorship
        for player in bot.DEADS:
            if(player == bot.MAYOR):
                await mayor_give_up()
                break

        ### check if village wins or lovers or loups ###
        print("check_win")
        print(check_win())
        if(check_win()):
            break

        bot.NB_NIGHTS += 1

    ### display winners ###
    message = f"\n\n**Les {bot.WINNER} ont gagné après la nuit {bot.NB_NIGHTS}**\n\n"
    message += f"\n\n**Les channels vont s'auto-détruire dans {TIME_AUTO_DESTRUCT} secondes**\n\n"
    await bot.HISTORY_TEXT_CHANNEL.send(message)

    await asyncio.sleep(TIME_AUTO_DESTRUCT)
    await stop_game(ctx)


def still_something(check_class):
    # check if no more loup in game
    still = False
    for player in bot.ALIVE_PLAYERS:
        if(isinstance(player.role, check_class)):
            still = True
            break
    return still


def check_ange():
    if(len(bot.DEADS) == 1 and isinstance(bot.DEADS[0].role, Ange)):
        return True
    return False


def check_win():

    still_loups = still_something(LoupGarou)
    still_villageois = still_something(Villageois)
    still_people = still_something(Role)

    if(check_ange() == True):
        bot.WINNER = "Ange"
        return True
    elif(len(bot.ALIVE_PLAYERS) == 1):
        bot.WINNER = bot.ALIVE_PLAYERS[0].role
        return True
    elif(not still_loups):
        # TODO: change this in funct of roles
        bot.WINNER = "Villageois"
        return True
    elif(not still_villageois):
        # TODO: if lovers only left then lovers win
        bot.WINNER = "Loups Garous"
        return True
    elif(not still_people):
        bot.WINNER = "Dieus"
        return True

    return False


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

    if(bot.TURN == "MAYOR_GIVE_UP"):
        # if current_player is the mayor
        if(currentPlayer == bot.MAYOR):
            if(choice >= 0 and choice < len(bot.ALIVE_PLAYERS)):
                await vote_mecanism(choice, currentPlayer, bot.HISTORY_TEXT_CHANNEL, bot.MAYOR_CHOICES)
                return

    if(currentPlayer == None):
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

    if(bot.TURN == "MAYOR_ELECTION"):
        # if choice is valid
        if(choice >= 0 and choice < len(bot.ALIVE_PLAYERS)):
            await vote_mecanism(choice, currentPlayer, bot.HISTORY_TEXT_CHANNEL, bot.MAYOR_TARGETS)
            return

    if(bot.TURN == "VICTIME_ELECTION"):
        # if choice is valid
        if(choice >= 0 and choice < len(bot.ALIVE_PLAYERS)):
            await vote_mecanism(choice, currentPlayer, bot.HISTORY_TEXT_CHANNEL, bot.VICTIM_TARGETS)
            return

    if(bot.TURN == "MAYOR_CHOICE"):
        # if current_player is the mayor
        if(currentPlayer == bot.MAYOR):
            if(choice >= 0 and choice < len(bot.MAYOR_ONLY_CHOICES)):
                await vote_mecanism(choice, currentPlayer, bot.HISTORY_TEXT_CHANNEL, bot.MAYOR_CHOICES)
                return

    if(bot.TURN == "VOYANTE"):
        # if current_player is a voyante
        if(isinstance(currentPlayer.role, Voyante)):
            if(choice >= 0 and choice < len(bot.ALIVE_PLAYERS)):
                await vote_mecanism(choice, currentPlayer, currentPlayer.private_channel, currentPlayer.role.targets)
                return


async def vote_mecanism(choice, currentPlayer, channel, targets_table):

    # if the player has a previous target
    # is player in accusator of all targets

    previous_target = None
    for target in targets_table:
        for accusator in target.accusators:
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


async def loups_turn():

    # warn village
    await bot.HISTORY_TEXT_CHANNEL.send(f'\n\n**Les loups garous ont {TIME_FOR_LOUPS} secondes pour choisir leur victime de la nuit:**\n\n')
    bot.TURN = "LOUPS"

    # make channel accessible
    for player in bot.LOUPS:
        member = player.discordMember
        # overwrites[member] = discord.PermissionOverwrite(read_messages=True)
        await bot.LOUPS_TEXT_CHANNEL.set_permissions(
            member, send_messages=True, read_messages=True)

    # warn loups garou
    message = f'Vous avez {TIME_FOR_LOUPS} secondes pour choisir votre victime de la nuit\n\n'
    time_left = TIME_FOR_LOUPS

    num = 0
    for player in bot.ALIVE_PLAYERS:
        member = player.discordMember
        message += f'{num}:  {member.display_name}\n'
        num += 1
    message += '\ncommande: !vote <int>\n'
    message += 'exemple: !vote 5\n'
    await bot.LOUPS_TEXT_CHANNEL.send(message)

    await asyncio.sleep(time_left - 10)
    time_left = 10
    await bot.LOUPS_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
    await asyncio.sleep(time_left - 5)
    time_left = 5
    await bot.LOUPS_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
    await asyncio.sleep(time_left)

    # find the target:
    print(bot.LOUP_TARGETS)
    # if no target
    if(len(bot.LOUP_TARGETS) == 0):
        # no dead from the loups
        await bot.LOUPS_TEXT_CHANNEL.send("vous n'avez pas choisi de victime")
    else:
        targets_choice = None
        max_accusator = max([len(target.accusators)
                             for target in bot.LOUP_TARGETS])
        targets_choice = [target for target in bot.LOUP_TARGETS if len(
            target.accusators) == max_accusator]

        # draw for the votes
        if(len(targets_choice) > 1):
            # choose the target randomly
            rand_index = random.randint(0, len(targets_choice) - 1)
            target_choice = targets_choice[rand_index]
        elif(len(targets_choice) == 1):
            target_choice = targets_choice[0]
        else:
            print(
                "error loups_turn: not len(targets_choice) > 1 ,  not len(targets_choice) == 1")
            raise Exception

        bot.TURN = "FIN_LOUPS"

        # make channel inacessible in write only
        for player in bot.LOUPS:
            member = player.discordMember
            # overwrites[member] = discord.PermissionOverwrite(read_messages=True)
            await bot.LOUPS_TEXT_CHANNEL.set_permissions(
                member, send_messages=False, read_messages=True)

        # warn loups of the choice
        await bot.LOUPS_TEXT_CHANNEL.send(f'votre choix est fait, vous avez choisi {target_choice.player}')
        await asyncio.sleep(1)
        bot.LOUP_FINAL_TARGET = target_choice.player
        bot.LOUP_TARGETS.clear()

    # make channel inacessible
    for player in bot.LOUPS:
        member = player.discordMember
        # overwrites[member] = discord.PermissionOverwrite(read_messages=True)
        await bot.LOUPS_TEXT_CHANNEL.set_permissions(
            member, send_messages=False, read_messages=False)


async def voyante_turn():
    await bot.HISTORY_TEXT_CHANNEL.send(f'La voyante a {TIME_FOR_VOYANTE} secondes pour choisir un joueur\n\n')
    bot.TURN = "VOYANTE"

    # find the voyante(s)
    voyantes = [player for player in bot.ALIVE_PLAYERS if(
        isinstance(player.role, Voyante))]

    # warn voyante(s)
    message = f'Vous avez {TIME_FOR_VOYANTE} secondes pour choisir le joueur dont le role vous intéresse\n\n'
    time_left = TIME_FOR_VOYANTE

    num = 0
    for player in bot.ALIVE_PLAYERS:
        member = player.discordMember
        message += f'{num}:  {member.display_name}\n'
        num += 1
    message += '\ncommande: !vote <int>\n'
    message += 'exemple: !vote 5\n'

    for voyante in voyantes:
        await voyante.private_channel.send(message)

    await asyncio.sleep(time_left - 10)
    time_left = 10
    for voyante in voyantes:
        await voyante.private_channel.send(f'{time_left} secondes restantes')
    await asyncio.sleep(time_left - 5)
    time_left = 5
    for voyante in voyantes:
        await voyante.private_channel.send(f'{time_left} secondes restantes')
    await asyncio.sleep(time_left)

    bot.TURN = "FIN_VOYANTE"

    # warn of the choice
    for voyante in voyantes:
        if(len(voyante.role.targets) == 0):
            await voyante.private_channel.send("vous n'avez choisi personne")
        elif(len(voyante.role.targets) == 1):
            target = voyante.role.targets[0]
            await voyante.private_channel.send(f'votre choix est fait, vous avez choisi {target.player} qui est {target.player.role}')
        else:
            print(
                "error in voyante_turn : not len(voyante.targets) == 0  and not len(voyante.targets) == 1")
            raise Exception
        voyante.role.targets = []


async def election():

    # find the target:
    # print(bot.LOUP_TARGETS)
    counter_max_elections = NB_MAX_MAYOR_ELECTIONS
    targets_choice = []
    while(len(targets_choice) != 1 and counter_max_elections > 0):

        ### warn village ###
        message = f'\n\nLes villageois ont {TIME_FOR_MAYOR_ELECTION} secondes pour choisir le maire:\n\n'
        bot.TURN = "MAYOR_ELECTION"

        ### vote ###

        time_left = TIME_FOR_MAYOR_ELECTION

        num = 0
        for player in bot.ALIVE_PLAYERS:
            message += f'{num}:  {player}\n'
            num += 1
        message += '\ncommande: !vote <int>\n'
        message += 'exemple: !vote 5\n'
        await bot.HISTORY_TEXT_CHANNEL.send(message)

        await asyncio.sleep(time_left - 30)
        time_left = 30
        await bot.HISTORY_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
        await asyncio.sleep(time_left - 20)
        time_left = 20
        await bot.HISTORY_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
        await asyncio.sleep(time_left - 10)
        time_left = 10
        await bot.HISTORY_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
        await asyncio.sleep(time_left - 5)
        time_left = 5
        await bot.HISTORY_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
        await asyncio.sleep(time_left)

        # if no target
        if(len(bot.MAYOR_TARGETS) == 0):
            # no mayor choice from the players
            await bot.HISTORY_TEXT_CHANNEL.send("\n\n*Vous n'avez pas choisi de maire, une nouvelle election va avoir lieu*\n\n")
        else:
            targets_choice.clear()
            max_accusator = max([len(target.accusators)
                                 for target in bot.MAYOR_TARGETS])
            targets_choice = [target for target in bot.MAYOR_TARGETS if len(
                target.accusators) == max_accusator]

        bot.MAYOR_TARGETS.clear()

        counter_max_elections -= 1

    # draw for the votes or no mayor have been choose
    if(len(targets_choice) > 1 or len(targets_choice) == 0):
        # choose the target randomly
        rand_index = random.randint(0, len(targets_choice) - 1)
        target_choice = targets_choice[rand_index]
    elif(len(targets_choice) == 1):
        target_choice = targets_choice[0]
    else:
        print(
            "error in election: not len(targets_choice) > 1, not len(targets_choice) == 1")
        raise Exception

    bot.TURN = "FIN_MAYOR_ELECTION"

    # results
    # warn players of the choice
    await bot.HISTORY_TEXT_CHANNEL.send(f'votre choix est fait, vous avez choisi {target_choice.player}')
    await asyncio.sleep(1)
    bot.MAYOR = target_choice.player
    bot.MAYOR_TARGETS.clear()


async def mayor_give_up():

    message = f'Le maire a {TIME_FOR_MAYOR_GIVE_UP} secondes pour donner son role:\n\n'
    bot.MAYOR_CHOICES.clear()
    bot.TURN = "MAYOR_GIVE_UP"

    time_left = TIME_FOR_MAYOR_GIVE_UP

    num = 0
    for player in bot.ALIVE_PLAYERS:
        message += f'{num}:  {player}\n'
        num += 1
    message += '\ncommande: !vote <int>\n'
    message += 'exemple: !vote 5\n'
    await bot.HISTORY_TEXT_CHANNEL.send(message)

    await asyncio.sleep(time_left - 30)
    time_left = 30
    await bot.HISTORY_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
    await asyncio.sleep(time_left - 20)
    time_left = 20
    await bot.HISTORY_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
    await asyncio.sleep(time_left - 10)
    time_left = 10
    await bot.HISTORY_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
    await asyncio.sleep(time_left - 5)
    time_left = 5
    await bot.HISTORY_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
    await asyncio.sleep(time_left)

    target_choice = None
    # if no target
    if(len(bot.MAYOR_CHOICES) == 0):
        # choose the target randomly
        rand_index = random.randint(0, len(bot.ALIVE_PLAYERS) - 1)
        target_choice = bot.ALIVE_PLAYERS[rand_index]
    elif(len(bot.MAYOR_CHOICES) == 1):
        target_choice = bot.MAYOR_CHOICES[0].player
    else:
        print(
            "error in election: not len(targets_choice) > 1, not len(targets_choice) == 1")
        raise Exception
    bot.TURN = "FIN_MAYOR_GIVE_UP"
    # results
    # warn players of the choice
    await bot.HISTORY_TEXT_CHANNEL.send(f'votre choix est fait, vous avez choisi {target_choice}')
    await asyncio.sleep(1)
    bot.MAYOR = target_choice.player
    bot.MAYOR_CHOICES.clear()


async def lynch():
    # find the target:
    # print(bot.LOUP_TARGETS)
    targets_choice = []

    ### warn village ###
    message = f'\n\n**Les villageois ont {TIME_FOR_VICTIM_ELECTION} secondes pour choisir la victime du jour:**\n\n'
    bot.TURN = "VICTIME_ELECTION"

    ### vote ###

    time_left = TIME_FOR_VICTIM_ELECTION

    num = 0
    for player in bot.ALIVE_PLAYERS:
        message += f'{num}:  {player}\n'
        num += 1
    message += '\ncommande: !vote <int>\n'
    message += 'exemple: !vote 5\n'
    await bot.HISTORY_TEXT_CHANNEL.send(message)

    await asyncio.sleep(time_left - 30)
    time_left = 30
    await bot.HISTORY_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
    await asyncio.sleep(time_left - 20)
    time_left = 20
    await bot.HISTORY_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
    await asyncio.sleep(time_left - 10)
    time_left = 10
    await bot.HISTORY_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
    await asyncio.sleep(time_left - 5)
    time_left = 5
    await bot.HISTORY_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
    await asyncio.sleep(time_left)

    # if no target
    if(len(bot.VICTIM_TARGETS) == 0):
        # no mayor choice from the players
        await bot.HISTORY_TEXT_CHANNEL.send("Vous n'avez pas choisi de victime, une nouveau lynchage va avoir lieu\n")
    else:
        targets_choice.clear()
        max_accusator = max([len(target.accusators)
                             for target in bot.VICTIM_TARGETS])
        targets_choice = [target for target in bot.VICTIM_TARGETS if len(
            target.accusators) == max_accusator]

    bot.VICTIM_TARGETS.clear()

    target_choice = None
    # draw for the votes
    if(len(targets_choice) > 1):
        # choose the target where the mayor is in accusators
        for victim_target in targets_choice:
            if(bot.MAYOR in victim_target.accusators):
                target_choice = victim_target
                break
    elif(len(targets_choice) == 1):
        target_choice = targets_choice[0]
    # else:
    # print(target_choice)
    # print(len(target_choice))
    # print("error in lynch: not len(targets_choice) > 1, not len(targets_choice) == 1")
    # raise Exception

    # if target_choice is still None then the mayor need to choose the victim
    if(target_choice == None):
        bot.MAYOR_ONLY_CHOICES = targets_choice
        target_choice = await mayor_choice(targets_choice)
        bot.MAYOR_ONLY_CHOICES.clear()
        target_choice = target_choice[0]

    bot.TURN = "FIN_VICTIME_ELECTION"

    # results
    # warn players of the choice
    await bot.HISTORY_TEXT_CHANNEL.send(f'votre choix est fait, vous avez choisi {target_choice.player}')
    await asyncio.sleep(1)
    bot.VICTIM = target_choice.player
    bot.VICTIM_TARGETS.clear()


async def mayor_choice(targets_choice):

    message = f'Le Maire a {TIME_FOR_MAYOR_FINAL_CHOICE} secondes pour choisir la victime finale\n\n'

    num = 0
    for target in targets_choice:
        message += f'{num}:  {target.player}\n'
        num += 1
    message += '\ncommande: !vote <int>\n'
    message += 'exemple: !vote 5\n'

    bot.TURN = "MAYOR_CHOICE"
    await bot.HISTORY_TEXT_CHANNEL.send(message)

    time_left = TIME_FOR_MAYOR_FINAL_CHOICE
    await asyncio.sleep(time_left - 10)
    time_left = 10
    await bot.LOUPS_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
    await asyncio.sleep(time_left - 5)
    time_left = 5
    await bot.LOUPS_TEXT_CHANNEL.send(f'{time_left} secondes restantes')
    await asyncio.sleep(time_left)

    # find the target:

    # if no target
    if(len(bot.MAYOR_CHOICES) == 0):
        # no dead from the loups
        await bot.HISTORY_TEXT_CHANNEL.send("vous n'avez pas choisi de victime")
        # choose the target randomly
        rand_index = random.randint(0, len(targets_choice) - 1)
        target_choice = targets_choice[rand_index]
    elif(len(bot.MAYOR_CHOICES) == 1):
        target_choice = bot.MAYOR_CHOICES[0]
    else:
        print("error mayor_choice: len(bot.MAYOR_CHOICES) > 0")
        raise Exception

    bot.MAYOR_CHOICES = []

    bot.TURN = "FIN_MAYOR_CHOICE"
    return target_choice


@bot.command(name='loup', help='configure le nombre de loups pour la partie')
@commands.has_role(MASTER_OF_THE_GAME)
async def assign_nb_loup(ctx, number_of_loups: int):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie créée')
        return
    if(bot.GAME_STARTED == True):
        await ctx.send('la partie a déjà commencé')
        return

    if(number_of_loups >= 0 and number_of_loups <= len(bot.PLAYERS)):
        bot.NB_LOUP = number_of_loups
        await ctx.send(f'nombre de loups:{bot.NB_LOUP}')
        # TODO: Reassign roles


@bot.command(name='min-players', help='configure le nombre de joueurs minimums pour la partie')
@commands.has_role(MASTER_OF_THE_GAME)
async def assign_min_players(ctx, min_number_of_players: int):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie créée')
        return
    if(bot.GAME_STARTED == True):
        await ctx.send('la partie a déjà commencé')
        return

    bot.MINIMUM_PLAYER_NB = min_number_of_players
    await ctx.send(f'nombre de joueurs minimum: {bot.MINIMUM_PLAYER_NB}')


async def create_game_category(ctx):
    # get guild (server)
    guild = ctx.guild

    # create the game category, it will overwrite an existing one
    category_exists = discord.utils.get(
        guild.categories, name=GAME_CATEGORY_NAME)
    if category_exists:
        await delete_game_category(ctx)
    # create a category for the game
    game_category = await guild.create_category(GAME_CATEGORY_NAME)
    bot.GAME_CATEGORY = game_category
    print(f'Creating a new category: {GAME_CATEGORY_NAME}')

    # create the history text channel
    bot.HISTORY_TEXT_CHANNEL = await game_category.create_text_channel(name=HISTORY_TEXT_CHANNEL_NAME)

    # create the game voice channel
    bot.GAME_VOICE_CHANNEL = await game_category.create_voice_channel(name=GAME_VOICE_CHANNEL_NAME)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False)
    }

    # for player in bot.LOUPS:
    #    member = player.discordMember
    #    overwrites[member] = discord.PermissionOverwrite(read_messages=True)

    # TODO: create loup garou only channel
    bot.LOUPS_TEXT_CHANNEL = await game_category.create_text_channel(LOUPS_TEXT_CHANNEL_NAME, overwrites=overwrites)

    # for each player create a secret text channel
    for player in bot.PLAYERS:
        member = player.discordMember
        # print(player.guild_permissions.administrator)
        # member = discord.utils.get(guild.members, id=player.id)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True)
        }

        if(member.guild_permissions.administrator):
            player.private_channel = await game_category.create_text_channel(PRIVATE_TEXT_CHANNEL_NAME + "_admin_" + member.display_name, overwrites=overwrites)
        else:
            player.private_channel = await game_category.create_text_channel(PRIVATE_TEXT_CHANNEL_NAME, overwrites=overwrites)
        # setattr(player,'PRIVATE_CHANNEL', private_channel)
        await player.private_channel.send(player.role.display_role())


async def assign_roles():
    nb_players = len(bot.PLAYERS)
    if(bot.NB_LOUP < nb_players):
        nb_loup = bot.NB_LOUP
    else:
        nb_loup = int(nb_players/4)
        if nb_loup == 0:
            nb_loup = 1

    roles = []

    for _ in range(nb_loup):
        roles.append(LoupGarou())

    # TODO: here add the number of the special roles
    nb_voyante = bot.NB_VOYANTE
    for _ in range(nb_voyante):
        roles.append(Voyante())

    # TODO: Here add the substraction of the nb of special role
    nb_villageois = nb_players - nb_loup - nb_voyante

    if(nb_villageois < 0):
        print('nb_villageois < 0')
        # raise ValueError

    for _ in range(nb_villageois):
        roles.append(Villageois())

    if(len(roles) != nb_players):
        print('error in assign_roles: nb_roles != nb_players')
        raise Exception

    random.shuffle(bot.PLAYERS)

    bot.LOUPS.clear()
    bot.ALIVE_PLAYERS.clear()
    for player, role in zip(bot.PLAYERS, roles):
        player.role = role
        if(isinstance(role, LoupGarou)):
            bot.LOUPS.append(player)
        # all players are now alive
        bot.ALIVE_PLAYERS.append(player)

    message = f"nombre de joueurs : {nb_players}\n"
    if(nb_loup != 0):
        message += f"loups : {nb_loup}\n"
    if(nb_villageois != 0):
        message += f"villageois\n"
    # TODO: add here for the special roles
    if(nb_voyante != 0):
        message += f"voyante\n"

    return message


async def delete_game_category(ctx):
    print(f'delete existing category {GAME_CATEGORY_NAME}')

    # get guild (server)
    guild = ctx.guild

    # delete all channels before deleting the category
    category_exists = discord.utils.get(
        guild.categories, name=GAME_CATEGORY_NAME)
    print(category_exists)
    if category_exists:
        for channel in category_exists.channels:
            await channel.delete()
        await category_exists.delete()

if __name__ == "__main__":
    bot.run(TOKEN)
