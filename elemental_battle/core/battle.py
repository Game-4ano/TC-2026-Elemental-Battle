class Battle:
    """Gerencia a batalha entre dois personagens em formato de rodadas (Rounds)."""

    def __init__(self, player, enemy, enemy_ai=None):
        self.player = player
        self.enemy = enemy
        self.enemy_ai = enemy_ai
        self.turn_count = 1
        self.combat_log = [] # Guarda as mensagens para o Pygame exibir na tela

    def is_over(self):
        return not self.player.is_alive() or not self.enemy.is_alive()

    def get_winner(self):
        if not self.player.is_alive():
            return self.enemy
        elif not self.enemy.is_alive():
            return self.player
        return None

    def play_round(self, player_action):
        """
        Executa um turno completo. Define quem ataca primeiro com base na velocidade.
        Retorna as mensagens do log de combate.
        """
        self.combat_log.clear()
        
        # IA escolhe a ação do inimigo
        enemy_action = self.enemy_ai.choose_action(self) if self.enemy_ai else None
        
        # Determina a ordem com base no atributo speed (velocidade)
        # Se for empate, o jogador tem vantagem
        if self.player.speed >= self.enemy.speed:
            first_actor, first_action = self.player, player_action
            second_actor, second_action = self.enemy, enemy_action
        else:
            first_actor, first_action = self.enemy, enemy_action
            second_actor, second_action = self.player, player_action

        # Turno do Primeiro
        self._execute_and_log(first_action, first_actor, second_actor)

        # Turno do Segundo (Apenas se ainda estiver vivo após o primeiro ataque)
        if second_actor.is_alive():
            self._execute_and_log(second_action, second_actor, first_actor)
        else:
            self.combat_log.append(f"{second_actor.name} desmaiou!")

        self.turn_count += 1
        return self.combat_log

    def _execute_and_log(self, action, actor, target):
        """Executa a ação e adiciona os resultados ao log do Pygame."""
        if action:
            # action.execute agora deve retornar uma lista de mensagens (ex: ["Slime usou Cuspir!", "Foi super efetivo!"])
            messages = action.execute(actor, target)
            self.combat_log.extend(messages)