

import pygame
import sys

pygame.init()

LARGURA_TELA = 800
ALTURA_TELA = 600
TAMANHO_TILE = 64

COLUNA_MAPA = 100
LINHAS_MAPA = 100

tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
sprite_terra = pygame.surface((TAMANHO_TILE, TAMANHO_TILE))
sprite_terra = pygame.image.load("assets/sprites/terraclara.png").convert_alpha()

jogador_x = ((COLUNA_MAPA * TAMANHO_TILE)) // 2
jogador_y = ((LINHAS_MAPA * TAMANHO_TILE)) // 2
velocidade = 15



