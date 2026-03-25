import pygame
from meu_jogo.entidades.character import Character
from meu_jogo.core.game import Game
from meu_jogo.core.game_manager import GameManager
from meu_jogo.core.map import MapManager
from meu_jogo.data.maps_data import maps, ALL_MAP_DATA


def main():
    pygame.init()

    # Tenta carregar o mapa.jpg como fundo
    try:
        bg_image = pygame.image.load("meu_jogo/mapa.jpg").convert()
    except Exception:
        try:
            bg_image = pygame.image.load("mapa.jpg").convert()
        except Exception:
            bg_image = None   # Sem fundo se não encontrar

    player      = Character("Hero", 120, 20, 5, "Fire", "Water")
    game        = Game(player, maps)
    map_manager = MapManager("MUNDO_ABERTO", ALL_MAP_DATA, bg_image=bg_image)
    manager     = GameManager(game, map_manager, player)
    manager.run()


if __name__ == "__main__":
    main()