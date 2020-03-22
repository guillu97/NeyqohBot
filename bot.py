# bot.py
import os
import random

import discord
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')


bot = commands.Bot(command_prefix='!')

MASTER_OF_THE_GAME = 'Maitre du jeu'

GAME_CATEGORY_NAME = "Neyqoh_Game"


GAME_VOICE_CHANNEL_NAME = "Place du village"

HISTORY_TEXT_CHANNEL_NAME = "Histoire"

PRIVATE_TEXT_CHANNEL_NAME = 'Ton role et actions'

bot.GAME_STARTED = False
bot.PLAYERS = []

MINIMUM_PLAYER_NB = 1


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
    #raise


@bot.command(name='99',help='Responds with a random quote from Brooklyn 99')
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

@bot.command(name='create-channel',help='create a channel')
@commands.has_role('admin')
async def create_channel(ctx, channel_name='real-python'):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)


@bot.command(name='new',help='crée une nouvelle partie')
@commands.has_role(MASTER_OF_THE_GAME)
async def new_game(ctx):
    if(bot.GAME_STARTED == False):
        await ctx.send('Nouvelle partie créée, utiliser la commande !join pour rejoindre la partie')
        bot.GAME_STARTED = True
    else:
        await ctx.send('Une partie est en cours')

@bot.command(name='join',help='rejoindre une partie')
#@commands.has_role(MASTER_OF_THE_GAME)
async def join_game(ctx):
    name = ctx.author.display_name
    print(f'{name} tried to joined')
    if(bot.GAME_STARTED == True):
        #print(ctx.__dict__)
        if ctx.author not in bot.PLAYERS:
            bot.PLAYERS.append(ctx.author)
            
            await ctx.send(f'{name} a rejoint la partie')
            nameList = []
            for player in bot.PLAYERS:
                nameList.append(player.display_name)
            await ctx.send(f'joueurs: {nameList}')
        else:
            await ctx.send(f'{name} vous êtes déjà dans la partie')
        print(nameList)

        #if(bot.PLAYERS):
    else:
        await ctx.send(f'aucune partie en cours')
    

@bot.command(name='stop',help='stop la partie en cours')
@commands.has_role(MASTER_OF_THE_GAME)
async def stop_game(ctx):
    if(bot.GAME_STARTED == True):
        await ctx.send('arret de la partie en cours')
        await delete_game_category(ctx)
        bot.GAME_STARTED = False
        bot.PLAYERS.clear()
    else:
        await ctx.send('aucune partie en cours')
    

@bot.command(name='start',help='commence la partie avec toutes les personnes ayant effectué !join')
@commands.has_role(MASTER_OF_THE_GAME)
async def start_game(ctx):
    if(bot.GAME_STARTED == True):
        if(len(bot.PLAYERS) >= MINIMUM_PLAYER_NB):
            await ctx.send('la partie commence!')
            await create_game_category(ctx)
            guild = ctx.guild
            game_voice_channel = bot.GAME_VOICE_CHANNEL

            # move the player to the game voice channel
            for player in bot.PLAYERS:
                print(player)
                try:
                    await player.move_to(game_voice_channel)
                except Exception as e:
                    print(e)
        else:
            await ctx.send(f"le nombre minimum de joueurs ({MINIMUM_PLAYER_NB}) n'est pas atteint")
    else:
        await ctx.send('aucune partie créée')

    #beginningChannel = None
    # search for the beginning voice channel
    #discord.utils.get(guild.categories, name=GAME_CATEGORY_NAME)
    #print(beginningChannel.members)



async def create_game_category(ctx):
    # get guild (server)
    guild = ctx.guild

    # create the game category, it will overwrite an existing one
    category_exists = discord.utils.get(guild.categories, name=GAME_CATEGORY_NAME)
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

    # TODO: attribute roles to all the people register in the game

    # for each player create a secret text channel
    for player in bot.PLAYERS:
        #print(player.guild_permissions.administrator)
        #member = discord.utils.get(guild.members, id=player.id)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            player: discord.PermissionOverwrite(read_messages=True)
        }
        if(player.guild_permissions.administrator):
            private_channel = await game_category.create_text_channel(PRIVATE_TEXT_CHANNEL_NAME + "_admin_" + player.display_name, overwrites=overwrites)
        else:
            private_channel = await game_category.create_text_channel(PRIVATE_TEXT_CHANNEL_NAME, overwrites=overwrites)
        #setattr(player,'PRIVATE_CHANNEL', private_channel)
        await private_channel.send(player.name)

async def delete_game_category(ctx):
    print(f'delete existing category {GAME_CATEGORY_NAME}')

    # get guild (server)
    guild = ctx.guild

    # delete all channels before deleting the category
    category_exists = discord.utils.get(guild.categories, name=GAME_CATEGORY_NAME)
    print(category_exists)
    if category_exists:
        for channel in category_exists.channels:
            await channel.delete()
        await category_exists.delete()

if __name__ == "__main__":
    bot.run(TOKEN)