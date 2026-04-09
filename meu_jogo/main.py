import pygame
from meu_jogo.entidades.character import Character
from meu_jogo.core.game import Game
from meu_jogo.core.game_manager import GameManager
from meu_jogo.core.map import MapManager
from meu_jogo.data.maps_data import maps, ALL_MAP_DATA


def main():
    pygame.init()

    try:
        bg_image = pygame.image.load("meu_jogo/mapa.jpg").convert()
    except Exception:
        try:
            bg_image = pygame.image.load("mapa.jpg").convert()
        except Exception:
            bg_image = None

    player = Character(
        "Hero", 120, 20, 5, "Fire", "Water",
        sprite_key="hero",
    )

    game        = Game(player, maps)
    map_manager = MapManager("MUNDO_ABERTO", ALL_MAP_DATA, bg_image=bg_image)
    manager     = GameManager(game, map_manager, player)

    # Registra o callback de level up no herói.
    # Quando player.level_up() for chamado, isso exibe a notificação na tela.
    def _on_level_up(character):
        manager.notificacoes.adicionar(
            f"★  {character.name} subiu para o nível {character.level}!  ★",
            cor=(255, 220, 50),
            duracao=3.0,
            destaque=True,
        )

    player.on_level_up = _on_level_up

    manager.run()


if __name__ == "__main__":
    main()

    #dwadwadas