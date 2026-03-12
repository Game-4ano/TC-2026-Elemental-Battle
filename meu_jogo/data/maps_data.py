from meu_jogo.core.map import Tile, GameMap, GrassTile, WaterTile, FireTile, WindTile, WallTile, PortalTile
from meu_jogo.data.characters_data import slime, goblin, wolf, forest_guardian

# Dados de mapas antigos (para compatibilidade)
map1 = GameMap(
    "Floresta",
    enemies=[slime, goblin, wolf],
    boss=forest_guardian,
)

maps = [map1]

# --- Definição dos tipos de tiles para o novo sistema de mapas ---
# Estes TILE_TYPES serão usados para todos os mapas, mas podem ser específicos por mapa se necessário
GLOBAL_TILE_TYPES = {
    "G": GrassTile(),
    "P": WaterTile(),
    "B": FireTile(),
    "V": WindTile(),
    "X": WallTile(),
    " ": GrassTile(), # Vazio como grama por padrão
    
    # Portais
    "F": PortalTile("Portal Fogo", (255, 165, 0), "SALA_BATALHA_FOGO", 1, 1), # Laranja para portal de fogo
    "A": PortalTile("Portal Água", (0, 0, 255), "SALA_BATALHA_AGUA", 1, 1), # Azul para portal de água
    "O": PortalTile("Portal Mundo Aberto", (0, 255, 0), "MUNDO_ABERTO", 10, 10), # Verde para portal de volta ao mundo aberto
}

# --- Matrizes de Mapa --- 

# MUNDO_ABERTO (20x15)
MUNDO_ABERTO_MATRIX = [
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

# Adicionando portais ao MUNDO_ABERTO
MUNDO_ABERTO_MATRIX[7][1] = "A" # Portal para Sala de Água
MUNDO_ABERTO_MATRIX[7][18] = "F" # Portal para Sala de Fogo

# SALA_BATALHA_FOGO (Pequena, 7x7)
SALA_BATALHA_FOGO_MATRIX = [
    ["X", "X", "X", "X", "X", "X", "X"],
    ["X", "B", "B", "B", "B", "B", "X"],
    ["X", "B", "B", "B", "B", "B", "X"],
    ["X", "B", "B", "O", "B", "B", "X"], # Portal de volta ao Mundo Aberto
    ["X", "B", "B", "B", "B", "B", "X"],
    ["X", "B", "B", "B", "B", "B", "X"],
    ["X", "X", "X", "X", "X", "X", "X"],
]

# SALA_BATALHA_AGUA (Pequena, 7x7)
SALA_BATALHA_AGUA_MATRIX = [
    ["X", "X", "X", "X", "X", "X", "X"],
    ["X", "P", "P", "P", "P", "P", "X"],
    ["X", "P", "P", "P", "P", "P", "X"],
    ["X", "P", "P", "O", "P", "P", "X"], # Portal de volta ao Mundo Aberto
    ["X", "P", "P", "P", "P", "P", "X"],
    ["X", "P", "P", "P", "P", "P", "X"],
    ["X", "X", "X", "X", "X", "X", "X"],
]

# Dicionário de todos os dados de mapas para o MapManager
ALL_MAP_DATA = {
    "MUNDO_ABERTO": {
        "matrix": MUNDO_ABERTO_MATRIX,
        "tile_types": GLOBAL_TILE_TYPES,
    },
    "SALA_BATALHA_FOGO": {
        "matrix": SALA_BATALHA_FOGO_MATRIX,
        "tile_types": GLOBAL_TILE_TYPES,
    },
    "SALA_BATALHA_AGUA": {
        "matrix": SALA_BATALHA_AGUA_MATRIX,
        "tile_types": GLOBAL_TILE_TYPES,
    },
}
