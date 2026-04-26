from meu_jogo.entidades.character import Character

# ---------------------------------------------------------------------------
# Inimigos genericos (usados pelo Game/GameMap antigo)
# ---------------------------------------------------------------------------
slime = Character(
    "Slime", 50, 10, 2, "Grass", "Fire",
    sprite_key="slime",
)
goblin = Character(
    "Goblin", 70, 12, 4, "Grass", "Fire",
    sprite_key="goblin",
)
wolf = Character(
    "Wolf", 60, 15, 3, "Grass", "Fire",
    sprite_key="wolf",
)
forest_guardian = Character(
    "Forest Guardian", 150, 25, 8, "Grass", "Fire",
    is_boss=True,
    sprite_key="forest_guardian",
)

# ---------------------------------------------------------------------------
# Bosses das salas do mundo aberto — dificuldade progressiva
# Boss 1 (Agua):   mais facil   — referencia para o jogador se adaptar
# Boss 2 (Eletrico): intermediario
# Boss 3 (Vento):  dificil
# Boss 4 (Fogo):   final — desafiador
# ---------------------------------------------------------------------------
hydra = Character(
    name="Hydra",
    hp=100, damage=16, defense=4,
    element="Water", weakness="Electric",
    is_boss=True,
    sprite_key="tide_crawler",
)

thunder_beast = Character(
    name="Thunder Beast",
    hp=120, damage=20, defense=5,
    element="Electric", weakness="Grass",
    is_boss=True,
    sprite_key="storm_raven",
)

storm_eagle = Character(
    name="Storm Eagle",
    hp=130, damage=22, defense=6,
    element="Air", weakness="Electric",
    is_boss=True,
    sprite_key="storm_eagle",
)

magma_titan = Character(
    name="Magma Titan",
    hp=160, damage=28, defense=8,
    element="Fire", weakness="Water",
    is_boss=True,
    sprite_key="magma_titan",
)


def reset_boss(boss: Character) -> Character:
    """Retorna o boss com HP resetado ao maximo."""
    boss.hp = boss.max_hp
    return boss


# Mapeamento sala → boss
ROOM_BOSS = {
    "SALA_BATALHA_AGUA":     hydra,
    "SALA_BATALHA_ELETRICA": thunder_beast,
    "SALA_BATALHA_VENTO":    storm_eagle,
    "SALA_BATALHA_FOGO":     magma_titan,
}
