
# importing os module
import os
from data_struct.bot import Bot
import constant
from data_struct.roles import *
from data_struct import roles

bot = Bot()


async def create_emojis():
    images_root_path = "images"
    all_roles = roles.IMPLEMENTED_ROLES[:]
    all_roles.append(Mayor())
    for role in all_roles:
        emoji_name = role.image_filename.replace(".png", "")
        with open(os.path.join(images_root_path, role.image_filename), "rb") as image:
            for guild in bot.guilds:
                exists = False
                for emoji in guild.emojis:
                    if(emoji.name == emoji_name):
                        exists = True
                        role.__class__.emoji = emoji
                        break
                if(not exists):
                    role.__class__.emoji = await guild.create_custom_emoji(name=emoji_name, image=bytearray(image.read()))