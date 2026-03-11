from meu_jogo.core.map import Tile, GameMap, GrassTile, WaterTile, FireTile, WindTile, WallTile
from meu_jogo.data.characters_data import slime, goblin, wolf, forest_guardian

# Dados de mapas antigos (para compatibilidade)
map1 = GameMap(
    "Floresta",
    enemies=[slime, goblin, wolf],
    boss=forest_guardian,
)

maps = [map1]

# Definição dos tipos de tiles usando Polimorfismo
TILE_TYPES = {
    "G": GrassTile(),
    "P": WaterTile(),
    "B": FireTile(),
    "V": WindTile(),
    "X": WallTile(),
    " ": GrassTile(), # Vazio como grama por padrão
}

# Matriz de mapa maior (20x15) com biomas elementais
MAP_MATRIX = [
    ["X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X"],
    ["X", "G", "G", "G", "G", "X", "V", "V", "V", "V", "V", "V", "V", "V", "X", "G", "G", "G", "G", "X"],
    ["X", "G", "G", "G", "G", "X", "V", "V", "V", "V", "V", "V", "V", "V", "X", "G", "G", "G", "G", "X"],
    ["X", "G", "G", "G", "G", "X", "X", "X", "V", "V", "X", "X", "X", "X", "X", "G", "G", "G", "G", "X"],
    ["X", "G", "G", "G", "G", "G", "G", "G", "G", "G", "G", "G", "G", "G", "G", "G", "G", "G", "G", "X"],
    ["X", "X", "X", "G", "G", "X", "X", "X", "X", "X", "X", "X", "X", "G", "G", "X", "X", "X", "X", "X"],
    ["X", "P", "P", "G", "G", "P", "P", "P", "P", "P", "P", "P", "P", "G", "G", "B", "B", "B", "B", "X"],
    ["X", "P", "P", "G", "G", "P", "P", "P", "P", "P", "P", "P", "P", "G", "G", "B", "B", "B", "B", "X"],
    ["X", "P", "P", "G", "G", "P", "P", "P", "P", "P", "P", "P", "P", "G", "G", "B", "B", "B", "B", "X"],
    ["X", "X", "X", "G", "G", "X", "X", "X", "X", "X", "X", "X", "X", "G", "G", "X", "X", "X", "X", "X"],
    ["X", "G", "G", "G", "G", "G", "G", "G", "G", "G", "G", "G", "G", "G", "G", "G", "G", "G", "G", "X"],
    ["X", "G", "G", "G", "G", "X", "X", "X", "B", "B", "X", "X", "X", "X", "X", "G", "G", "G", "G", "X"],
    ["X", "G", "G", "G", "G", "X", "B", "B", "B", "B", "B", "B", "B", "B", "X", "G", "G", "G", "G", "X"],
    ["X", "G", "G", "G", "G", "X", "B", "B", "B", "B", "B", "B", "B", "B", "X", "G", "G", "G", "G", "X"],
    ["X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X"],
]
