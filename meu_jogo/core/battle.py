from core.actions import AttackAction, DefendAction
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

    def execute_enemy_turn(self):
        action = self.enemy_ai.choose_action(self)
        return action.execute(self.enemy, self.player)
    
    def get_player_action_from_input(self):
        print("\nSeu turno:")
        print("1 - Atacar")
        print("2 - Defender")
        while True:
            choice = input("Escolha: ")
            actions = {
                "1": AttackAction(),
                "2": DefendAction()
            }
            action = actions.get(choice)
            if action:
                return action
            print("Opção inválida. Tente novamente.")

    #lógica de batalha
