"""
Controla fluxo principal do jogo.
"""

from core.battle import Battle


class Game:
    def __init__(self, player, maps):
        self.player = player
        self.maps = maps
        self.current_map_index = 0

    def start_next_battle(self):
        current_map = self.maps[self.current_map_index]

        if current_map.enemies:
            enemy = current_map.enemies.pop(0)
        else:
            enemy = current_map.boss

        return Battle(self.player, enemy)
