"""
Define estrutura de mapa.
"""


class GameMap:
    def __init__(self, name, enemies, boss):
        self.name = name
        self.enemies = enemies
        self.boss = boss
        self.completed = False
