import os
from dotenv import load_dotenv
from data_struct.roles import *

### CONSTANTS ###

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

COMMANDS_PREFIX = "!"

MASTER_OF_THE_GAME = 'Maitre du jeu'

IMPLEMENTED_ROLES = [Villageois, Voyante, Sorcière,
                     Chasseur, Ange, Cupidon, LoupGarou, LoupBlanc]

GAME_CATEGORY_NAME = "Neyqoh_Game"
GAME_VOICE_CHANNEL_NAME = "Place du village"
TEMP_VOICE_CHANNEL_NAME = "Voice"
HISTORY_TEXT_CHANNEL_NAME = "Histoire"
PRIVATE_TEXT_CHANNEL_NAME = 'Ton role et actions'
LOUPS_TEXT_CHANNEL_NAME = 'Loups Garous'

TIME_FOR_ROLES = 10
TIME_FOR_LOUPS = 15
TIME_FOR_LOUP_BLANC = 15
TIME_FOR_MAYOR_ELECTION = 30  # TODO: 120 in prod

TIME_FOR_VICTIM_ELECTION = 30  # TODO: 120 in prod
TIME_FOR_MAYOR_FINAL_CHOICE = 30  # TODO: 10 - 20 secs in prod

TIME_FOR_MAYOR_GIVE_UP = 30  # TODO in prod 30 s

TIME_FOR_CUPIDON = 25

TIME_FOR_VOYANTE = 20  # TODO 20 - 30 secs in prod

TIME_FOR_SORCIERE = 30

TIME_FOR_CHASSEUR = 30

TIME_DELETE_MSG = 0

TIME_AUTO_DESTRUCT = 120  # TODO: 30 in prod

NB_MAX_MAYOR_ELECTIONS = 3

#NB_MAX_VICTIM_ELECTIONS = 3

MINIMUM_PLAYER_NB = 2  # TODO: in prod : 4 players min

DEFAULT_NB_LOUP = 1000  # if nb > nb_players => nb = nb_players/4

DEFAULT_NB_LOUP_BLANC = 0

DEFAULT_NB_CUPIDON = 0

DEFAULT_NB_VOYANTE = 0

DEFAULT_NB_SORCIERE = 0

DEFAULT_NB_CHASSEUR = 0

MAX_NB_ANGE = 1
###
