"""
meu_jogo/testes/balance_report.py — simula a campanha completa (5 bosses,
progressao de nivel incluida) para validar o balanceamento sem precisar
jogar manualmente.

Roda com: python -m meu_jogo.testes.balance_report

Nao faz parte do jogo final — usa as classes reais de battle/character/IA
para o resultado refletir o jogo de verdade, com uma politica de jogador
simples (cura abaixo de 35% HP, senao usa Especial enquanto houver, senao
ataque basico).
"""

from meu_jogo.entidades.character import Player
from meu_jogo.core.game import Game
from meu_jogo.core.battle import Battle
from meu_jogo.entidades.ai_entidade import SmartAI
from meu_jogo.entidades.acoes import AttackAction, SpecialAttackAction, HealAction
from meu_jogo.core.progression import build_boss

# Ordem de portais a simular — a primeira sala e sempre a mais dificil de
# testar porque o boss recebe os stats de tier 0 (o mais fraco).
ORDEM_SALAS = [
    "SALA_BATALHA_FOGO", "SALA_BATALHA_AGUA", "SALA_BATALHA_ELETRICA",
    "SALA_BATALHA_VENTO", "SALA_BATALHA_SOMBRA",
]

HEAL_THRESHOLD = 0.35


def simular_campanha(elemento="Fire", fraqueza="Water", ordem=ORDEM_SALAS):
    player = Player("Hero", 120, 20, 5, elemento, fraqueza, sprite_key="hero")
    game = Game(player)

    for dest in ordem:
        boss = build_boss(dest, game.defeated_bosses)
        battle = Battle(player, boss, SmartAI())
        special = SpecialAttackAction()
        heal = HealAction()
        turnos = 0

        while not battle.is_over() and turnos < 200:
            turnos += 1
            if player.hp < player.max_hp * HEAL_THRESHOLD and heal.can_use():
                battle.execute_player_action(heal)
            elif special.can_use():
                battle.execute_player_action(special)
            else:
                battle.execute_player_action(AttackAction())
            if battle.is_over():
                break
            battle.execute_enemy_action(battle.choose_enemy_action())

        venceu = battle.get_winner() is player
        pct_hp = 100 * max(player.hp, 0) / player.max_hp
        print(
            f"  {boss.name:14s} tier={len(game.defeated_bosses)} "
            f"boss=({boss.max_hp},{boss.damage},{boss.defense}) "
            f"-> {'WIN' if venceu else 'LOSE'} turnos={turnos} "
            f"hero_hp={max(player.hp, 0):.0f}/{player.max_hp} ({pct_hp:.0f}%)"
        )
        if not venceu:
            print("  HEROI MORREU — campanha interrompida")
            return
        game.handle_victory(boss)
        player.hp = player.max_hp


if __name__ == "__main__":
    for elemento, fraqueza in [("Fire", "Water"), ("Water", "Electric"),
                                ("Grass", "Fire"), ("Electric", "Grass"),
                                ("Dark", "Electric")]:
        print(f"=== Heroi {elemento} (fraqueza {fraqueza}) ===")
        simular_campanha(elemento, fraqueza)
        print()
