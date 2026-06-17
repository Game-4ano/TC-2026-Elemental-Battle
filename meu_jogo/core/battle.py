"""
Controla a lógica de batalha.
"""


class Battle:
    """Gerencia batalha entre dois personagens."""

    def __init__(self, player, enemy, enemy_ai=None):
        self.player = player
        self.enemy = enemy
        self.enemy_ai = enemy_ai

    def is_over(self):
        return not self.player.is_alive() or not self.enemy.is_alive()

    def get_winner(self):
        if not self.player.is_alive():
            return self.enemy
        if not self.enemy.is_alive():
            return self.player
        return None

    def execute_player_action(self, action):
        return action.execute(self.player, self.enemy)

    def choose_enemy_action(self):
        return self.enemy_ai.choose_action(self)

    def execute_enemy_action(self, action):
        return action.execute(self.enemy, self.player)

    def execute_enemy_turn(self):
        return self.execute_enemy_action(self.choose_enemy_action())