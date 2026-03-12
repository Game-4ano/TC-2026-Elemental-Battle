import pygame

from meu_jogo.cenas.base_cenas import BaseScene
from meu_jogo.entidades.acoes import AttackAction
from meu_jogo.core.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    WHITE,
    BLACK,
    RED,
    BLUE,
    GRAY,
    GREEN,
)
from meu_jogo.core.game_state import GameState


class BattleScene(BaseScene):
    def __init__(self, manager, battle):
        super().__init__(manager)
        self.battle = battle
        self.font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 30)

        self.message = "Pressione A ou ESPAÇO para atacar"
        self.enemy_turn_pending = False
        self.enemy_turn_timer = 0.0
        self.finished = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and not self.battle.is_over():
            if event.key in (pygame.K_a, pygame.K_SPACE) and not self.enemy_turn_pending:
                result = self.battle.execute_player_action(AttackAction())
                self.message = f"{result['attacker']} causou {result['damage']} de dano!"

                if not self.battle.is_over():
                    self.enemy_turn_pending = True
                    self.enemy_turn_timer = 0.8

        if event.type == pygame.KEYDOWN and self.finished:
            if event.key == pygame.K_RETURN:
                if self.manager.game.state == GameState.GAME_COMPLETE:
                    self.manager.running = False
                elif self.manager.game.state == GameState.GAME_OVER:
                    self.manager.running = False

    def update(self, dt):
        if self.enemy_turn_pending:
            self.enemy_turn_timer -= dt
            if self.enemy_turn_timer <= 0:
                result = self.battle.execute_enemy_turn()
                self.message = f"{result['attacker']} causou {result['damage']} de dano!"
                self.enemy_turn_pending = False

        if self.battle.is_over() and not self.finished:
            winner = self.battle.get_winner()

            if winner == self.manager.game.player:
                self.manager.game.handle_victory(self.battle.enemy)

                if self.manager.game.state == GameState.GAME_COMPLETE:
                    self.message = "Você venceu o jogo! ENTER para sair."
                    self.finished = True
                else:
                    next_battle = self.manager.game._start_next_battle()
                    self.battle = next_battle
                    self.message = "Vitória! Próxima batalha iniciada."
            else:
                self.manager.game.state = GameState.GAME_OVER
                self.message = "Game Over! ENTER para sair."
                self.finished = True

    def draw_health_bar(self, screen, x, y, width, height, current_hp, max_hp):
        pygame.draw.rect(screen, GRAY, (x, y, width, height))
        ratio = max(current_hp, 0) / max_hp
        pygame.draw.rect(screen, GREEN, (x, y, int(width * ratio), height))
        pygame.draw.rect(screen, BLACK, (x, y, width, height), 2)

    def render(self, screen):
        screen.fill((230, 230, 245))

        # Jogador
        pygame.draw.rect(screen, RED, (80, 260, 90, 90))
        player_name = self.font.render(
            f"{self.battle.player.name} Lv.{self.battle.player.level}", True, BLACK
        )
        player_hp = self.font.render(
            f"HP: {self.battle.player.hp}/{self.battle.player.max_hp}", True, BLACK
        )

        # Inimigo
        pygame.draw.rect(screen, BLUE, (330, 120, 90, 90))
        enemy_name = self.font.render(
            f"{self.battle.enemy.name} Lv.{self.battle.enemy.level}", True, BLACK
        )
        enemy_hp = self.font.render(
            f"HP: {self.battle.enemy.hp}/{self.battle.enemy.max_hp}", True, BLACK
        )

        self.draw_health_bar(screen, 50, 60, 150, 18, self.battle.player.hp, self.battle.player.max_hp)
        self.draw_health_bar(screen, 300, 60, 150, 18, self.battle.enemy.hp, self.battle.enemy.max_hp)

        screen.blit(player_name, (40, 30))
        screen.blit(player_hp, (50, 85))

        screen.blit(enemy_name, (290, 30))
        screen.blit(enemy_hp, (300, 85))

        # Caixa de mensagem
        pygame.draw.rect(screen, WHITE, (25, 390, 450, 85))
        pygame.draw.rect(screen, BLACK, (25, 390, 450, 85), 2)

        msg_surface = self.font.render(self.message, True, BLACK)
        atk_surface = self.font.render("A / ESPAÇO = atacar", True, BLACK)

        screen.blit(msg_surface, (40, 410))
        if not self.finished:
            screen.blit(atk_surface, (40, 440))