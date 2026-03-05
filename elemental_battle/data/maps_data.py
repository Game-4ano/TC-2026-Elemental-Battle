from core.map import GameMap
from data.characters_data import slime, goblin, wolf, forest_guardian

# Cor de fundo temporária para representar a Floresta (RGB)
cor_floresta = (34, 139, 34) 

map1 = GameMap(
    name="Floresta",
    enemies=[slime, goblin, wolf],
    boss=forest_guardian,
    background_color=cor_floresta
)

# Prepara as posições geométricas dos inimigos
map1.load_entities()

maps = [map1]