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


bot = commands.Bot(command_prefix='!')

MASTER_OF_THE_GAME = 'Maitre du jeu'

GAME_CATEGORY_NAME = "Neyqoh_Game"
GAME_VOICE_CHANNEL_NAME = "Place du village"
HISTORY_TEXT_CHANNEL_NAME = "Histoire"
PRIVATE_TEXT_CHANNEL_NAME = 'Ton role et actions'
LOUPS_TEXT_CHANNEL_NAME = 'Loups Garous'

TIME_FOR_ROLES = 10
TIME_FOR_LOUPS = 30
TIME_FOR_MAYOR_ELECTION = 120

TIME_AUTO_DESTRUCT = 10  # TODO: 30 in prod

NB_MAX_MAYOR_ELECTIONS = 3


bot.GAME_CREATED = False
bot.GAME_STARTED = False
bot.PLAYERS = []
bot.DEADS = []
bot.LOUPS = []
bot.ALIVE_PLAYERS = []
bot.LOUP_TARGETS = []
bot.MAYOR_TARGETS = []

bot.WINNER = None

bot.MAYOR = None

bot.LOUP_FINAL_TARGET = None

bot.MINIMUM_PLAYER_NB = 4  # TODO: in prod : 4 players min

bot.NB_LOUP = 2

bot.NB_NIGHTS = 1

bot.TURN = ""


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

    roles = assign_roles()
    print(roles)

    message = f'{name} a rejoint la partie\n\n'
    message += f'joueurs: {nameList}\n\n'
    message += f'{roles}\n'
    await ctx.send(message)

    print(nameList)


@bot.command(name='stop', help='stop la partie en cours')
@commands.has_role(MASTER_OF_THE_GAME)
async def stop_game(ctx):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie en cours')
        return

    await ctx.send('arret de la partie en cours')
    await delete_game_category(ctx)
    bot.GAME_CREATED = False
    bot.GAME_STARTED = False
    bot.PLAYERS.clear()
    bot.ALIVE_PLAYERS.clear()
    bot.LOUPS.clear()
    bot.LOUP_TARGETS.clear()
    bot.DEADS.clear()
    bot.NB_NIGHTS = 1


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

        ### wake loups ###
        await loups_turn()

        ### wake villageois ###
        await bot.HISTORY_TEXT_CHANNEL.send('Le village se réveille')
        bot.TURN = "DAY"

        ### compute deads ###
        if(bot.LOUP_FINAL_TARGET != None):
            bot.DEADS.append(bot.LOUP_FINAL_TARGET)

        ### display the night deads ###
        message = ""
        if(len(bot.DEADS) == 0):
            message += "personne n'est mort ce soir"
        else:
            for player in bot.DEADS:
                message += f"{player} est mort ce soir, son role : {player.role}\n"
        await bot.HISTORY_TEXT_CHANNEL.send(message)

        ### remove dead players from alive table ###
        index = 0
        for player in bot.DEADS:
            if(player in bot.ALIVE_PLAYERS):
                bot.ALIVE_PLAYERS.remove(player)
            index += 1
        # the loup final_target can be reset to None
        bot.LOUP_FINAL_TARGET = None

        ### display deads ###
        message = "\nmorts:\n"
        for player in bot.DEADS:
            message += f"{player}: {player.role}\n"

        ### display alive ###
        message += "\nvivants:\n"
        for player in bot.ALIVE_PLAYERS:
            message += f"{player}\n"

        ### display roles in games ###
        message += "\nroles restants:\n"
        roles = [player.role for player in bot.ALIVE_PLAYERS]
        random.shuffle(roles)
        for role in roles:
            message += f'{role}\n'
        await bot.HISTORY_TEXT_CHANNEL.send(message)

        ### check someone wins or draw ###
        if(len(bot.ALIVE_PLAYERS) == 1):
            bot.WINNER = bot.ALIVE_PLAYERS[0].role
            break

        ### vote for maire ###
        if(bot.MAYOR == None):
            await election()

        ### vote for day kill ###
        bot.TURN = "LINCHAGE"

        ### display kill of the day ###

        bot.NB_NIGHTS += 1

    ### display winners ###
    message = f"{bot.WINNER} a gagné après la nuit {bot.NB_NIGHTS}\n\n"
    message += f"Les channels vont s'auto-détruire dans {TIME_AUTO_DESTRUCT} secondes\n"
    await bot.HISTORY_TEXT_CHANNEL.send(message)

    await asyncio.sleep(TIME_AUTO_DESTRUCT)
    await delete_game_category(ctx)


@bot.command(name='vote', help='vote pendant la partie')
# @commands.has_role(MASTER_OF_THE_GAME)
async def vote(ctx, choice: int):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie créée')
        return
    if(bot.GAME_STARTED == False):
        await ctx.send("la partie n'a pas commencé")
        return

    # if vote during TURN="LOUPS"
    if(bot.TURN == "LOUPS"):
        # if vote dans channel loup
        if(ctx.message.channel == bot.LOUPS_TEXT_CHANNEL):
            # if choice is valid
            if(choice >= 0 and choice < len(bot.ALIVE_PLAYERS)):
                # search for the player in bot.ALIVE_PLAYERS with ctx.message.author
                currentPlayer = None
                for player in bot.ALIVE_PLAYERS:
                    if(player.discordMember == ctx.message.author):
                        currentPlayer = player
                        break
                if(currentPlayer == None):
                    print('error: current player is not in the alive players')
                    raise Exception

                await vote_mecanism(ctx, choice, currentPlayer, bot.LOUPS_TEXT_CHANNEL, bot.LOUP_TARGETS)

    if(bot.TURN == "MAYOR_ELECTION"):
        # if choice is valid
        if(choice >= 0 and choice < len(bot.ALIVE_PLAYERS)):
            # search for the player in bot.ALIVE_PLAYERS with ctx.message.author
            currentPlayer = None
            for player in bot.ALIVE_PLAYERS:
                if(player.discordMember == ctx.message.author):
                    currentPlayer = player
                    break
            if(currentPlayer == None):
                print('error: current player is not in the alive players')
                raise Exception

            await vote_mecanism(ctx, choice, currentPlayer, bot.HISTORY_TEXT_CHANNEL, bot.MAYOR_TARGETS)


async def vote_mecanism(ctx, choice, currentPlayer, channel, targets_table):
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

    message = ""
    for target in targets_table:
        message += f"{target}\n"
    await channel.send(message)


async def election():

    # find the target:
    # print(bot.LOUP_TARGETS)
    counter_max_elections = NB_MAX_MAYOR_ELECTIONS
    targets_choice = []
    while(len(targets_choice) != 1 or counter_max_elections > 0):

        ### warn village ###
        message = f'Les villageois ont {TIME_FOR_MAYOR_ELECTION} secondes pour choisir le maire:\n\n'
        await bot.HISTORY_TEXT_CHANNEL.send(message)
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
            await bot.HISTORY_TEXT_CHANNEL.send("Vous n'avez pas choisi de maire, une nouvelle election va avoir lieu\n")
        else:
            targets_choice.clear()
            max_accusator = max([len(target.accusators)
                                 for target in bot.MAYOR_TARGETS])
            targets_choice = [target for target in bot.MAYOR_TARGETS if len(
                target.accusators) == max_accusator]

        bot.MAYOR_TARGETS.clear()

        counter_max_elections -= 1

    # draw for the votes
    if(len(targets_choice) > 1):
        # choose the target randomly
        rand_index = random.randint(0, len(targets_choice) - 1)
        target_choice = targets_choice[rand_index]
    elif(len(targets_choice) == 1):
        target_choice = targets_choice[0]
    else:
        raise Exception

    bot.TURN = "FIN_MAYOR_ELECTION"

    # results
    # warn players of the choice
    await bot.HISTORY_TEXT_CHANNEL.send(f'votre choix est fait, vous avez choisi {target_choice.player}')
    await asyncio.sleep(1)
    bot.MAYOR = target_choice.player
    bot.MAYOR_TARGETS.clear()


async def loups_turn():

    # warn village
    await bot.HISTORY_TEXT_CHANNEL.send(f'Les loups garous ont {TIME_FOR_LOUPS} secondes pour choisir leur victime de la nuit:\n\n')
    bot.TURN = "LOUPS"

    # make channel accessible
    for player in bot.LOUPS:
        member = player.discordMember
        #overwrites[member] = discord.PermissionOverwrite(read_messages=True)
        await bot.LOUPS_TEXT_CHANNEL.set_permissions(
            member, send_messages=True, read_messages=True)

    # warn loups garou
    message = f'Vous avez {TIME_FOR_LOUPS} secondes pour choisir votre victime de la nuit:\n\n'
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
            raise Exception

        bot.TURN = "FIN_LOUPS"

        # make channel inacessible in write only
        for player in bot.LOUPS:
            member = player.discordMember
            #overwrites[member] = discord.PermissionOverwrite(read_messages=True)
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
        #overwrites[member] = discord.PermissionOverwrite(read_messages=True)
        await bot.LOUPS_TEXT_CHANNEL.set_permissions(
            member, send_messages=False, read_messages=False)


@bot.command(name='loup', help='configure le nombre de loups pour la partie')
@commands.has_role(MASTER_OF_THE_GAME)
async def assign_nb_loup(ctx, number_of_loups: int):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie créée')
        return
    if(bot.GAME_STARTED == True):
        await ctx.send('la partie a déjà commencé')
        return

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


def assign_roles():
    nb_players = len(bot.PLAYERS)
    if(bot.NB_LOUP < nb_players):
        nb_loup = bot.NB_LOUP
    else:
        nb_loup = int(nb_players/4)
        if nb_loup == 0:
            nb_loup = 1
    # TODO: here add the number of the special roles

    roles = []

    for _ in range(nb_loup):
        roles.append(LoupGarou())

    # TODO: Here add the substraction of the nb of special role
    nb_villageois = nb_players - nb_loup

    for _ in range(nb_villageois):
        roles.append(Villageois())

    if(len(roles) != nb_players):
        print('error nb_roles != nb_players')
        raise Exception

    random.shuffle(roles)

    bot.LOUPS.clear()
    bot.ALIVE_PLAYERS.clear()
    for player, role in zip(bot.PLAYERS, roles):
        player.role = role
        if(isinstance(role, LoupGarou)):
            bot.LOUPS.append(player)
        # all players are now alive
        bot.ALIVE_PLAYERS.append(player)

    message = f"nombre de joueurs : {nb_players}\n"
    message += f"loups : {nb_loup}\n"
    message += f"villageois : {nb_villageois}\n"

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
