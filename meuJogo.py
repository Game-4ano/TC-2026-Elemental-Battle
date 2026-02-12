import pygame
import sys

# Inicialização
pygame.init()

# Configurações da Janela
largura = 800
altura = 600

tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("MEu Primeiro Jogo")

# Cores
preto = (0, 0, 0)
azul = (0, 100, 255)

# Jogador
jogador_pos = [400, 300]
velocidade = 5

# Loop Principal
while True:
    for evento in pygame.event.get():
        if evento.type==pygame.QUIT:
            pygame.quit()
            sys.exit

    # Movimentação
    teclas = pygame.key.get_pressed()
    if teclas [pygame.K_LEFT]:
        jogador_pos[0]-=velocidade
    if teclas [pygame.K_RIGHT]:
        jogador_pos[0]+=velocidade
    if teclas[pygame.K_UP]:
        jogador_pos[1]-=velocidade
    if teclas[pygame.K_DOWN]:
        jogador_pos[1]+=velocidade

    # Desenho
    tela.fill(preto)
    pygame.draw.rect(tela, azul, (jogador_pos[0], jogador_pos[1], 50, 50))
    pygame.display.flip()
    pygame.time.Clock().tick(60)
