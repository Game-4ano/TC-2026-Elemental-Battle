"""
Controla fluxo geral do jogo.
"""

from meu_jogo.core.battle import Battle
from meu_jogo.entidades.ai_entidade import BasicAI
from meu_jogo.core.game_state import GameState
from meu_jogo.core.config import DEFAULT_XP_REWARD, BOSS_XP_REWARD, XP_PER_LEVEL
from meu_jogo.data.characters_data import BOSS_BASE


class Game:
    """Gerencia progressão, mapas e estados."""

    def __init__(self, player, maps):
        self.player = player
        self.maps = maps
        self.current_map_index = 0
        self.current_enemy_index = 0
        self.state = GameState.TRAINING

        # Bosses derrotados (por nome). Vitória final só quando todos caírem.
        self.defeated_bosses: set[str] = set()
        self.total_bosses = len(BOSS_BASE)

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
            # Fonte unica de XP: exatamente +1 nivel por boss derrotado.
            self.player.gain_xp(XP_PER_LEVEL)
            self.defeated_bosses.add(enemy.name)
            if len(self.defeated_bosses) >= self.total_bosses:
                self.state = GameState.GAME_COMPLETE
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