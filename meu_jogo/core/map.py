class GameMap:
    """
    Classe para compatibilidade com a estrutura antiga de dados de mapa.
    """
    def __init__(self, name, enemies, boss):
        self.name = name
        self.enemies = enemies
        self.boss = boss
