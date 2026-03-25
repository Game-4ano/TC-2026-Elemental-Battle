from meu_jogo.entidades.character import Character

# --- Inimigos genéricos ---
slime           = Character("Slime",            50,  10, 2, "Grass",    "Fire")
goblin          = Character("Goblin",           70,  12, 4, "Grass",    "Fire")
wolf            = Character("Wolf",             60,  15, 3, "Grass",    "Fire")
forest_guardian = Character("Forest Guardian", 150,  25, 8, "Grass",    "Fire", is_boss=True)

# --- Monstro Aquático (sala azul / esquerda-meio) ---
hydra = Character(
    name="Hydra",
    hp=110, damage=18, defense=6,
    element="Water", weakness="Electric",
    is_boss=True,
)

# --- Monstro Elétrico (sala amarela / direita-meio) ---
thunder_beast = Character(
    name="Thunder Beast",
    hp=95, damage=22, defense=4,
    element="Electric", weakness="Grass",
    is_boss=True,
)

# --- Monstro de Vento (sala superior) ---
storm_eagle = Character(
    name="Storm Eagle",
    hp=85, damage=20, defense=5,
    element="Air", weakness="Electric",
    is_boss=True,
)

# --- Monstro de Fogo (sala inferior) ---
magma_titan = Character(
    name="Magma Titan",
    hp=130, damage=25, defense=7,
    element="Fire", weakness="Water",
    is_boss=True,
)


def reset_boss(boss: Character) -> Character:
    """Retorna o boss com HP resetado ao máximo."""
    boss.hp = boss.max_hp
    return boss


# Mapeamento sala → boss
ROOM_BOSS = {
    "SALA_BATALHA_AGUA":     hydra,
    "SALA_BATALHA_ELETRICA": thunder_beast,
    "SALA_BATALHA_VENTO":    storm_eagle,
    "SALA_BATALHA_FOGO":     magma_titan,
}