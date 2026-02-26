from core.character import Character
from data.maps_data import maps
from core.game import Game

player = Character("Hero", 120, 20, 5, "Fire", "Water")

game = Game(player, maps)

battle = game.start_next_battle()

while not battle.is_over():
    input("Pressione Enter para atacar...")
    damage = battle.attack()
    print(f"Dano causado: {damage}")
    print(f"HP Player: {battle.player.hp}")
    print(f"HP Enemy: {battle.enemy.hp}")

print("Batalha encerrada!")
