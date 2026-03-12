"""
Sistema de vantagem elemental.
"""

element_advantage = {
    "Fire": "Grass",
    "Water": "Fire",
    "Grass": "Water",
    "Electric": "Water",
    "Dark": "Fire",
}


def calculate_damage(attacker, defender):
    base_damage = attacker.damage

    if element_advantage.get(attacker.element) == defender.element:
        base_damage *= 1.5

    if attacker.element == defender.weakness:
        base_damage *= 1.2

    return base_damage