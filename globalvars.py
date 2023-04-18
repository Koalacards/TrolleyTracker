from discord.app_commands import Choice
from typing import List
#just a bunch of global variables

GAMES_LIST = ['Jungle Vines', 'Ice Slide', 'Tag', 'Cannon Game', 'Match Minnie']

GAMES_CHOICES: List[Choice] = []
for index, game in enumerate(GAMES_LIST):
    GAMES_CHOICES.append(Choice(name=game, value=index))


#the shutdown time in seconds
SHUTDOWN_TIME = 300

#the shutdown time in mintes
SHUTDOWN_TIME_MINS = 5

SUGGESTION_CHANNEL=1090463392579465246

LOGS_CHANNEL=1090463408643657829

END_COOLDOWN_TIME = 45

NUM_PLAYERS = {
    "Jungle Vines": (1, 1),
    "Ice Slide": (2, 8),
    "Tag": (2, 2),
    "Cannon Game": (1, 1),
    "Match Minnie": (2, 4)
}