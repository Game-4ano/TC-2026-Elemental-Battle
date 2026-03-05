"""
Sistema de cálculo de dano e vantagem elemental.
"""

# Tabela de vantagem elemental
ELEMENT_ADVANTAGE = {
    "Fire": "Grass",
    "Water": "Fire",
    "Grass": "Water",
    "Electric": "Water",
    "Dark": "Fire",
}


def has_element_advantage(attacker, defender):
    """
    Verifica se o elemento do atacante tem vantagem sobre o defensor.
    """
    return ELEMENT_ADVANTAGE.get(attacker.element) == defender.element


def calculate_damage(attacker, defender):
    """
    Calcula o dano final considerando:
    - Dano base do atacante
    - Vantagem elemental
    - Fraqueza específica do defensor
    """

    base_damage = attacker.damage

    # Multiplicador por vantagem elemental
    if has_element_advantage(attacker, defender):
        base_damage *= 1.5

    # Multiplicador por fraqueza direta
    if attacker.element == defender.weakness:
        base_damage *= 1.2

<<<<<<< HEAD:elemental_battle/core/elements.py
    return int(base_damage)
=======
    return base_damage

# caracteristicas do inimigos
>>>>>>> origin/dev:meu_jogo/core/elements.py
