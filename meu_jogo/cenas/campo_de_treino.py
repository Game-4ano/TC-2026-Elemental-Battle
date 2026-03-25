import pygame

from meu_jogo.core.game_scene import GameScene
from meu_jogo.core.config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, TILE_SIZE
from meu_jogo.core.map import PortalTile
from meu_jogo.core.battle import Battle
from meu_jogo.entidades.ai_entidade import BasicAI


ROOM_BG = {
    "SALA_BATALHA_AGUA":     (8,   20,  70),
    "SALA_BATALHA_ELETRICA": (40,  38,   5),
    "SALA_BATALHA_VENTO":    (20,  50,  80),
    "SALA_BATALHA_FOGO":     (70,  10,   0),
}

ROOM_HINTS = {
    "SALA_BATALHA_AGUA":     "💧 Hydra  (Água)    — fraqueza: Elétrico",
    "SALA_BATALHA_ELETRICA": "⚡ Thunder Beast (Elétrico) — fraqueza: Planta",
    "SALA_BATALHA_VENTO":    "🌪 Storm Eagle (Vento)  — fraqueza: Elétrico",
    "SALA_BATALHA_FOGO":     "🔥 Magma Titan (Fogo)   — fraqueza: Água",
}


class CampoDeTreinoScene(GameScene):

    def __init__(self, manager):
        super().__init__(manager)
        self.font      = pygame.font.SysFont(None, 22)
        self.big_font  = pygame.font.SysFont(None, 28)
        self.player_grid_x = 7
        self.player_grid_y = 7

    # -----------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event):
        if event.type != pygame.KEYDOWN:
            return
        dx, dy = 0, 0
        if event.key == pygame.K_UP:     dy = -1
        elif event.key == pygame.K_DOWN:   dy =  1
        elif event.key == pygame.K_LEFT:   dx = -1
        elif event.key == pygame.K_RIGHT:  dx =  1
        if dx or dy:
            self._try_move(dx, dy)

    def _try_move(self, dx, dy):
        nx = self.player_grid_x + dx
        ny = self.player_grid_y + dy
        cmap = self.manager.map_manager.current_map
        if not cmap.is_walkable(nx, ny):
            return
        self.player_grid_x, self.player_grid_y = nx, ny
        tile = cmap.get_tile_at(nx, ny)
        if isinstance(tile, PortalTile):
            self._enter_portal(tile)
        elif tile:
            tile.on_step(self.manager.player, self.manager.map_manager)

    def _enter_portal(self, tile: PortalTile):
        from meu_jogo.data.characters_data import ROOM_BOSS
        from meu_jogo.cenas.battle_scene import BattleScene

        dest = tile.destination_map_name

        if dest in ROOM_BOSS:
            boss    = ROOM_BOSS[dest]
            boss.hp = boss.max_hp          # ← RESET DE HP DO BOSS
            # Reset HP do jogador se estava morto
            player = self.manager.game.player
            if not player.is_alive():
                player.hp = player.max_hp

            battle = Battle(player, boss, BasicAI())
            bg     = ROOM_BG.get(dest, (15, 15, 30))

            # Passa a imagem de fundo para a BattleScene
            bg_img = self.manager.map_manager.bg_image

            self.manager.scene_manager.change_scene(
                BattleScene(self.manager, battle, bg_color=bg, bg_image=bg_img)
            )
        else:
            self.manager.map_manager.request_map_change(
                dest, tile.spawn_x, tile.spawn_y
            )

    # -----------------------------------------------------------------------
    def update(self, dt: float):
        px = self.player_grid_x * TILE_SIZE + TILE_SIZE // 2
        py = self.player_grid_y * TILE_SIZE + TILE_SIZE // 2
        self.manager.map_manager.current_map.update_camera(px, py)

    def draw(self, screen: pygame.Surface):
        self.manager.map_manager.current_map.draw(screen)

        # Jogador
        cam = self.manager.map_manager.current_map
        sx  = self.player_grid_x * TILE_SIZE - cam.camera_offset_x
        sy  = self.player_grid_y * TILE_SIZE - cam.camera_offset_y

        # Sombra do jogador
        pygame.draw.ellipse(screen, (0, 0, 0, 120),
            (sx + 4, sy + TILE_SIZE - 6, TILE_SIZE - 8, 8))
        # Corpo
        pygame.draw.rect(screen, (220, 70, 70),
            (sx + 3, sy + 3, TILE_SIZE - 6, TILE_SIZE - 6), border_radius=6)
        # Borda brilhante
        pygame.draw.rect(screen, (255, 160, 160),
            (sx + 3, sy + 3, TILE_SIZE - 6, TILE_SIZE - 6), 2, border_radius=6)

        # HUD do jogador
        player = self.manager.game.player
        hp_txt = self.font.render(
            f"HP {player.hp}/{player.max_hp}  Lv.{player.level}", True, WHITE
        )
        pygame.draw.rect(screen, (0, 0, 0, 140),
            (8, SCREEN_HEIGHT - 50, hp_txt.get_width() + 16, 28))
        screen.blit(hp_txt, (16, SCREEN_HEIGHT - 46))

        # Dica inferior
        hint = self.font.render(
            "↑↓←→ mover  |  Azul=Água  Amarelo=Elétrico  Cinza=Vento  Vermelho=Fogo",
            True, (220, 220, 220),
        )
        pygame.draw.rect(screen, (0, 0, 0),
            (0, SCREEN_HEIGHT - 22, SCREEN_WIDTH, 22))
        screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 20))

    def render(self, screen: pygame.Surface):
        self.draw(screen)