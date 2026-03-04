from core.elements import calculate_damage


class Action:
    def execute(self, attacker, defender):
        raise NotImplementedError("Ação deve implementar execute().")


class AttackAction(Action):
    """Ação padrão de ataque."""

    def execute(self, attacker, defender):
        damage = attacker.attack(defender, calculate_damage)
        return {
            "type": "attack",
            "attacker": attacker.name,
            "defender": defender.name,
            "damage": damage,
        }