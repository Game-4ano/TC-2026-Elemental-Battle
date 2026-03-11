import pygame
import sys
from meu_jogo.core.config import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE
from meu_jogo.core.map import Map
from meu_jogo.data.maps_data import MAP_MATRIX, TILE_TYPES
from meu_jogo.entidades.character import Character

def draw_ui(surface, player):
    """
    Desenha a interface básica do jogador (HP).
    """
    font = pygame.font.SysFont("Arial", 24, bold=True)
    
    # Barra de HP de fundo (preta)
    pygame.draw.rect(surface, (0, 0, 0), (20, 20, 200, 25))
    
    # Barra de HP preenchida (vermelha)
    hp_ratio = player.hp / player.max_hp
    pygame.draw.rect(surface, (255, 0, 0), (20, 20, int(200 * hp_ratio), 25))
    
    # Texto do HP
    hp_text = font.render(f"HP: {player.hp}/{player.max_hp}", True, (255, 255, 255))
    surface.blit(hp_text, (25, 20))
    
    # Nome e Elemento
    info_text = font.render(f"{player.name} ({player.element})", True, (0, 0, 0))
    surface.blit(info_text, (20, 50))

def main_game():
    # Inicializa o Pygame
    pygame.init()

    # Configurações da tela
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Elemental Battle - Exploração")
    clock = pygame.time.Clock()

    # Instancia o mapa
    game_map = Map(MAP_MATRIX, TILE_TYPES)

    # Instancia o jogador (Fogo)
    player = Character(
        name="Hero",
        hp=100,
        damage=20,
        defense=5,
        element="Fire",
        weakness="Water"
    )

    running = True
    print("\n--- Elemental Battle ---")
    print("Use as setas ou WASD para se mover.")
    print("Pise em diferentes tiles para ver os efeitos elementais!")

    while running:
        # 1. Captura de Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                dx, dy = 0, 0
                if event.key in [pygame.K_UP, pygame.K_w]:
                    dy = -1
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    dy = 1
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    dx = -1
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    dx = 1
                
                if dx != 0 or dy != 0:
                    player.move(dx, dy, game_map)

        # 2. Atualização (Lógica)
        player.update()
        game_map.update_camera(player.pixel_x, player.pixel_y)

        # 3. Renderização
        SCREEN.fill((200, 200, 200)) # Fundo cinza claro
        
        # Desenha o mapa com o offset da câmara
        game_map.draw(SCREEN)
        
        # Desenha o jogador por cima do mapa
        player.draw(SCREEN, game_map.camera_offset_x, game_map.camera_offset_y)
        
        # Desenha a UI (HP)
        draw_ui(SCREEN, player)

        pygame.display.flip()
        clock.tick(60)

        # Verifica se o jogador morreu
        if not player.is_alive():
            print("\nGAME OVER! O herói sucumbiu aos elementos.")
            pygame.time.wait(2000)
            running = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_game()
