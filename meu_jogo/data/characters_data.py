from meu_jogo.entidades.character import Boss

# ---------------------------------------------------------------------------
# Bosses das salas do mundo aberto — dificuldade progressiva
# Boss 1 (Agua):     mais facil   — referencia para o jogador se adaptar
# Boss 2 (Eletrico): intermediario
# Boss 3 (Vento):    dificil
# Boss 4 (Fogo):     final — desafiador
# Boss 5 (Sombra):   segredo
# ---------------------------------------------------------------------------
hydra = Boss(
    name="Hydra",
    hp=100, damage=16, defense=4,
    element="Water", weakness="Electric",
    sprite_key="tide_crawler",
)

thunder_beast = Boss(
    name="Thunder Beast",
    hp=120, damage=20, defense=5,
    element="Electric", weakness="Grass",
    sprite_key="storm_raven",
)

storm_eagle = Boss(
    name="Storm Eagle",
    hp=130, damage=22, defense=6,
    element="Air", weakness="Electric",
    sprite_key="storm_eagle",
)

magma_titan = Boss(
    name="Magma Titan",
    hp=160, damage=28, defense=8,
    element="Fire", weakness="Water",
    sprite_key="magma_titan",
)

shadow_lord = Boss(
    name="Shadow Lord",
    hp=140, damage=24, defense=7,
    element="Dark", weakness="Electric",
    sprite_key="void_emperor",
)


def reset_boss(boss: Boss) -> Boss:
    """Retorna o boss com HP resetado ao maximo."""
    boss.hp = boss.max_hp
    return boss


# Mapeamento sala → boss
ROOM_BOSS = {
    "SALA_BATALHA_AGUA":     hydra,
    "SALA_BATALHA_ELETRICA": thunder_beast,
    "SALA_BATALHA_VENTO":    storm_eagle,
    "SALA_BATALHA_FOGO":     magma_titan,
    "SALA_BATALHA_SOMBRA":   shadow_lord,
}
