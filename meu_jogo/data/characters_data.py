# ---------------------------------------------------------------------------
# Identidade de cada boss por sala (elemento, fraqueza, sprite) — SEM stats.
# Stats (hp/dano/defesa) sao calculados em core/progression.py na hora de
# entrar na batalha, escalados pela ordem de enfrentamento (nao pelo
# elemento/portal escolhido): o primeiro boss enfrentado e sempre o mais
# fraco, nao importa qual sala o jogador visita primeiro.
# ---------------------------------------------------------------------------
BOSS_BASE = {
    "SALA_BATALHA_AGUA": {
        "name": "Hydra", "element": "Water", "weakness": "Electric",
        "sprite_key": "tide_crawler",
    },
    "SALA_BATALHA_ELETRICA": {
        "name": "Thunder Beast", "element": "Electric", "weakness": "Grass",
        "sprite_key": "storm_raven",
    },
    "SALA_BATALHA_VENTO": {
        "name": "Storm Eagle", "element": "Air", "weakness": "Electric",
        "sprite_key": "storm_eagle",
    },
    "SALA_BATALHA_FOGO": {
        "name": "Magma Titan", "element": "Fire", "weakness": "Water",
        "sprite_key": "magma_titan",
    },
    "SALA_BATALHA_SOMBRA": {
        "name": "Shadow Lord", "element": "Dark", "weakness": "Electric",
        "sprite_key": "void_emperor",
    },
    "SALA_BATALHA_PLANTA": {
        "name": "Forest Guardian", "element": "Grass", "weakness": "Fire",
        "sprite_key": "forest_guardian",
    },
}
