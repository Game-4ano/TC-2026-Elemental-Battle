from meu_jogo.entidades.character import Character

slime = Character("Slime", 50, 10, 2, "Grass", "Fire")
goblin = Character("Goblin", 70, 12, 4, "Grass", "Fire")
wolf = Character("Wolf", 60, 15, 3, "Grass", "Fire")

forest_guardian = Character(
    "Forest Guardian", 150, 25, 8, "Grass", "Fire", is_boss=True
)