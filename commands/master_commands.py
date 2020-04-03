
from discord.ext import commands
from discord import Emoji
from discord import *
import random
import asyncio
import constant
from channels_process import create_game_category, delete_game_category
from roles_compute import calc_roles, assign_roles
from game_process import game_process, stop_game
from data_struct.player import Player
from data_struct.bot import Bot
from data_struct.roles import *
from data_struct.target import TargetEmoji
from vote import vote
from join import joining_process, check_start

bot = Bot()


@bot.command(name='new', help='crée une nouvelle partie')
@commands.has_role(constant.MASTER_OF_THE_GAME)
async def new_game(ctx):
    if(bot.GAME_CREATED == True):
        await ctx.send('Une partie est déjà créée')
        return
    if(bot.GAME_STARTED == True):
        await ctx.send('Une partie est déjà en cours')
        return

    # save the channel where the new was typed
    bot.BEGINNING_CHANNEL = ctx.channel

    bot.GAME_CREATED = True

    await ctx.send('Nouvelle partie créée!\n\n')

    # choose roles
    # await choose_roles()

    # joining loop witing for the MASTER_OF_THE_GAME to  input !start ###
    # this will fill bot.PLAYERS
    await joining_process(channel=ctx.channel, emoji="👍")
    await ctx.send('la partie commence!')

    await assign_roles()

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

    # get the game loop
    #bot.GAME_LOOP = asyncio.get_running_loop()

    await game_process(ctx)


@bot.command(name='stop', help='stop la partie en cours')
@commands.has_role(constant.MASTER_OF_THE_GAME)
async def command_stop_game(ctx):
    await stop_game(ctx)


@bot.command(name='delete', help="supprime les categrory du jeu si aucune partie n'est en cours")
@commands.has_role(constant.MASTER_OF_THE_GAME)
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
@commands.has_role(constant.MASTER_OF_THE_GAME)
async def start_game(ctx):
    await check_start(ctx.channel)


@bot.command(name='loup', help='configure le nombre de loups pour la partie')
@commands.has_role(constant.MASTER_OF_THE_GAME)
async def assign_nb_loup(ctx, number_of_loups: int):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie créée', delete_after=2)
        return
    if(bot.ROLES_CHOOSEN == True and bot.GAME_STARTED == True):
        await ctx.send('la partie a déjà commencé', delete_after=2)
        return

    if(number_of_loups > 0):
        print(number_of_loups)
        if(not bot.ALLOW_MORE_ROLES):
            if(number_of_loups < len(bot.PLAYERS)):
                bot.NB_LOUP = number_of_loups
                roles = await calc_roles(verbose=True)
                print(roles)
                message = f'\n{roles}\n'
                await ctx.send(message)
            else:
                await ctx.send('nombre de loup > ou = au nombre de joueurs')
        else:
            bot.NB_LOUP = number_of_loups
            roles = await calc_roles(verbose=True)
            print(roles)
            message = f'\n{roles}\n'
            await ctx.send(message)


@bot.command(name='loupBlanc', help="configure le nombre de loup-garou blanc pour la partie: 0 ou 1")
@commands.has_role(constant.MASTER_OF_THE_GAME)
async def assign_nb_loupBlanc(ctx, number_of: int):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie créée', delete_after=2)
        return
    if(bot.ROLES_CHOOSEN == True and bot.GAME_STARTED == True):
        await ctx.send('la partie a déjà commencé', delete_after=2)
        return

    if(number_of == 0 or number_of == 1):
        bot.NB_LOUP_BLANC = number_of
        roles = await calc_roles(verbose=True)
        print(roles)
        message = f'\n{roles}\n'
        await ctx.send(message)


@bot.command(name='ange', help="configure le nombre d'ange pour la partie: 0 ou 1")
@commands.has_role(constant.MASTER_OF_THE_GAME)
async def assign_nb_ange(ctx, number_of: int):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie créée', delete_after=2)
        return
    if(bot.ROLES_CHOOSEN == True and bot.GAME_STARTED == True):
        await ctx.send('la partie a déjà commencé', delete_after=2)
        return

    if(number_of >= 0 and number_of <= constant.MAX_NB_ANGE):
        bot.NB_ANGE = number_of
        roles = await calc_roles(verbose=True)
        print(roles)
        message = f'\n{roles}\n'
        await ctx.send(message)


@bot.command(name='voyante', help="configure le nombre de voyantes pour la partie (0 ou plus)")
@commands.has_role(constant.MASTER_OF_THE_GAME)
async def assign_nb_voyante(ctx, number_of: int):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie créée', delete_after=2)
        return
    if(bot.ROLES_CHOOSEN == True and bot.GAME_STARTED == True):
        await ctx.send('la partie a déjà commencé', delete_after=2)
        return

    if(number_of >= 0 and number_of <= len(bot.PLAYERS)):
        bot.NB_VOYANTE = number_of
        roles = await calc_roles(verbose=True)
        print(roles)
        message = f'\n{roles}\n'
        await ctx.send(message)


@bot.command(name='sorcière', help="configure le nombre de sorcières pour la partie (0 ou plus)")
@commands.has_role(constant.MASTER_OF_THE_GAME)
async def assign_nb_sorcière(ctx, number_of: int):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie créée', delete_after=2)
        return
    if(bot.ROLES_CHOOSEN == True and bot.GAME_STARTED == True):
        await ctx.send('la partie a déjà commencé', delete_after=2)
        return

    if(number_of >= 0 and number_of <= len(bot.PLAYERS)):
        bot.NB_SORCIERE = number_of
        roles = await calc_roles(verbose=True)
        print(roles)
        message = f'\n{roles}\n'
        await ctx.send(message)


@bot.command(name='chasseur', help="configure le nombre de chasseurs pour la partie (0 ou 1)")
@commands.has_role(constant.MASTER_OF_THE_GAME)
async def assign_nb_chasseur(ctx, number_of: int):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie créée', delete_after=2)
        return
    if(bot.ROLES_CHOOSEN == True and bot.GAME_STARTED == True):
        await ctx.send('la partie a déjà commencé', delete_after=2)
        return

    if(number_of == 0 or number_of == 1):
        bot.NB_CHASSEUR = number_of
        roles = await calc_roles(verbose=True)
        print(roles)
        message = f'\n{roles}\n'
        await ctx.send(message)


@bot.command(name='cupidon', help="configure le nombre de cupidon pour la partie (0 ou 1)")
@commands.has_role(constant.MASTER_OF_THE_GAME)
async def assign_nb_cupidon(ctx, number_of: int):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie créée', delete_after=2)
        return
    if(bot.ROLES_CHOOSEN == True and bot.GAME_STARTED == True):
        await ctx.send('la partie a déjà commencé', delete_after=2)
        return

    if(number_of == 0 or number_of == 1):
        bot.NB_CUPIDON = number_of
        roles = await calc_roles(verbose=True)
        print(roles)
        message = f'\n{roles}\n'
        await ctx.send(message)


@bot.command(name='roles', help="montre les roles choisis pour la partie")
@commands.has_role(constant.MASTER_OF_THE_GAME)
async def show_roles(ctx):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie créée', delete_after=2)
        return
    if(bot.ROLES_CHOOSEN == True and bot.GAME_STARTED == True):
        await ctx.send('la partie a déjà commencé', delete_after=2)
        return
    roles = await calc_roles(verbose=True)
    print(roles)
    message = f'\n{roles}\n'
    await ctx.send(message)


@bot.command(name='allow-more-roles', help="autorise le fait d'ajouter plus de roles que de joueurs présents dans la partie")
@commands.has_role(constant.MASTER_OF_THE_GAME)
async def allow_more_roles(ctx, boolean: bool):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie créée', delete_after=2)
        return
    if(bot.ROLES_CHOOSEN == True and bot.GAME_STARTED == True):
        await ctx.send('la partie a déjà commencé', delete_after=2)
        return

    bot.ALLOW_MORE_ROLES = boolean
    if(boolean):
        await ctx.send("il est autorisé d'ajouter plus de roles que de joueurs présents dans la partie")
    else:
        await ctx.send("il n'est pas autorisé d'ajouter plus de roles que de joueurs présents dans la partie")


@bot.command(name='pause', help="met en pause le bot pendant un nombre de secondes donné")
@commands.has_role(constant.MASTER_OF_THE_GAME)
async def timed_pause_game(ctx, pause_time: int = 30):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie créée', delete_after=2)
        return
    if(bot.GAME_STARTED == False):
        await ctx.send("la partie n'a pas encore commencé")
        return

    if(ctx.channel != bot.HISTORY_TEXT_CHANNEL):
        await bot.HISTORY_TEXT_CHANNEL.send(f"\n\n**Le bot est en pause pendant {pause_time} secondes**\n\n")
    await ctx.send(f"\n\n**La bot est en pause pendant {pause_time} secondes**\n\n")

    time.sleep(pause_time)

    if(ctx.channel != bot.HISTORY_TEXT_CHANNEL):
        await bot.HISTORY_TEXT_CHANNEL.send(f"\n\n**Le bot n'est plus en pause**\n\n")
    await ctx.send(f"\n\n**Le bot n'est plus en pause**\n\n")

    # msg = await bot.wait_for('message', check=lambda message: message.author == ctx.author)


"""
@bot.command(name='resume', help="continue la partie s'il y avait une pause")
@commands.has_role(constant.MASTER_OF_THE_GAME)
async def pause_game(ctx):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie créée', delete_after=2)
        return
    if(bot.GAME_STARTED == False):
        await ctx.send("la partie n'a pas encore commencé")
        return
    if(bot.PAUSE == False):
        await ctx.send("la partie n'est pas en pause")
        return

    bot.PAUSE = False
    if(ctx.channel != bot.HISTORY_TEXT_CHANNEL):
        await bot.HISTORY_TEXT_CHANNEL.send("\n\n**La partie continue**\n\n")
    await ctx.send("\n\n**La partie continue**\n\n")
"""


@bot.command(name='min-players', help='configure le nombre de joueurs minimums pour la partie')
@commands.has_role(constant.MASTER_OF_THE_GAME)
async def assign_min_players(ctx, min_number_of_players: int):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie créée', delete_after=2)
        return
    if(bot.ROLES_CHOOSEN == True and bot.GAME_STARTED == True):
        await ctx.send('la partie a déjà commencé', delete_after=2)
        return

    bot.MINIMUM_PLAYER_NB = min_number_of_players
    await ctx.send(f'nombre de joueurs minimum: {bot.MINIMUM_PLAYER_NB}')


@bot.command(name='test', help="test du système de vote")
@commands.has_role(constant.MASTER_OF_THE_GAME)
async def test(ctx):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie créée', delete_after=2)
        return
    """if(bot.GAME_STARTED == True):
        await ctx.send("la partie a déjà commencé")
        return"""

    targets_choice = await vote(channel=ctx.channel, target_players=bot.PLAYERS, voters=bot.PLAYERS, emoji="👎", time=10)

    target_choice = None
    if(len(targets_choice) == 1):
        target_choice = targets_choice[0]

    if(target_choice != None):
        await ctx.send(f'**{target_choice.nb_accusators()}** votes pour **{target_choice.player}**: | *{"* | *".join(map(str,target_choice.accusators))}* |')
    else:
        await ctx.send(f"vous n'avez pas fait de choix")


@bot.command(name='reset-perm', help="met les permissions d'envoi de messages et de reaction de tous les membres à True")
@commands.has_role(constant.MASTER_OF_THE_GAME)
async def reset_permissions(ctx):
    for member in ctx.channel.guild.members:
        await ctx.channel.set_permissions(
            member, add_reactions=True, send_messages=True, read_messages=True)
    await ctx.send("permissions reset")
