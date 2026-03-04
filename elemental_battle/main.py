from core.character import Character
from core.game import Game
from core.game_state import GameState
from core.actions import AttackAction
from data.maps_data import maps

player = Character("Hero", 120, 20, 5, "Fire", "Water")

game = Game(player, maps)

battle = game.start_game()

while game.state not in (GameState.GAME_OVER, GameState.GAME_COMPLETE):

    print(f"\nBatalha contra {battle.enemy.name}")

    while not battle.is_over():

        input("Pressione Enter para atacar...")

        result = battle.execute_player_action(AttackAction())
        print(f"{result['attacker']} causou {result['damage']} de dano!")

        if battle.is_over():
            break

        result = battle.execute_enemy_turn()
        print(f"{result['attacker']} causou {result['damage']} de dano!")

        print(f"HP Player: {battle.player.hp}")
        print(f"HP Enemy: {battle.enemy.hp}")

    winner = battle.get_winner()

    if winner == player:
        print("Vitória!")
        game.handle_victory(battle.enemy)
        battle = game._start_next_battle()
    else:
        print("Game Over!")
        game.state = GameState.GAME_OVER