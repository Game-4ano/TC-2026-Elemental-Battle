"""
core/map_manager.py — carrega mapas sob demanda (cache por nome) e processa
as trocas de mapa solicitadas por portais.
"""

import pygame

from meu_jogo.core.map import Map


class MapManager:
    def __init__(self, initial_map_name, all_map_data,
                 bg_image: pygame.Surface | None = None):
        self.all_map_data    = all_map_data
        self.bg_image        = bg_image
        self.current_map_name = initial_map_name
        self.current_map     = None
        self.maps_cache      = {}
        self.pending_map_change = None
        self.load_map(initial_map_name)

    def load_map(self, map_name):
        if map_name not in self.maps_cache:
            data = self.all_map_data.get(map_name)
            if not data:
                raise ValueError(f"Mapa '{map_name}' não encontrado.")
            self.maps_cache[map_name] = Map(
                map_name, data["matrix"], data["tile_types"],
                bg_image=self.bg_image,
            )
        self.current_map      = self.maps_cache[map_name]
        self.current_map_name = map_name

    def request_map_change(self, dest, spawn_pos: pygame.Vector2):
        self.pending_map_change = (dest, spawn_pos)

    def process_map_change(self, player):
        if self.pending_map_change:
            dest, _spawn_pos = self.pending_map_change
            self.load_map(dest)
            self.pending_map_change = None
            return True
        return False
