from core.map import GameMap
from data.characters_data import slime, goblin, wolf, forest_guardian

map1 = GameMap(
    "Floresta",
    enemies=[slime, goblin, wolf],
    boss=forest_guardian
)

maps = [map1]
