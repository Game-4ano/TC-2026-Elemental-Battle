import pygame
import sys

from meu_jogo.core.config import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE
from meu_jogo.core.map import MapManager
from meu_jogo.data.maps_data import ALL_MAP_DATA
from meu_jogo.entidades.character import Character

# Inicializa o Pygame
pygame.init()
pygame.font.init()

# Configurações da tela
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Elemental Battle - Exploração")
clock = pygame.time.Clock()

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def draw_ui(surface, player):
    """
    Desenha a interface básica do jogador (HP).
    """
    font = pygame.font.SysFont("Arial", 24, bold=True)
    
    # Barra de HP de fundo (preta)
    pygame.draw.rect(surface, BLACK, (20, 20, 200, 25))
    
    # Barra de HP preenchida (vermelha)
    hp_ratio = player.hp / player.max_hp
    pygame.draw.rect(surface, (255, 0, 0), (20, 20, int(200 * hp_ratio), 25))
    
    # Texto do HP
    hp_text = font.render(f"HP: {player.hp}/{player.max_hp}", True, WHITE)
    surface.blit(hp_text, (25, 20))
    
    # Nome e Elemento
    info_text = font.render(f"{player.name} ({player.element})", True, BLACK)
    surface.blit(info_text, (20, 50))

def fade_effect(surface, fade_type, speed=5):
    """
    Implementa um efeito de fade-in ou fade-out para transições de cenário.
    """
    fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade_surface.fill(BLACK)
    for alpha in range(0, 255, speed):
        fade_surface.set_alpha(alpha)
        surface.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(5)
    
    if fade_type == 'in':
        for alpha in range(255, 0, -speed):
            fade_surface.set_alpha(alpha)
            surface.blit(fade_surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(5)

def main_game():
    """
    Loop principal do jogo.
    Gere a exploração, movimento e transições de mapa.
    """
    # Instancia o jogador (Fogo)
    player = Character(
        name="Hero",
        hp=100,
        damage=20,
        defense=5,
        element="Fire",
        weakness="Water"
    )

    # Instancia o MapManager com o mapa inicial
    map_manager = MapManager("MUNDO_ABERTO", ALL_MAP_DATA)

    running = True
    print("\n--- Elemental Battle ---")
    print("Use as setas ou WASD para se mover.")
    print("Pise em diferentes tiles para ver os efeitos elementais!")
    print("Procure os portais (tiles coloridos) para mudar de cenário!")

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
                    player.move(dx, dy, map_manager.current_map, map_manager)

        # 2. Atualização (Lógica)
        player.update()
        map_manager.current_map.update_camera(player.pixel_x, player.pixel_y)

        # Processa mudança de mapa se houver uma pendente
        if map_manager.pending_map_change:
            fade_effect(SCREEN, 'out')
            map_manager.process_map_change(player)
            fade_effect(SCREEN, 'in')

        # 3. Renderização
        SCREEN.fill((200, 200, 200)) # Fundo cinza claro
        
        # Desenha o mapa atual com o offset da câmara
        map_manager.current_map.draw(SCREEN)
        
        # Desenha o jogador por cima do mapa
        player.draw(SCREEN, map_manager.current_map.camera_offset_x, map_manager.current_map.camera_offset_y)
        
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
