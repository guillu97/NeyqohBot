# main.py
from data_struct.bot import Bot

import constant

import easter_eggs
import events
import commands.master_commands
import commands.players_commands

bot = Bot()


if __name__ == "__main__":
    bot.run(constant.TOKEN)
