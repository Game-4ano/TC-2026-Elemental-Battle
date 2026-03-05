from meu_jogo.entidades.character import Character
from meu_jogo.core.game import Game
from meu_jogo.core.game_state import GameState
from meu_jogo.entidades.acoes import AttackAction
from meu_jogo.data.maps_data import maps


def print_battle_start(player, enemy):
    print("\n==============================")
    print("       BATALHA INICIADA       ")
    print("==============================")
    print(f"{player.name} VS {enemy.name}")
    print("==============================\n")


def print_action_result(result):
    if result["type"] == "attack":
        print(
            f'{result["attacker"]} atacou {result["defender"]} '
            f'e causou {result["damage"]} de dano!'
        )
    elif result["type"] == "defend":
        print(f'{result["character"]} está se defendendo!')


def get_player_action():
    print("\nSeu turno:")
    print("1 - Atacar")
    print("2 - Defender")

    while True:
        choice = input("Escolha: ")

        actions = {
            "1": AttackAction(),
            "2": DefendAction(),
        }

        action = actions.get(choice)

        if action:
            return action

        print("Opção inválida. Tente novamente.")


def main():
    # Criando jogador
    player = Character(
        name="Hero",
        hp=100,
        damage=20,
        defense=5,
        element="Fire",
        weakness="Water",
    )

    # Criando inimigo
    enemy = Character(
        name="Orc",
        hp=80,
        damage=15,
        defense=3,
        element="Grass",
        weakness="Fire",
    )

    enemy_ai = BasicAI()

    battle = Battle(player, enemy, enemy_ai)

    print_battle_start(player, enemy)

    # Loop principal da batalha
    while not battle.is_over():

        # Turno do jogador
        action = get_player_action()
        result = battle.execute_player_action(action)
        print_action_result(result)

        if battle.is_over():
            break

        # Turno do inimigo
        enemy_result = battle.execute_enemy_turn()
        print_action_result(enemy_result)

        # Mostrar HP após rodada
        print(f"\n{player.name}: {player.hp}/{player.max_hp} HP")
        print(f"{enemy.name}: {enemy.hp}/{enemy.max_hp} HP")

    winner = battle.get_winner()

    print("\n==============================")
    print("        BATALHA FINALIZADA     ")
    print("==============================")
    print(f"Vencedor: {winner.name}")


if __name__ == "__main__":
    main()