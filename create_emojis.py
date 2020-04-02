
from data_struct.bot import Bot
import constant
from data_struct.roles import *
bot = Bot()


async def create_emojis():
    with open("images/ange.png", "rb") as image:
        for guild in bot.guilds:
            exists = False
            for emoji in guild.emojis:
                if(emoji.name == "ange"):
                    exists = True
                    Ange.emoji = emoji
                    break
            if(not exists):
                Ange.emoji = await guild.create_custom_emoji(name="ange", image=bytearray(image.read()))

    with open("images/chasseur.png", "rb") as image:
        for guild in bot.guilds:
            exists = False
            for emoji in guild.emojis:
                if(emoji.name == "chasseur"):
                    exists = True
                    Chasseur.emoji = emoji
                    break
            if(not exists):
                Chasseur.emoji = await guild.create_custom_emoji(name="chasseur", image=bytearray(image.read()))
    with open("images/cupidon.png", "rb") as image:
        for guild in bot.guilds:
            exists = False
            for emoji in guild.emojis:
                if(emoji.name == "cupidon"):
                    exists = True
                    Cupidon.emoji = emoji
                    break
            if(not exists):
                Cupidon.emoji = await guild.create_custom_emoji(name="cupidon", image=bytearray(image.read()))
    with open("images/loup_garou.png", "rb") as image:
        for guild in bot.guilds:
            exists = False
            for emoji in guild.emojis:
                if(emoji.name == "loup_garou"):
                    exists = True
                    LoupGarou.emoji = emoji
                    break
            if(not exists):
                LoupGarou.emoji = await guild.create_custom_emoji(name="loup_garou", image=bytearray(image.read()))
    with open("images/loup_garou_blanc.png", "rb") as image:
        for guild in bot.guilds:
            exists = False
            for emoji in guild.emojis:
                if(emoji.name == "loup_garou_blanc"):
                    exists = True
                    LoupBlanc.emoji = emoji
                    break
            if(not exists):
                LoupBlanc.emoji = await guild.create_custom_emoji(name="loup_garou_blanc", image=bytearray(image.read()))
    with open("images/salvateur.png", "rb") as image:
        for guild in bot.guilds:
            exists = False
            for emoji in guild.emojis:
                if(emoji.name == "salvateur"):
                    exists = True
                    Salvateur.emoji = emoji
                    break
            if(not exists):
                Salvateur.emoji = await guild.create_custom_emoji(name="salvateur", image=bytearray(image.read()))
    with open("images/sorcière.png", "rb") as image:
        for guild in bot.guilds:
            exists = False
            for emoji in guild.emojis:
                if(emoji.name == "sorciere"):
                    exists = True
                    Sorcière.emoji = emoji
                    break
            if(not exists):
                Sorcière.emoji = await guild.create_custom_emoji(name="sorciere", image=bytearray(image.read()))
    with open("images/villageois.png", "rb") as image:
        for guild in bot.guilds:
            exists = False
            for emoji in guild.emojis:
                if(emoji.name == "villageois"):
                    exists = True
                    Villageois.emoji = emoji
            if(not exists):
                Villageois.emoji = await guild.create_custom_emoji(name="villageois", image=bytearray(image.read()))
    with open("images/voyante.png", "rb") as image:
        for guild in bot.guilds:
            exists = False
            for emoji in guild.emojis:
                if(emoji.name == "voyante"):
                    exists = True
                    Voyante.emoji = emoji
            if(not exists):
                Voyante.emoji = await guild.create_custom_emoji(name="voyante", image=bytearray(image.read()))
