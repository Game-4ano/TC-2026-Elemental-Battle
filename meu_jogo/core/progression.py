"""
core/progression.py — escalonamento de dificuldade dos bosses.

Cada boss e' criado como instancia NOVA a cada batalha (nunca um singleton
reutilizado — singletons vazam HP/estado entre lutas). Os stats escalam pelo
numero de bosses ja derrotados na partida (`defeated_bosses`), nao pelo
elemento/portal escolhido: o primeiro boss enfrentado e' sempre o mais fraco,
nao importa qual sala o jogador visita primeiro.
"""

from meu_jogo.core.config import (
    BOSS_BASE_HP, BOSS_BASE_DAMAGE, BOSS_BASE_DEFENSE,
    BOSS_HP_PER_TIER, BOSS_DAMAGE_PER_TIER, BOSS_DEFENSE_PER_TIER,
)
from meu_jogo.data.characters_data import BOSS_BASE
from meu_jogo.entidades.character import Boss


def build_boss(dest_map_name: str, defeated_bosses: set[str]) -> Boss:
    """Monta o boss da sala `dest_map_name` no tier da partida atual."""
    identidade = BOSS_BASE[dest_map_name]
    tier       = len(defeated_bosses)

    boss = Boss(
        name=identidade["name"],
        hp=BOSS_BASE_HP + BOSS_HP_PER_TIER * tier,
        damage=BOSS_BASE_DAMAGE + BOSS_DAMAGE_PER_TIER * tier,
        defense=BOSS_BASE_DEFENSE + BOSS_DEFENSE_PER_TIER * tier,
        element=identidade["element"],
        weakness=identidade["weakness"],
        sprite_key=identidade["sprite_key"],
    )
    # Nivel exibido no HUD acompanha o tier (1 no primeiro boss, 2 no
    # segundo...) para refletir visualmente que o boss esta mais forte.
    boss.level = tier + 1
    return boss
