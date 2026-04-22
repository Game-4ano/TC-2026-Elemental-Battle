import pygame

from meu_jogo.core.game_scene import GameScene
from meu_jogo.core.config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, TILE_SIZE
from meu_jogo.core.map import PortalTile
from meu_jogo.core.battle import Battle
from meu_jogo.entidades.ai_entidade import BasicAI
from meu_jogo.midia.sprites.animated_sprite import AnimatedSprite


ROOM_BG = {
    "SALA_BATALHA_AGUA":     (8,   20,  70),
    "SALA_BATALHA_ELETRICA": (40,  38,   5),
    "SALA_BATALHA_VENTO":    (20,  50,  80),
    "SALA_BATALHA_FOGO":     (70,  10,   0),
}

# 16×16 × 2 = 32×32 px  (= 1 tile)
_MAP_SPRITE_SCALE = 2


class CampoDeTreinoScene(GameScene):

    def __init__(self, manager):
        super().__init__(manager)
        self.font     = pygame.font.SysFont(None, 22)

        self.player_grid_x = 7
        self.player_grid_y = 7

        self._facing_left = False

        # Cooldown de movimento: impede andar 60 tiles/s
        self._move_cooldown     = 0.18   # segundos entre passos
        self._move_timer        = 0.0

        self._hero_anim = AnimatedSprite(
            "hero_walk",
            scale=_MAP_SPRITE_SCALE,
            fps=8.0,
        )

        self.manager.audio.play_music("overworld_theme", volume=0.40)

    # -----------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event):
        # Eventos de portal/ação ainda tratados aqui
        pass

    def _try_move(self, dx, dy):
        nx = self.player_grid_x + dx
        ny = self.player_grid_y + dy
        cmap = self.manager.map_manager.current_map
        if not cmap.is_walkable(nx, ny):
            return
        self.player_grid_x, self.player_grid_y = nx, ny
        self.manager.audio.play_sfx("step", volume=0.35)
        tile = cmap.get_tile_at(nx, ny)
        if isinstance(tile, PortalTile):
            self._enter_portal(tile)
        elif tile:
            tile.on_step(self.manager.player, self.manager.map_manager)

    def _enter_portal(self, tile: PortalTile):
        from meu_jogo.data.characters_data import ROOM_BOSS
        from meu_jogo.cenas.battle_scene import BattleScene

        self.manager.audio.play_sfx("portal")
        dest = tile.destination_map_name

        if dest in ROOM_BOSS:
            boss    = ROOM_BOSS[dest]
            boss.hp = boss.max_hp
            player  = self.manager.game.player
            if not player.is_alive():
                player.hp = player.max_hp

            battle = Battle(player, boss, BasicAI())
            bg     = ROOM_BG.get(dest, (15, 15, 30))
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
        keys = pygame.key.get_pressed()

        dx, dy = 0, 0
        moving = False

        if keys[pygame.K_LEFT]:
            dx = -1
            self._facing_left = True
            moving = True
        elif keys[pygame.K_RIGHT]:
            dx = 1
            self._facing_left = False
            moving = True
        elif keys[pygame.K_UP]:
            dy = -1
            moving = True
        elif keys[pygame.K_DOWN]:
            dy = 1
            moving = True

        # Cooldown: só move quando o timer chegar a zero
        if moving:
            self._move_timer -= dt
            if self._move_timer <= 0:
                self._try_move(dx, dy)
                self._move_timer = self._move_cooldown
        else:
            # Zera o timer quando soltar a tecla para mover imediatamente
            # ao pressionar de novo (sem esperar o cooldown anterior)
            self._move_timer = 0.0

        # Animação: roda enquanto se move, para quando parado
        self._hero_anim.flipped = self._facing_left
        if moving:
            self._hero_anim.update(dt)
        else:
            self._hero_anim.reset()

        # Câmera
        px = self.player_grid_x * TILE_SIZE + TILE_SIZE // 2
        py = self.player_grid_y * TILE_SIZE + TILE_SIZE // 2
        self.manager.map_manager.current_map.update_camera(px, py)

    # -----------------------------------------------------------------------
    def draw(self, screen: pygame.Surface):
        cmap = self.manager.map_manager.current_map
        cmap.draw(screen)

        sx = self.player_grid_x * TILE_SIZE - cmap.camera_offset_x
        sy = self.player_grid_y * TILE_SIZE - cmap.camera_offset_y

        sprite_w = self._hero_anim.width
        sprite_h = self._hero_anim.height
        draw_x   = sx + (TILE_SIZE - sprite_w) // 2
        draw_y   = sy + (TILE_SIZE - sprite_h) // 2

        # Sombra
        shadow_surf = pygame.Surface((TILE_SIZE - 8, 6), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 100),
            shadow_surf.get_rect())
        screen.blit(shadow_surf, (sx + 4, sy + TILE_SIZE - 6))

        # Sprite animado (fallback: retângulo)
        if sprite_w > 0:
            self._hero_anim.draw(screen, draw_x, draw_y)
        else:
            pygame.draw.rect(screen, (220, 70, 70),
                (sx + 3, sy + 3, TILE_SIZE - 6, TILE_SIZE - 6),
                border_radius=6)

        # HUD
        player = self.manager.game.player
        total  = self.manager.score.get_total_score()
        hp_txt = self.font.render(
            f"HP {player.hp}/{player.max_hp}  Lv.{player.level}"
            f"   |   Pontos: {total}",
            True, WHITE)
        pygame.draw.rect(screen, (0, 0, 0),
            (8, SCREEN_HEIGHT - 50, hp_txt.get_width() + 16, 28))
        screen.blit(hp_txt, (16, SCREEN_HEIGHT - 46))

        hint = self.font.render(
            "Setas = mover  |  Portais coloridos = batalha",
            True, (220, 220, 220))
        pygame.draw.rect(screen, (0, 0, 0),
            (0, SCREEN_HEIGHT - 22, SCREEN_WIDTH, 22))
        screen.blit(hint,
            (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 20))

    def render(self, screen: pygame.Surface):
        self.draw(screen)