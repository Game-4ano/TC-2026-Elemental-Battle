"""
Controla fluxo geral do jogo.
"""

from meu_jogo.core.game_state import GameState
from meu_jogo.core.config import DEFAULT_XP_REWARD, BOSS_XP_REWARD

# Bosses do mundo aberto — GAME_COMPLETE quando todos forem derrotados.
WORLD_BOSSES = frozenset({
    "Hydra", "Thunder Beast", "Storm Eagle", "Magma Titan", "Shadow Lord"
})


class Game:
    """Gerencia progressão do jogador e estado global da campanha."""

    def __init__(self, player):
        self.player           = player
        self.state            = GameState.TRAINING
        self.defeated_bosses: set[str] = set()

    def handle_victory(self, enemy):
        if enemy.is_boss:
            self.player.gain_xp(BOSS_XP_REWARD)
            self.defeated_bosses.add(enemy.name)
            if self.defeated_bosses >= WORLD_BOSSES:
                self.state = GameState.GAME_COMPLETE
        else:
            self.player.gain_xp(DEFAULT_XP_REWARD)
