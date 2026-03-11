import pygame
from meu_jogo.core.battle import Battle
from meu_jogo.entidades.character import Character
from meu_jogo.entidades.ai_entidade import BasicAI
from meu_jogo.entidades.acoes import DefendAction, AttackAction
from meu_jogo.core.map import Map
from meu_jogo.data.maps_data import MAP_MATRIX, TILE_TYPES

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


def main_battle():
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


def main_map_render():
    # Inicializa o Pygame
    pygame.init()

    # Configurações da tela
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Elemental Battle - Mapa")

    # Cores
    WHITE = (255, 255, 255)

    game_map = Map(MAP_MATRIX, TILE_TYPES)

    running = True
    clock = pygame.time.Clock()

    print("\nAbrindo visualização do mapa... Feche a janela do Pygame para encerrar.")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        SCREEN.fill(WHITE)  # Preenche o fundo com branco
        game_map.draw(SCREEN)
        pygame.display.flip() # Atualiza a tela
        clock.tick(60) # Limita a 60 FPS

    pygame.quit()

if __name__ == "__main__":
    # Por padrão, abre a visualização do mapa conforme solicitado
    main_map_render()
    
    # Se quiser rodar a batalha via console depois, pode descomentar:
    # main_battle()
