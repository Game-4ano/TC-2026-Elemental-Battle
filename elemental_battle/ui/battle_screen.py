import pygame

class Scene:
    """Classe base abstrata para todas as telas do jogo."""
    def __init__(self, display):
        self.display = display

    def handle_events(self, events):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def draw(self):
        raise NotImplementedError


class BattleScreen(Scene):
    """
    Tela de Batalha que gerencia a interface do usuário e a representação 
    visual (temporária em geometria) do combate em turnos.
    """
    def __init__(self, display, battle):
        super().__init__(display)
        self.battle = battle
        
        # Fontes do sistema
        pygame.font.init()
        self.font_log = pygame.font.SysFont("Arial", 24)
        self.font_menu = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_hud = pygame.font.SysFont("Arial", 20, bold=True)

        # Sistema de Menu
        self.options = ["Atacar", "Habilidade", "Fugir"]
        self.selected_index = 0
        
        # Sistema de Log e Máquina de Estados
        self.state = "MENU" # Estados possíveis: "MENU", "SHOWING_LOG", "GAME_OVER"
        self.log_queue = [] # Fila de mensagens a serem exibidas uma a uma
        self.current_message = ""

        # Dimensões da tela (considerando um padrão, ajuste conforme seu config.py)
        self.screen_width = self.display.get_width()
        self.screen_height = self.display.get_height()

    def handle_events(self, events):
        """Processa as entradas do jogador dependendo do estado atual."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                
                # Estado 1: Navegando no menu
                if self.state == "MENU":
                    if event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        self._execute_player_choice()

                # Estado 2: Lendo o Log de Batalha
                elif self.state == "SHOWING_LOG":
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self._advance_log()

    def update(self):
        """Atualiza lógicas contínuas (animações, timers), se houver."""
        if self.battle.is_over() and self.state != "SHOWING_LOG":
            self.state = "GAME_OVER"

    def draw(self):
        """Orquestra a renderização de todos os elementos da tela."""
        self._draw_background()
        self._draw_entities()
        self._draw_hud()
        self._draw_bottom_panel()

    # =========================================================================
    # Métodos Privados de Lógica Interna
    # =========================================================================

    def _execute_player_choice(self):
        """Envia o comando escolhido para o motor de batalha."""
        choice = self.options[self.selected_index]
        
        if choice == "Atacar":
            # Aqui você pega a ação de ataque básica do seu personagem
            # Exemplo genérico: assumindo que actions[0] é o ataque básico
            action = self.battle.player.actions[0]
            
            # O play_round deve processar o turno e retornar uma lista de strings
            new_logs = self.battle.play_round(action)
            self.log_queue.extend(new_logs)
            self._advance_log()
            
        elif choice == "Habilidade":
            self.log_queue.append("Sistema de Skills em desenvolvimento!")
            self._advance_log()
            
        elif choice == "Fugir":
            self.log_queue.append("Não há como escapar desta batalha!")
            self._advance_log()

    def _advance_log(self):
        """Avança para a próxima mensagem do log ou volta ao menu se acabar."""
        if self.log_queue:
            self.state = "SHOWING_LOG"
            self.current_message = self.log_queue.pop(0)
        else:
            self.current_message = ""
            if not self.battle.is_over():
                self.state = "MENU"
            else:
                self.state = "GAME_OVER"

    # =========================================================================
    # Métodos Privados de Renderização (Draw)
    # =========================================================================

    def _draw_background(self):
        """Desenha o cenário (Fundo)."""
        # Cinza escuro para o cenário provisório
        self.display.fill((40, 40, 40)) 

    def _draw_entities(self):
        """Desenha as representações geométricas dos personagens."""
        # Inimigo: Círculo Vermelho (Direita/Superior)
        enemy_pos = (self.screen_width - 150, 200)
        pygame.draw.circle(self.display, (220, 50, 50), enemy_pos, 70)
        
        # Jogador: Triângulo Azul (Esquerda/Inferior)
        # Pontos do triângulo: (Topo, Baixo-Esquerda, Baixo-Direita)
        player_x, player_y = 150, 400
        triangle_points = [
            (player_x, player_y - 60), 
            (player_x - 60, player_y + 60), 
            (player_x + 60, player_y + 60)
        ]
        pygame.draw.polygon(self.display, (50, 100, 220), triangle_points)

    def _draw_hud(self):
        """Desenha as barras de vida (HP)."""
        self._draw_health_bar(self.battle.player, 50, 300)
        self._draw_health_bar(self.battle.enemy, self.screen_width - 250, 80)

    def _draw_health_bar(self, entity, x, y):
        """Desenha a barra de vida de uma entidade específica."""
        width = 200
        height = 20
        # Evita divisão por zero e limita a porcentagem entre 0 e 1
        hp_ratio = max(0, min(entity.hp / entity.max_hp, 1))
        
        # Texto do Nome e HP
        hp_text = self.font_hud.render(f"{entity.name} (HP: {int(entity.hp)}/{entity.max_hp})", True, (255, 255, 255))
        self.display.blit(hp_text, (x, y - 25))
        
        # Barra Vermelha (Fundo)
        pygame.draw.rect(self.display, (150, 0, 0), (x, y, width, height))
        # Barra Verde (Vida Atual)
        pygame.draw.rect(self.display, (0, 200, 0), (x, y, width * hp_ratio, height))
        # Borda
        pygame.draw.rect(self.display, (255, 255, 255), (x, y, width, height), 2)

    def _draw_bottom_panel(self):
        """Desenha a caixa inferior (Log ou Menu)."""
        panel_height = 180
        panel_y = self.screen_height - panel_height
        
        # Caixa de fundo
        pygame.draw.rect(self.display, (20, 20, 20), (0, panel_y, self.screen_width, panel_height))
        # Borda superior da caixa
        pygame.draw.rect(self.display, (200, 200, 200), (0, panel_y, self.screen_width, panel_height), 4)

        if self.state == "MENU":
            self._draw_menu(panel_y)
        elif self.state == "SHOWING_LOG":
            self._draw_log_text(panel_y)
        elif self.state == "GAME_OVER":
            self._draw_game_over(panel_y)

    def _draw_menu(self, panel_y):
        """Desenha as opções de comando na tela."""
        start_x = 50
        start_y = panel_y + 30
        
        for i, option in enumerate(self.options):
            color = (255, 215, 0) if i == self.selected_index else (200, 200, 200)
            prefix = "▶ " if i == self.selected_index else "  "
            
            text_surface = self.font_menu.render(f"{prefix}{option}", True, color)
            self.display.blit(text_surface, (start_x, start_y + (i * 40)))

    def _draw_log_text(self, panel_y):
        """Desenha a mensagem atual do log de combate."""
        # Renderiza a mensagem principal
        log_surface = self.font_log.render(self.current_message, True, (255, 255, 255))
        self.display.blit(log_surface, (50, panel_y + 50))
        
        # Instrução piscante/suave para avançar
        prompt_text = self.font_hud.render("Pressione [ESPAÇO] ou [ENTER] para continuar ▼", True, (150, 150, 150))
        self.display.blit(prompt_text, (self.screen_width - 400, panel_y + 140))

    def _draw_game_over(self, panel_y):
        """Exibe o resultado final da batalha."""
        winner = self.battle.get_winner()
        msg = f"A batalha terminou! {winner.name if winner else 'Empate'} venceu!"
        log_surface = self.font_log.render(msg, True, (255, 215, 0))
        self.display.blit(log_surface, (50, panel_y + 50))