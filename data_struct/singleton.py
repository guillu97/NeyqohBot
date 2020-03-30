import discord
from discord.ext import commands

import constant


class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
            cls._instance = commands.Bot(
                command_prefix=constant.COMMANDS_PREFIX)
            cls.default_values(cls._instance)
            cls._instance.default_values = cls.default_values

        return cls._instance


    def default_values(_instance):
        _instance.GAME_CREATED = False
        _instance.GAME_STARTED = False
        _instance.PLAYERS = []
        _instance.DEADS_OF_NIGHT = []
        _instance.DEADS_OF_DAY = []
        _instance.DEADS = []
        _instance.LOUPS = []
        _instance.ALIVE_PLAYERS = []
        _instance.LOUP_TARGETS = []
        _instance.MAYOR_TARGETS = []
        _instance.MAYOR_CHOICES = []
        _instance.MAYOR_ONLY_CHOICES = []
        _instance.VICTIM_TARGETS = []
        _instance.AMOUREUX = []
        # _instance.SORCIERE_SAVE = False
        # _instance.SORCIERE_KILL = None
        _instance.WINNER = None
        _instance.LOUP_FINAL_TARGET = None
        _instance.MAYOR = None
        _instance.VICTIM = None
        _instance.MINIMUM_PLAYER_NB = constant.MINIMUM_PLAYER_NB
        _instance.NB_LOUP = constant.DEFAULT_NB_LOUP
        _instance.NB_LOUP_BLANC = constant.DEFAULT_NB_LOUP_BLANC
        _instance.NB_CUPIDON = constant.DEFAULT_NB_CUPIDON
        _instance.NB_VOYANTE = constant.DEFAULT_NB_VOYANTE
        _instance.NB_SORCIERE = constant.DEFAULT_NB_SORCIERE
        _instance.NB_CHASSEUR = constant.DEFAULT_NB_CHASSEUR
        _instance.NB_ANGE = 0
        _instance.ALLOW_MORE_ROLES = False
        _instance.NB_NIGHTS = 1
        _instance.TURN = ""
        # _instance.PAUSE = False
