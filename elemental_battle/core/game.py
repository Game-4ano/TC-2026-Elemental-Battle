from core.battle import Battle
from config import DEFAULT_XP_REWARD, BOSS_XP_REWARD


class Game:

    def __init__(self, player, maps):
        self.player = player
        self.maps = maps
        self.current_map_index = 0
        self.current_enemy_index = 0

    def get_current_map(self):
        return self.maps[self.current_map_index]

    def start_next_battle(self):
        current_map = self.get_current_map()

        if self.current_enemy_index < len(current_map.enemies):
            enemy = current_map.enemies[self.current_enemy_index]
            self.current_enemy_index += 1
        else:
            enemy = current_map.boss

        return Battle(self.player, enemy)

    def reward_player(self, enemy):
        if enemy.is_boss:
            self.player.gain_xp(BOSS_XP_REWARD)
        else:
            self.player.gain_xp(DEFAULT_XP_REWARD)