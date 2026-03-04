
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

    def perform_attack(self):
        attacker = self.current_turn
        defender = self.enemy if attacker == self.player else self.player

        damage = attacker.attack(defender, calculate_damage)

        print(f"{attacker.name} causou {damage} de dano!")

        self.switch_turn()

    def is_over(self):
        return not self.player.is_alive() or not self.enemy.is_alive()

    def get_winner(self):
        if not self.player.is_alive():
            return self.enemy
        if not self.enemy.is_alive():
            return self.player
        return None