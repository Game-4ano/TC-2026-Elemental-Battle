from meu_jogo.entidades.acoes import AttackAction, SpecialAttackAction, HealAction


class BaseAI:
    def choose_action(self, battle):
        raise NotImplementedError()


class BasicAI(BaseAI):
    def choose_action(self, battle):
        return AttackAction()


class SmartAI(BaseAI):
    """
    IA adaptativa para chefes:
      - Cura quando HP < 30% e ainda tem usos.
      - Especial quando o jogador esta defendendo e ainda tem usos.
      - Ataque basico no restante.
    """

    def __init__(self):
        self._special = SpecialAttackAction()
        self._heal    = HealAction()

    def choose_action(self, battle):
        enemy  = battle.enemy
        player = battle.player

        if enemy.hp < enemy.max_hp * 0.30 and self._heal.can_use():
            return self._heal

        if getattr(player, "is_defending", False) and self._special.can_use():
            return self._special

        return AttackAction()
