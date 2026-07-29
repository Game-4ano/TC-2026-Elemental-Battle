# main.py
import pygame
import sys
from .core.settings import LARGURA_TELA, ALTURA_TELA, FPS, PRETO
from .core.assets_manager import AssetManager
from .entidades.player import Player

def main():
    pygame.init()
    screen = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("Meu RPG Pygame")
    clock = pygame.time.Clock()

    # 1. Carregar Assets
    # ATENÇÃO: Garanta que as imagens existem nas pastas informadas antes de rodar!
    try:
        mapa_bg = AssetManager.load_background("meu_jogo/assets/background/mapa.png")
        player_anims = AssetManager.load_player_spritesheet("meu_jogo/assets/sprites/spritepersonagem.png")
    except FileNotFoundError as e:
        print(f"Erro ao carregar imagem: {e}")
        print("Crie imagens provisórias nas pastas corretas para testar.")
        sys.exit()

    # 2. Instanciar Entidades
    player = Player(player_anims, LARGURA_TELA // 2, ALTURA_TELA // 2)

    # 3. Game Loop
    running = True
    while running:
        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Atualizações lógicas
        keys = pygame.key.get_pressed()
        player.update(keys)

        # Renderização
        screen.fill(PRETO)
        screen.blit(mapa_bg, (0, 0)) # Desenha o mapa cobrindo a tela toda
        player.draw(screen)          # Desenha o jogador por cima

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()