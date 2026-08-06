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

# Fonte unica dos nomes PT-BR de elemento (consumida por menu e batalha).
ELEMENT_NAMES_PT = {
    "Fire": "Fogo", "Water": "Agua", "Grass": "Planta",
    "Electric": "Eletrico", "Dark": "Sombra", "Air": "Vento",
}

# Cores canonicas por elemento — fonte unica para menu, batalha e VFX.
ELEMENT_COLORS: dict[str, tuple] = {
    "Fire":     (255, 110,  30),
    "Water":    ( 40, 160, 255),
    "Grass":    ( 70, 210,  70),
    "Electric": (255, 235,  30),
    "Dark":     (150,  40, 220),
    "Air":      (190, 230, 255),
}



def calculate_damage(attacker, defender):
    base_damage = attacker.damage

    # Vantagem (tabela) e fraqueza (campo do personagem) NAO empilham — o
    # bonus multiplicativo (1.5*1.2=1.8x) criava combinacoes intransponiveis
    # (ex: Fogo vs Hydra) enquanto outros elementos nunca levavam bonus
    # nenhum. Usa o maior dos dois bonus, nunca os dois juntos.
    vantagem         = element_advantage.get(attacker.element) == defender.element
    explora_fraqueza = attacker.element == defender.weakness

    if vantagem:
        base_damage *= 1.5
    elif explora_fraqueza:
        base_damage *= 1.2

    return base_damage