from enum import Enum


class GameState(Enum):
    MENU = 1
    TRAINING = 2
    BATTLE = 3
    MAP_COMPLETE = 4
    GAME_OVER = 5
    GAME_COMPLETE = 6