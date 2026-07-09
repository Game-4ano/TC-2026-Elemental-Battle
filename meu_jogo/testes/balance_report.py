"""
Relatorio de balanceamento (stdlib puro, sem abrir janela).

Simula, para cada estagio (ordem de enfrentamento 1..N), o heroi no nivel
correspondente contra o boss escalado por core.progression.build_boss, e
estima o resultado de uma luta "so ataque basico" (sem tatica) em matchup
elemental neutro. Usado para validar se a dificuldade sobe pela ORDEM em
que os bosses sao enfrentados, e nao pelo elemento escolhido no portal.

Rodar com:  python -m meu_jogo.testes.balance_report
"""

import math

from meu_jogo.core.config import (
    XP_PER_LEVEL, EXTRA_USES_EVERY, MAX_EXTRA_USES,
)
from meu_jogo.data.characters_data import Character, BOSS_BASE
from meu_jogo.core.progression import build_boss
from meu_jogo.entidades.acoes import HealAction

# Ordem de exemplo (a dificuldade real depende so da posicao, nao do elemento)
ROOM_ORDER = [
    "SALA_BATALHA_AGUA", "SALA_BATALHA_ELETRICA", "SALA_BATALHA_VENTO",
    "SALA_BATALHA_FOGO", "SALA_BATALHA_SOMBRA",
]


def _dano_efetivo(dano_bruto: int, defesa: int) -> int:
    """Replica Entity.take_damage quando o defensor NAO esta defendendo."""
    return max(dano_bruto - defesa // 2, 0)


def _build_player(level: int) -> Character:
    player = Character("Hero", 120, 20, 5, "Fire", "Water")
    for _ in range(level - 1):
        player.gain_xp(XP_PER_LEVEL)
    return player


def main():
    header = (
        f"{'Est.':<4}{'Boss':<15}{'BLv':<4}{'PLv':<4}"
        f"{'P(hp/dmg/def)':<16}{'B(hp/dmg/def)':<16}"
        f"{'DmgP/turno':<11}{'DmgB/turno':<11}"
        f"{'TurnosP':<8}{'HPfinal':<10}{'%HP':<7}{'Cura P':<8}"
    )
    print(header)
    print("-" * len(header))

    defeated = set()
    for stage, room in enumerate(ROOM_ORDER, start=1):
        player = _build_player(stage)
        boss   = build_boss(room, defeated)
        defeated.add(boss.name)

        dmg_p = _dano_efetivo(player.damage, boss.defense)
        dmg_b = _dano_efetivo(boss.damage, player.defense)

        turnos_p = math.ceil(boss.max_hp / dmg_p) if dmg_p > 0 else float("inf")
        # Boss ataca (turnos_p - 1) vezes antes de morrer (golpe final e livre)
        hp_final = player.hp - max(turnos_p - 1, 0) * dmg_b
        pct_hp   = max(hp_final, 0) / player.max_hp * 100

        bonus = min((stage - 1) // EXTRA_USES_EVERY, MAX_EXTRA_USES)
        cura  = int(player.max_hp * HealAction.HEAL_RATIO)

        p_stats = f"{player.max_hp}/{player.damage}/{player.defense}"
        b_stats = f"{boss.max_hp}/{boss.damage}/{boss.defense}"

        print(
            f"{stage:<4}{boss.name:<15}{boss.level:<4}{player.level:<4}"
            f"{p_stats:<16}{b_stats:<16}"
            f"{dmg_p:<11}{dmg_b:<11}"
            f"{turnos_p:<8}{max(hp_final, 0):<10.0f}{pct_hp:<7.1f}"
            f"{cura} (+{bonus} usos)"
        )

    print()
    print("Obs: DmgP/DmgB assumem matchup elemental neutro (sem x1.5/x1.2) e")
    print("ataque basico repetido, sem Defender/Curar/Especial. HP final")
    print("negativo indica que a tatica (Curar/Defender/Especial) e necessaria")
    print("para vencer aquele estagio so no ataque basico.")


if __name__ == "__main__":
    main()
