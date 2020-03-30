# main.py
from data_struct.singleton import Singleton

import constant

import easter_eggs
import events
import commands.master_commands
import commands.players_commands

bot = Singleton()

if __name__ == "__main__":
    bot.run(constant.TOKEN)
