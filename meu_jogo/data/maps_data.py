from meu_jogo.core.map import GameMap
from meu_jogo.data.characters_data import slime, goblin, wolf, forest_guardian

map1 = GameMap(
    "Floresta",
    enemies=[slime, goblin, wolf],
    boss=forest_guardian,
)

maps = [map1]

from meu_jogo.core.map import Tile

# Definição dos tipos de tiles
TILE_TYPES = {
    "G": Tile("Grama", "Terra", (34, 139, 34), True),  # Verde escuro
    "P": Tile("Poça", "Água", (30, 144, 255), True, damage_on_step=5),  # Azul dodger
    "B": Tile("Brasa", "Fogo", (255, 69, 0), True, damage_on_step=10),  # Laranja avermelhado
    "V": Tile("Vento", "Ar", (173, 216, 230), True),  # Azul claro
    "X": Tile("Montanha", "Nenhum", (139, 69, 19), False),  # Marrom (obstáculo)
    " ": Tile("Vazio", "Nenhum", (0, 0, 0), True),  # Preto (espaço vazio)
}

# Exemplo de matriz de mapa
MAP_MATRIX = [
    ["X", "X", "X", "X", "X", "X", "X", "X", "X", "X"],
    ["X", "G", "G", "G", "G", "G", "G", "G", "G", "X"],
    ["X", "G", "P", "P", "G", "G", "G", "B", "G", "X"],
    ["X", "G", "P", "P", "G", "G", "B", "B", "G", "X"],
    ["X", "G", "G", "G", "G", "G", "G", "G", "G", "X"],
    ["X", "G", "V", "V", "G", "G", "G", "G", "G", "X"],
    ["X", "G", "V", "V", "G", "G", "G", "G", "G", "X"],
    ["X", "G", "G", "G", "G", "G", "G", "G", "G", "X"],
    ["X", "G", "G", "G", "G", "G", "G", "G", "G", "X"],
    ["X", "X", "X", "X", "X", "X", "X", "X", "X", "X"],
]
