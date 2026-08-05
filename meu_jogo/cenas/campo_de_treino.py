import math
import pygame

from meu_jogo.core.game_scene import GameScene
from meu_jogo.core.config import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE
from meu_jogo.core.map import PortalTile
from meu_jogo.core.battle import Battle
from meu_jogo.entidades.ai_entidade import SmartAI
from meu_jogo.midia.sprites.animated_sprite import AnimationController
from meu_jogo.data.maps_data import REGIONS


ROOM_BG = {
    "SALA_BATALHA_AGUA":     (8,   20,  70),
    "SALA_BATALHA_ELETRICA": (40,  38,   5),
    "SALA_BATALHA_VENTO":    (20,  50,  80),
    "SALA_BATALHA_FOGO":     (70,  10,   0),
    "SALA_BATALHA_SOMBRA":   (20,   5,  35),
}

# Tint RGBA por região
REGION_TINTS = {
    "caverna_aguas":    (  0,  80, 200, 34),
    "vulcao":           (200,  60,   0, 34),
    "ceu_ventos":       (180, 220, 255, 28),
    "terra_trovejante": (200, 190,   0, 30),
    "centro":           ( 30, 160,  30, 28),
}

# Lookup rápido (col, row) → nome da região — construído na importação
_REGION_LOOKUP: dict[tuple[int, int], str] = {}
for _rname, _rdata in REGIONS.items():
    for _coord in _rdata["tiles"]:
        _REGION_LOOKUP[_coord] = _rname

_MAP_SPRITE_SCALE = 2

# Cores de elemento para o HUD
_ELEM_COLORS = {
    "Fire":     (220,  80,  30),
    "Water":    ( 50, 120, 220),
    "Air":      (150, 200, 240),
    "Electric": (220, 200,   0),
    "Grass":    ( 60, 180,  60),
}


class CampoDeTreinoScene(GameScene):

    MOVE_SPEED = 190.0  # pixels/segundo — velocidade do deslize entre tiles

    def __init__(self, manager):
        super().__init__(manager)
        self.font     = pygame.font.SysFont(None, 22)
        self.font_big = pygame.font.SysFont(None, 28)

        self.player_grid_x = 14
        self.player_grid_y = 14

        self._facing_left   = False

        # Posicao visual (pixels, float) — desliza suavemente entre tiles,
        # desacoplada da posicao logica (grid) usada para colisao/portais.
        self._visual_x = float(self.player_grid_x * TILE_SIZE)
        self._visual_y = float(self.player_grid_y * TILE_SIZE)
        self._glide_active = False
        self._glide_target  = pygame.Vector2(self._visual_x, self._visual_y)

        self._hero_ctrl = AnimationController({
            "idle":       {"anim_key": "hero_idle",       "fps": 1.8, "loop": True},
            "walk_side":  {"anim_key": "hero_walk",        "fps": 8.0, "loop": True},
            "walk_back":  {"anim_key": "hero_walk_back",   "fps": 8.0, "loop": True},
            "walk_front": {"anim_key": "hero_walk_front",  "fps": 8.0, "loop": True},
        }, scale=_MAP_SPRITE_SCALE)

        # Região atual para notificações e tint
        self._current_region: str | None = None

        # Surface reutilizável para tint de região (evita alocação por frame)
        self._tint_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        self.manager.audio.play_music("overworld_theme", volume=0.40)

    # -----------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event):
        pass

    def _try_move(self, dx: int, dy: int):
        if self._glide_active:
            return
        nx = self.player_grid_x + dx
        ny = self.player_grid_y + dy
        cmap = self.manager.map_manager.current_map
        if not cmap.is_walkable(nx, ny):
            return
        self.player_grid_x, self.player_grid_y = nx, ny
        self._glide_target = pygame.Vector2(nx * TILE_SIZE, ny * TILE_SIZE)
        self._glide_active = True
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

            battle = Battle(player, boss, SmartAI())
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
    def _detect_region(self) -> str | None:
        return _REGION_LOOKUP.get((self.player_grid_x, self.player_grid_y))

    def update(self, dt: float):
        keys = pygame.key.get_pressed()
        dx, dy, moving = 0, 0, False

        if keys[pygame.K_LEFT]:
            dx, self._facing_left, moving = -1, True, True
        elif keys[pygame.K_RIGHT]:
            dx, self._facing_left, moving =  1, False, True
        elif keys[pygame.K_UP]:
            dy, moving = -1, True
        elif keys[pygame.K_DOWN]:
            dy, moving =  1, True

        if moving and not self._glide_active:
            self._try_move(dx, dy)

        if self._glide_active:
            cur       = pygame.Vector2(self._visual_x, self._visual_y)
            remaining = self._glide_target - cur
            dist      = remaining.length()
            step      = self.MOVE_SPEED * dt
            if step >= dist or dist < 0.5:
                cur = pygame.Vector2(self._glide_target)
                self._glide_active = False
            else:
                cur += remaining.normalize() * step
            self._visual_x, self._visual_y = cur.x, cur.y

        self._hero_ctrl.flipped = self._facing_left
        if moving:
            if dy < 0:
                self._hero_ctrl.play("walk_back")
            elif dy > 0:
                self._hero_ctrl.play("walk_front")
            else:
                self._hero_ctrl.play("walk_side")
            self._hero_ctrl.update(dt)
        else:
            self._hero_ctrl.play("idle")
            self._hero_ctrl.update(dt)

        # Notificação de mudança de região
        new_region = self._detect_region()
        if new_region != self._current_region:
            if new_region and new_region in REGIONS:
                info = REGIONS[new_region]
                self.manager.notificacoes.adicionar(
                    f"◆  {info['name']}  ◆",
                    cor=info["color"],
                    duracao=2.5,
                )
            self._current_region = new_region

        # Câmera suave (lerp embutido no update_camera)
        px = self._visual_x + TILE_SIZE // 2
        py = self._visual_y + TILE_SIZE // 2
        self.manager.map_manager.current_map.update_camera(px, py, dt)

    # -----------------------------------------------------------------------
    # Helpers de desenho
    # -----------------------------------------------------------------------

    def _draw_region_tint(self, screen: pygame.Surface):
        tint = REGION_TINTS.get(self._current_region)
        if tint:
            self._tint_surf.fill(tint)
            screen.blit(self._tint_surf, (0, 0))

    def _draw_lightning_flash(self, screen: pygame.Surface):
        """Raio horizontal esporadico cruzando a Sala Eletrica (~0.1s)."""
        t     = pygame.time.get_ticks() / 1000.0
        cycle = 3.3
        phase = t % cycle
        if phase < 0.1:
            seed  = int(t / cycle)
            y     = 60 + (seed * 137) % (SCREEN_HEIGHT - 140)
            alpha = int(255 * (1 - phase / 0.1))
            line  = pygame.Surface((SCREEN_WIDTH, 2), pygame.SRCALPHA)
            line.fill((255, 255, 255, alpha))
            screen.blit(line, (0, y))

    def _draw_portal_indicators(self, screen: pygame.Surface, cmap):
        t  = pygame.time.get_ticks() / 1000.0
        px, py = self.player_grid_x, self.player_grid_y

        for dy in range(-2, 3):
            for dx in range(-2, 3):
                nx, ny = px + dx, py + dy
                tile   = cmap.get_tile_at(nx, ny)
                if not isinstance(tile, PortalTile):
                    continue
                sx = int(nx * TILE_SIZE - cmap.camera_offset_x + TILE_SIZE // 2)
                sy = int(ny * TILE_SIZE - cmap.camera_offset_y + TILE_SIZE // 2)

                pulse  = abs(math.sin(t * 3.5))
                r      = int(TILE_SIZE // 2 + 4 + pulse * 6)
                bright = tuple(min(c + 90, 255) for c in tile.color)
                pygame.draw.circle(screen, bright, (sx, sy), r, 2)

                orbit_r = int(TILE_SIZE // 2 + 12 + pulse * 4)
                for i in range(4):
                    angle = t * 1.2 + i * math.pi / 2
                    ax = sx + int(math.cos(angle) * orbit_r)
                    ay = sy + int(math.sin(angle) * orbit_r)
                    pygame.draw.circle(screen, (255, 255, 200), (ax, ay), 2)

                # Texto de dica quando a até 2 tiles
                dist = max(abs(dx), abs(dy))
                if dist <= 2:
                    hint_alpha = int(180 + 75 * abs(math.sin(t * 3)))
                    hint = self.font.render("Pressione ← → ↑ ↓ para entrar", True, bright)
                    hint.set_alpha(hint_alpha)
                    screen.blit(hint, (sx - hint.get_width() // 2, sy - TILE_SIZE - 8))

    def _draw_hero_shadow(self, screen: pygame.Surface, sx: int, sy: int):
        t     = pygame.time.get_ticks() / 1000.0
        pulse = int(2 * abs(math.sin(t * 8.0)))
        w     = TILE_SIZE - 8 - pulse
        surf  = pygame.Surface((w, 6), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (0, 0, 0, 90), surf.get_rect())
        screen.blit(surf, (sx + 4 + pulse // 2, sy + TILE_SIZE - 6))

    def _draw_hud(self, screen: pygame.Surface, player, total: int):
        panel_w, panel_h = 290, 76
        px, py = 8, SCREEN_HEIGHT - panel_h - 8

        # Fundo semi-transparente
        hud = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        hud.fill((8, 6, 18, 200))
        screen.blit(hud, (px, py))

        # Bordas estilo RPG retro
        for i, col in enumerate([(150, 120, 50), (80, 60, 20), (200, 170, 70)]):
            pygame.draw.rect(screen, col,
                pygame.Rect(px + i, py + i, panel_w - 2*i, panel_h - 2*i), 1)

        # Ornamentos nos cantos
        for cx2, cy2 in [(px+3, py+3), (px+panel_w-7, py+3),
                         (px+3, py+panel_h-7), (px+panel_w-7, py+panel_h-7)]:
            pygame.draw.rect(screen, (210, 180, 80), (cx2, cy2, 4, 4))

        # Círculo de elemento
        elem = getattr(player, "element", "")
        ecol = _ELEM_COLORS.get(elem, (180, 180, 180))
        pygame.draw.circle(screen, ecol, (px + 15, py + 15), 8)
        pygame.draw.circle(screen, (255, 255, 255), (px + 15, py + 15), 8, 1)

        # Nível
        lv = self.font.render(f"Lv.{player.level}", True, (220, 200, 80))
        screen.blit(lv, (px + 28, py + 8))

        # Barra de HP
        hp_ratio = max(0.0, player.hp / max(player.max_hp, 1))
        bx, by   = px + 28, py + 28
        bw, bh   = panel_w - 36, 12
        pygame.draw.rect(screen, (50, 15, 15), (bx, by, bw, bh))
        bar_col = (70, 210, 70) if hp_ratio > 0.5 else (220, 180, 0) if hp_ratio > 0.25 else (210, 40, 40)
        pygame.draw.rect(screen, bar_col, (bx, by, int(bw * hp_ratio), bh))
        pygame.draw.rect(screen, (130, 130, 130), (bx, by, bw, bh), 1)

        hp_txt = self.font.render(f"{player.hp}/{player.max_hp}", True, (230, 230, 230))
        screen.blit(hp_txt, (bx + 2, by - 1))

        # Pontuação
        sc = self.font.render(f"Pts: {total}", True, (160, 220, 255))
        screen.blit(sc, (px + 10, py + 50))

        # Nome da região
        if self._current_region and self._current_region in REGIONS:
            rname = REGIONS[self._current_region]["name"]
            rcol  = REGIONS[self._current_region]["color"]
            rtxt  = self.font.render(rname, True, rcol)
            screen.blit(rtxt, (px + panel_w + 8, py + panel_h - 20))

    # -----------------------------------------------------------------------
    def draw(self, screen: pygame.Surface):
        cmap = self.manager.map_manager.current_map
        cmap.draw(screen)

        # Tint ambiental por região
        self._draw_region_tint(screen)
        if self.manager.map_manager.current_map_name == "SALA_BATALHA_ELETRICA":
            self._draw_lightning_flash(screen)

        sx = int(self._visual_x - cmap.camera_offset_x)
        sy = int(self._visual_y - cmap.camera_offset_y)

        self._draw_hero_shadow(screen, sx, sy)

        sprite_w = self._hero_ctrl.width
        sprite_h = self._hero_ctrl.height
        draw_x   = sx + (TILE_SIZE - sprite_w) // 2
        draw_y   = sy + (TILE_SIZE - sprite_h) // 2

        if sprite_w > 0:
            self._hero_ctrl.draw(screen, draw_x, draw_y)
        else:
            pygame.draw.rect(screen, (220, 70, 70),
                (sx + 3, sy + 3, TILE_SIZE - 6, TILE_SIZE - 6), border_radius=6)

        # Indicadores de portal próximo
        self._draw_portal_indicators(screen, cmap)

        # HUD melhorado
        player = self.manager.game.player
        total  = self.manager.score.get_total_score()
        self._draw_hud(screen, player, total)

        # Barra de dica inferior
        hint = self.font.render(
            "Setas = mover  |  Portais coloridos = batalha",
            True, (200, 200, 200))
        pygame.draw.rect(screen, (0, 0, 0),
            (0, SCREEN_HEIGHT - 22, SCREEN_WIDTH, 22))
        screen.blit(hint,
            (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 20))

    def render(self, screen: pygame.Surface):
        self.draw(screen)
