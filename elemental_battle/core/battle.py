"""
Controla a lógica de batalha.
"""

from core.elements import calculate_damage


class Battle:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.current_turn = player

    def switch_turn(self):
        self.current_turn = (
            self.enemy if self.current_turn == self.player else self.player
        )

    def attack(self):
        attacker = self.current_turn
        defender = self.enemy if attacker == self.player else self.player

        damage = calculate_damage(attacker, defender)
        real_damage = defender.take_damage(damage)

        self.switch_turn()
        return real_damage

    def is_over(self):
        return not self.player.is_alive() or not self.enemy.is_alive()
