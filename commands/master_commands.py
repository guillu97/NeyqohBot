
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

    bot.PLAYERS.append(Player(ctx.author))
    bot.GAME_CREATED = True

    message = 'Nouvelle partie créée, utiliser la commande !join pour rejoindre la partie\n\n'
    message += f'{ctx.author.display_name} a rejoint la partie\n\n'
    message += f'joueurs: {" ".join(map(str,bot.PLAYERS))}\n'
    await ctx.send(message)

    # save the channel where the new was typed
    bot.BEGINNING_CHANNEL = ctx.message.channel


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
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie créée')
        return

    if(len(bot.PLAYERS) < bot.MINIMUM_PLAYER_NB):
        await ctx.send(f"le nombre minimum de joueurs ({bot.MINIMUM_PLAYER_NB}) n'est pas atteint")
        return

    if(not bot.ALLOW_MORE_ROLES):
        roles = await calc_roles(verbose=False)
        if(roles == None):
            await ctx.send('\n**Le nombre de roles est supérieur au nombre de joueurs**\n')
            return

    await ctx.send('la partie commence!')

    bot.GAME_STARTED = True

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
    bot.GAME_LOOP = asyncio.get_running_loop()

    await game_process(ctx)

    # beginningChannel = None
    # search for the beginning voice channel
    # discord.utils.get(guild.categories, name=constant.GAME_CATEGORY_NAME)
    # print(beginningChannel.members)


@bot.command(name='loup', help='configure le nombre de loups pour la partie')
@commands.has_role(constant.MASTER_OF_THE_GAME)
async def assign_nb_loup(ctx, number_of_loups: int):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie créée')
        return
    if(bot.GAME_STARTED == True):
        await ctx.send('la partie a déjà commencé')
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
        await ctx.send('aucune partie créée')
        return
    if(bot.GAME_STARTED == True):
        await ctx.send('la partie a déjà commencé')
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
        await ctx.send('aucune partie créée')
        return
    if(bot.GAME_STARTED == True):
        await ctx.send('la partie a déjà commencé')
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
        await ctx.send('aucune partie créée')
        return
    if(bot.GAME_STARTED == True):
        await ctx.send('la partie a déjà commencé')
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
        await ctx.send('aucune partie créée')
        return
    if(bot.GAME_STARTED == True):
        await ctx.send('la partie a déjà commencé')
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
        await ctx.send('aucune partie créée')
        return
    if(bot.GAME_STARTED == True):
        await ctx.send('la partie a déjà commencé')
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
        await ctx.send('aucune partie créée')
        return
    if(bot.GAME_STARTED == True):
        await ctx.send('la partie a déjà commencé')
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
        await ctx.send('aucune partie créée')
        return
    if(bot.GAME_STARTED == True):
        await ctx.send('la partie a déjà commencé')
        return
    roles = await calc_roles(verbose=True)
    print(roles)
    message = f'\n{roles}\n'
    await ctx.send(message)


@bot.command(name='allow-more-roles', help="autorise le fait d'ajouter plus de roles que de joueurs présents dans la partie")
@commands.has_role(constant.MASTER_OF_THE_GAME)
async def allow_more_roles(ctx, boolean: bool):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie créée')
        return
    if(bot.GAME_STARTED == True):
        await ctx.send('la partie a déjà commencé')
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
        await ctx.send('aucune partie créée')
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
        await ctx.send('aucune partie créée')
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
        await ctx.send('aucune partie créée')
        return
    if(bot.GAME_STARTED == True):
        await ctx.send('la partie a déjà commencé')
        return

    bot.MINIMUM_PLAYER_NB = min_number_of_players
    await ctx.send(f'nombre de joueurs minimum: {bot.MINIMUM_PLAYER_NB}')


@bot.command(name='test', help='test')
@commands.has_role(constant.MASTER_OF_THE_GAME)
async def test(ctx):
    if(bot.GAME_CREATED == False):
        await ctx.send('aucune partie créée')
        return
    """if(bot.GAME_STARTED == True):
        await ctx.send("la partie a déjà commencé")
        return"""

    targets_choice = await vote(ctx, bot.PLAYERS, "👎", 10)

    target_choice = None
    if(len(targets_choice) == 1):
        target_choice = targets_choice[0]

    if(target_choice != None):
        await ctx.send(f'**{target_choice.nb_accusators()}** votes pour **{target_choice.player}**: | *{"* | *".join(map(str,target_choice.accusators))}* |')
    else:
        await ctx.send(f"vous n'avez pas fait de choix")


async def check_multiple_votes(ctx, context_messages, emoji, players):
    # check nb reactions per player
    # => should be 0 at the beginning
    # => to be sure => remove all reactions except from me

    # playerReacts = {player: Reaction}  # a dict associating the player to the only reaction he has
    playerReacts = {}
    for player in players:
        playerReacts[player.discordMember] = None

    ids = [message.id for message in context_messages]
    async for message in ctx.channel.history(limit=100):
        if message.id in ids:
            if(len(message.reactions) != 1):
                await message.clear_reactions()
                await message.add_reaction(emoji=emoji)

    while(True):
        # print("check running")
        # check again the nb of reactions per player
        # if before it was 0  => don't remove the reaction
        # if it was not 0 => remove the old reaction and let the new reaction

        async for message in ctx.channel.history(limit=100):
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


async def timer(ctx, time):
    time_message = await ctx.send(f'*temps restant: {time}*')
    for i in range(1, time+1):
        await asyncio.sleep(1)
        await time_message.edit(content=str(f'*temps restant: {time-i}*'))
    # print("timer finished")


async def vote(ctx, players, emoji, time):  # @return [] or a list of TargetEmoji
    messages = []
    for player in players:
        message = await ctx.send(f'{player.discordMember.mention}')
        await message.add_reaction(emoji=emoji)
        messages.append(message)
    ids = [message.id for message in messages]

    # start the task check of multiple reactions
    task_msg_check = asyncio.create_task(
        check_multiple_votes(ctx, messages, emoji, players))
    # start timer message
    await timer(ctx, time)

    # not accepting the other emojis
    for player in players:
        await ctx.channel.set_permissions(
            player.discordMember, add_reactions=False, send_messages=False, read_messages=False)
    # wait synchronisation of the reaction changes
    await asyncio.sleep(1)
    # stop the task check of multiple reactions
    task_msg_check.cancel()

    # target = {player: [accusators:Player]}
    # emojisCount = {}
    targets_choice = []
    possible_accusators = players[:]
    async for message in ctx.channel.history(limit=100):
        if message.id in ids:
            # with the mention get back the player
            current_player = None
            for player in players:
                if(player.discordMember.mentioned_in(message)):
                    current_player = player
                    break
            if(current_player != None):
                accusators = []
                for reaction in message.reactions:
                    if(reaction.emoji == emoji):
                        users = reaction.users()
                        users = await users.flatten()
                        users_without_me = [
                            user for user in users if not user.bot]  # debug this
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

    # accepting the other emojis
    for player in players:
        await ctx.channel.set_permissions(
            player.discordMember, add_reactions=True, send_messages=True, read_messages=True)

    return targets_choice
