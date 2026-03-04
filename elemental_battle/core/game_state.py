from enum import Enum


class GameState(Enum):
    MENU = 1
    BATTLE = 2
    MAP_COMPLETE = 3
    GAME_OVER = 4
    GAME_COMPLETE = 5