from core.character import Character
from core.game import Game
from data.maps_data import maps

player = Character("Hero", 120, 20, 5, "Fire", "Water")

game = Game(player, maps)

while True:
    battle = game.start_next_battle()

    print(f"\nIniciando batalha contra {battle.enemy.name}!")

    while not battle.is_over():
        input("Pressione Enter para atacar...")
        battle.perform_attack()
        print(f"HP Player: {battle.player.hp}")
        print(f"HP Enemy: {battle.enemy.hp}")

    winner = battle.get_winner()

    if winner == player:
        print("Você venceu!")
        game.reward_player(battle.enemy)
    else:
        print("Você perdeu!")
        break

    if battle.enemy.is_boss:
        print("Mapa concluído!")
        break