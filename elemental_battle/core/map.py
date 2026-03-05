import pygame

class GameMap:
    def __init__(self, name, enemies, boss, background_color):
        self.name = name
        self.enemies = enemies
        self.boss = boss
        self.background_color = background_color
        
        # Lista para armazenar objetos renderizáveis/físicos no mapa
        self.game_objects = []

    def load_entities(self):
        # Exemplo: Atribuindo posições (x, y) temporárias para os inimigos no mapa
        # Na prática, você criaria uma classe herdeira de GameObject para representá-los
        posicoes_iniciais = [(200, 300), (400, 150), (600, 400)]
        
        for i, enemy in enumerate(self.enemies):
            # Injetando posição temporária para renderização geométrica
            enemy.pos_x = posicoes_iniciais[i][0]
            enemy.pos_y = posicoes_iniciais[i][1]
            self.game_objects.append(enemy)

    def draw(self, surface):
        # Desenha o fundo do mapa (Geometria básica/Preenchimento)
        surface.fill(self.background_color)
        
        # Desenha os inimigos geométricos baseados nos elementos
        for obj in self.game_objects:
            if hasattr(obj, 'element'):
                # Definindo cores temporárias com base no elemento do personagem
                cor = (255, 255, 255) # Padrão
                if obj.element == "Grass":
                    cor = (0, 255, 0) # Verde
                elif obj.element == "Fire":
                    cor = (255, 0, 0) # Vermelho
                elif obj.element == "Water":
                    cor = (0, 0, 255) # Azul
                
                # Representação temporária por figura geométrica (Círculo)
                pygame.draw.circle(surface, cor, (obj.pos_x, obj.pos_y), 20)
                
                # Adiciona o nome acima do círculo
                font = pygame.font.SysFont(None, 24)
                text = font.render(obj.name, True, (255, 255, 255))
                surface.blit(text, (obj.pos_x - 15, obj.pos_y - 35))