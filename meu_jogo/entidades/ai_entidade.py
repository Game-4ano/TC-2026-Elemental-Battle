from meu_jogo.entidades.acoes import AttackAction


class BaseAI:
    def choose_action(self, battle):
        raise NotImplementedError()


class BasicAI(BaseAI):
    def choose_action(self, battle):
        return AttackAction()