from meu_jogo.core.elements import calculate_damage


class Action:
    def execute(self, attacker, defender):
        raise NotImplementedError("Acao deve implementar execute().")


class AttackAction(Action):
    """Ataque basico — usa calculate_damage normal."""

    def execute(self, attacker, defender):
        damage = attacker.attack(defender, calculate_damage)
        return {
            "type":     "attack",
            "attacker": attacker.name,
            "defender": defender.name,
            "damage":   damage,
        }


class SpecialAttackAction(Action):
    """Ataque especial elemental — dano x1.8, maximo 3 usos por batalha."""

    MAX_USES = 3

    def __init__(self, bonus_uses: int = 0):
        self.max_uses  = self.MAX_USES + bonus_uses
        self.uses_left = self.max_uses

    def can_use(self) -> bool:
        return self.uses_left > 0

    def execute(self, attacker, defender):
        self.uses_left -= 1
        base   = calculate_damage(attacker, defender)
        damage = int(base * 1.8)
        real   = defender.take_damage(damage)
        return {
            "type":     "special",
            "attacker": attacker.name,
            "defender": defender.name,
            "damage":   real,
        }


class DefendAction(Action):
    """Reduz dano recebido no proximo turno em 50%. Maximo 2 usos por batalha."""

    MAX_USES = 2

    def __init__(self, bonus_uses: int = 0):
        self.max_uses  = self.MAX_USES + bonus_uses
        self.uses_left = self.max_uses

    def can_use(self) -> bool:
        return self.uses_left > 0

    def execute(self, attacker, defender):
        self.uses_left -= 1
        attacker.is_defending = True
        return {
            "type":     "defend",
            "attacker": attacker.name,
            "defender": defender.name,
            "damage":   0,
        }


class HealAction(Action):
    """Recupera 30% do HP maximo. Maximo 2 usos por batalha."""

    MAX_USES   = 2
    HEAL_RATIO = 0.30

    def __init__(self, bonus_uses: int = 0):
        self.max_uses  = self.MAX_USES + bonus_uses
        self.uses_left = self.max_uses

    def can_use(self) -> bool:
        return self.uses_left > 0

    def execute(self, attacker, defender):
        self.uses_left -= 1
        # A cura escala sozinha com o nivel: e % do max_hp, que cresce no level up.
        heal      = int(attacker.max_hp * self.HEAL_RATIO)
        attacker.hp = min(attacker.hp + heal, attacker.max_hp)
        return {
            "type":     "heal",
            "attacker": attacker.name,
            "defender": defender.name,
            "damage":   0,
            "heal":     heal,
        }
