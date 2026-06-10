"""
core/map_builder.py — logica de montagem das salas de batalha.

Separa a *logica* (montar a matriz, mesclar dicionarios de tile) dos *dados*
(matrizes, registries, REGIONS) que permanecem em data/maps_data.py.
"""


def build_themed_room(floor_tile, border_tile, deco_pattern, exit_row, exit_col):
    """
    Gera matriz 12×10 (12 cols, 10 linhas) com bordas, chão, decorações e saída.
    deco_pattern: lista de (row, col, tile_key) para decorações internas
    exit_row, exit_col: posição do portal de saída
    """
    rows, cols = 10, 12
    room = [[border_tile if (r == 0 or r == rows-1 or c == 0 or c == cols-1)
             else floor_tile
             for c in range(cols)] for r in range(rows)]
    for r, c, tk in deco_pattern:
        if 0 < r < rows-1 and 0 < c < cols-1:
            room[r][c] = tk
    room[exit_row][exit_col] = "O"
    return room


def make_room_tiles(global_tiles, battle_overrides):
    """Combina os tiles globais (base) com as sobrescritas especificas da sala."""
    base = dict(global_tiles)
    base.update(battle_overrides)
    return base
