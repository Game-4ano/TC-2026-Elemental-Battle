from meu_jogo.entidades.character import Character
from meu_jogo.core.game import Game
from meu_jogo.core.game_manager import GameManager
from meu_jogo.data.maps_data import maps


def main():
    player = Character("Hero", 120, 20, 5, "Fire", "Water")
    game = Game(player, maps)
    manager = GameManager(game)
    manager.run()


if __name__ == "__main__":
    main_game()
