import os
import discord
from discord.ext import commands
import constant
from data_struct.bot import Bot

bot = Bot()


async def create_game_category(ctx):

    # get guild (server)
    guild = ctx.guild

    # create the game category, it will overwrite an existing one
    category_exists = discord.utils.get(
        guild.categories, name=constant.GAME_CATEGORY_NAME)
    if category_exists:
        await delete_game_category(ctx)
    # create a category for the game
    game_category = await guild.create_category(constant.GAME_CATEGORY_NAME)
    bot.GAME_CATEGORY = game_category
    print(f'Creating a new category: {constant.GAME_CATEGORY_NAME}')

    # create the history text channel
    bot.HISTORY_TEXT_CHANNEL = await game_category.create_text_channel(name=constant.HISTORY_TEXT_CHANNEL_NAME)

    # create the game voice channel
    bot.GAME_VOICE_CHANNEL = await game_category.create_voice_channel(name=constant.GAME_VOICE_CHANNEL_NAME)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False)
    }

    # for player in bot.LOUPS:
    #    member = player.discordMember
    #    overwrites[member] = discord.PermissionOverwrite(read_messages=True)

    bot.LOUPS_TEXT_CHANNEL = await game_category.create_text_channel(constant.LOUPS_TEXT_CHANNEL_NAME, overwrites=overwrites)

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
            player.private_channel = await game_category.create_text_channel(constant.PRIVATE_TEXT_CHANNEL_NAME + "_admin_" + member.display_name, overwrites=overwrites)
        else:
            player.private_channel = await game_category.create_text_channel(constant.PRIVATE_TEXT_CHANNEL_NAME, overwrites=overwrites)
        # setattr(player,'PRIVATE_CHANNEL', private_channel)
        print(player)
        await player.private_channel.send(file=discord.File(os.path.join('images', player.role.image_filename)))
        await player.private_channel.send(player.role.display_role())


async def delete_game_category(ctx):
    print(f'delete existing category {constant.GAME_CATEGORY_NAME}')

    # get guild (server)
    guild = ctx.guild

    # delete all channels before deleting the category
    category_exists = discord.utils.get(
        guild.categories, name=constant.GAME_CATEGORY_NAME)
    print(category_exists)
    if category_exists:
        for channel in category_exists.channels:
            await channel.delete()
        await category_exists.delete()
