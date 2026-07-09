"""
Escalonamento dos bosses pela ORDEM em que o jogador os enfrenta.

Logica pura e sem estado: o 1o boss enfrentado (qualquer que seja o portal
escolhido) e sempre o mais facil; cada boss seguinte sobe de nivel. A unica
fonte de verdade e o conjunto game.defeated_bosses.
"""

from meu_jogo.core.config import BOSS_GROWTH
from meu_jogo.data.characters_data import Character, BOSS_BASE


def encounter_level(defeated_bosses: set) -> int:
    """Nivel do proximo boss: 1o enfrentado = 1, 2o = 2, ..."""
    return len(defeated_bosses) + 1


def build_boss(room_key: str, defeated_bosses: set) -> Character:
    """Cria uma INSTANCIA NOVA do boss da sala, escalada pela ordem de
    enfrentamento. Nunca reutiliza singletons — evita stats mutados vazando
    entre lutas."""
    base  = BOSS_BASE[room_key]
    nivel = encounter_level(defeated_bosses)

    def scale(stat: str) -> int:
        return round(base[stat] * (1 + BOSS_GROWTH[stat] * (nivel - 1)))

    boss = Character(
        name=base["name"],
        hp=scale("hp"), damage=scale("damage"), defense=scale("defense"),
        element=base["element"], weakness=base["weakness"],
        is_boss=True, sprite_key=base["sprite_key"],
    )
    boss.level = nivel
    return boss
