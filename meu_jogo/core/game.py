"""
Controla fluxo geral do jogo.
"""

from core.battle import Battle
from core.ai import BasicAI
from meu_jogo.core.game_state import GameState
from meu_jogo.testes.teste_movimentacao import DEFAULT_XP_REWARD, BOSS_XP_REWARD


class Game:
    """Gerencia progressão, mapas e estados."""

    def __init__(self, player, maps):
        self.player = player
        self.maps = maps
        self.current_map_index = 0
        self.current_enemy_index = 0
        self.state = GameState.MENU

    def start_game(self):
        self.state = GameState.BATTLE
        return self._start_next_battle()

    def _start_next_battle(self):
        current_map = self.maps[self.current_map_index]

        if self.current_enemy_index < len(current_map.enemies):
            enemy = current_map.enemies[self.current_enemy_index]
            self.current_enemy_index += 1
        else:
            enemy = current_map.boss

        return Battle(self.player, enemy, enemy_ai=BasicAI())

    def handle_victory(self, enemy):
        if enemy.is_boss:
            self._complete_map()
        else:
            self.player.gain_xp(DEFAULT_XP_REWARD)

    def _complete_map(self):
        self.player.gain_xp(BOSS_XP_REWARD)

        self.current_map_index += 1
        self.current_enemy_index = 0

        if self.current_map_index >= len(self.maps):
            self.state = GameState.GAME_COMPLETE
        else:
            self.state = GameState.MAP_COMPLETE