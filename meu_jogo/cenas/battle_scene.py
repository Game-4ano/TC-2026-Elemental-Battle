import math
import random
import pygame

from meu_jogo.core.game_scene import GameScene
from meu_jogo.core.game_object import GameObject
from meu_jogo.core.config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GREEN, GRAY, RED
from meu_jogo.core.game_state import GameState
from meu_jogo.entidades.acoes import AttackAction
from meu_jogo.midia.sprites.sprite_factory import get_sprite

ELEMENT_COLORS = {
    "Fire":     (255, 110,  30),
    "Water":    ( 40, 160, 255),
    "Grass":    ( 70, 210,  70),
    "Electric": (255, 235,  30),
    "Dark":     (150,  40, 220),
    "Air":      (190, 230, 255),
}

ELEMENT_NAMES_PT = {
    "Fire": "Fogo", "Water": "Água", "Grass": "Planta",
    "Electric": "Elétrico", "Dark": "Sombra", "Air": "Vento",
}

# Escala do sprite na tela de batalha.
# 16×16 × 5 = 80×80 px  (bom para tela 500×500)
_SPRITE_SCALE = 5


# ---------------------------------------------------------------------------
# Projétil
# ---------------------------------------------------------------------------
class Projectile(GameObject):
    SPEED  = 340.0
    RADIUS = 10

    def __init__(self, origin, target_obj, element, on_hit_callback):
        super().__init__(origin.x, origin.y)
        self.target_obj = target_obj
        self.element    = element
        self.on_hit     = on_hit_callback
        self.color      = ELEMENT_COLORS.get(element, WHITE)
        self._hit       = False
        self._trail: list[pygame.Vector2] = []

        direction = target_obj.position - origin
        if direction.length() > 0:
            self.velocity = direction.normalize() * self.SPEED

    def update(self, dt: float):
        if self._hit:
            return
        self._trail.append(pygame.Vector2(self.position))
        if len(self._trail) > 8:
            self._trail.pop(0)
        self.apply_physics(dt)
        if self.position.distance_to(self.target_obj.position) < 40:
            self._hit  = True
            self.alive = False
            self.on_hit()

    def draw(self, screen: pygame.Surface):
        if self._hit:
            return
        for i, pos in enumerate(self._trail):
            alpha  = int(180 * (i / max(len(self._trail), 1)))
            radius = max(2, int(self.RADIUS * (i / max(len(self._trail), 1))))
            surf   = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (radius, radius), radius)
            screen.blit(surf, (int(pos.x) - radius, int(pos.y) - radius))
        pygame.draw.circle(screen, self.color,
            (int(self.position.x), int(self.position.y)), self.RADIUS)
        bright = tuple(min(c + 100, 255) for c in self.color)
        pygame.draw.circle(screen, bright,
            (int(self.position.x), int(self.position.y)), self.RADIUS - 4)


# ---------------------------------------------------------------------------
# CharacterObject  —  usa sprite_factory; fallback = retângulo colorido
# ---------------------------------------------------------------------------
class CharacterObject(GameObject):
    """
    Representa visualmente um personagem na tela de batalha.

    Ordem de prioridade para renderização:
        1. Sprite da sprite_factory  (se character.sprite_key existir)
        2. Retângulo colorido        (fallback automático)
    """

    # Tamanho de referência usado para colisão e HUD.
    # Para sprites 16×16 × _SPRITE_SCALE = 80, usamos 80 como SIZE.
    SIZE = 16 * _SPRITE_SCALE   # 80 px

    def __init__(self, character, x, y, fallback_color, facing_right):
        super().__init__(x, y)
        self.character      = character
        self.fallback_color = fallback_color
        self.facing_right   = facing_right
        self._shake_timer   = 0.0
        self._shake_off     = pygame.Vector2(0, 0)
        self._flash_timer   = 0.0

        # Carrega sprite uma única vez (None se sprite_key não existe)
        self._sprite: pygame.Surface | None = self._load_sprite()

        # Versão espelhada para inimigos (que ficam à direita, olhando à esquerda)
        self._sprite_flipped: pygame.Surface | None = None
        if self._sprite and not facing_right:
            self._sprite_flipped = pygame.transform.flip(self._sprite, True, False)

    def _load_sprite(self) -> pygame.Surface | None:
        key = getattr(self.character, "sprite_key", None)
        if not key:
            return None
        return get_sprite(key, scale=_SPRITE_SCALE)

    def take_hit(self):
        self._shake_timer = 0.3
        self._flash_timer = 0.2

    def update(self, dt: float):
        if self._shake_timer > 0:
            self._shake_timer -= dt
            self._shake_off = pygame.Vector2(
                random.uniform(-5, 5), random.uniform(-3, 3))
        else:
            self._shake_off = pygame.Vector2(0, 0)
        if self._flash_timer > 0:
            self._flash_timer -= dt

    def draw(self, screen: pygame.Surface):
        dp = self.position + self._shake_off
        cx = int(dp.x)
        cy = int(dp.y)

        # Sombra elíptica no chão
        pygame.draw.ellipse(screen, (0, 0, 0),
            (cx + 6, cy + self.SIZE - 6, self.SIZE - 12, 10))

        if self._sprite:
            # ── Sprite pixel art ──────────────────────────────────────
            surf = self._sprite_flipped if self._sprite_flipped else self._sprite

            if self._flash_timer > 0:
                # Flash branco: copia a surface e tinta de branco
                flash = surf.copy()
                flash.fill((255, 255, 255, 160), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(flash, (cx, cy))
            else:
                screen.blit(surf, (cx, cy))

            # Borda de elemento ao redor do sprite (quadrado)
            elem_c = ELEMENT_COLORS.get(self.character.element, WHITE)
            pygame.draw.rect(screen, elem_c,
                (cx - 2, cy - 2, self.SIZE + 4, self.SIZE + 4), 2)

        else:
            # ── Fallback: retângulo colorido (comportamento original) ──
            color = (255, 255, 255) if self._flash_timer > 0 else self.fallback_color
            body  = pygame.Rect(cx, cy, self.SIZE, self.SIZE)
            pygame.draw.rect(screen, color, body, border_radius=14)
            elem_c = ELEMENT_COLORS.get(self.character.element, WHITE)
            pygame.draw.rect(screen, elem_c, body, 3, border_radius=14)

        # Rótulo de elemento abaixo do sprite
        font     = pygame.font.SysFont(None, 19)
        elem_c   = ELEMENT_COLORS.get(self.character.element, WHITE)
        elem_name = ELEMENT_NAMES_PT.get(self.character.element, self.character.element)
        lbl = font.render(f"[{elem_name}]", True, elem_c)
        screen.blit(lbl, (cx, cy + self.SIZE + 2))

        # Tag BOSS
        if self.character.is_boss:
            bfont = pygame.font.SysFont(None, 20)
            tag   = bfont.render("★ BOSS", True, (220, 180, 0))
            screen.blit(tag, (cx, cy - 18))

    def draw_hud(self, screen, hud_x, hud_y):
        font  = pygame.font.SysFont(None, 22)
        bfont = pygame.font.SysFont(None, 26)

        panel = pygame.Rect(hud_x - 6, hud_y - 4, 160, 58)
        pygame.draw.rect(screen, (0, 0, 0), panel, border_radius=6)
        elem_c = ELEMENT_COLORS.get(self.character.element, WHITE)
        pygame.draw.rect(screen, elem_c, panel, 2, border_radius=6)

        name_s = bfont.render(
            f"{self.character.name}  Lv.{self.character.level}", True, WHITE)
        screen.blit(name_s, (hud_x, hud_y))

        bar_w, bar_h = 148, 11
        ratio     = max(self.character.hp, 0) / self.character.max_hp
        hp_color  = (60, 200, 60) if ratio > 0.5 else (220, 180, 0) if ratio > 0.25 else (220, 40, 40)
        pygame.draw.rect(screen, (60, 60, 60),
            (hud_x, hud_y + 22, bar_w, bar_h), border_radius=4)
        pygame.draw.rect(screen, hp_color,
            (hud_x, hud_y + 22, int(bar_w * ratio), bar_h), border_radius=4)
        pygame.draw.rect(screen, WHITE,
            (hud_x, hud_y + 22, bar_w, bar_h), 1, border_radius=4)

        hp_s = font.render(
            f"{self.character.hp}/{self.character.max_hp} HP", True, WHITE)
        screen.blit(hp_s, (hud_x, hud_y + 37))


# ---------------------------------------------------------------------------
# BattleScene
# ---------------------------------------------------------------------------
class BattleScene(GameScene):
    # Personagem do jogador fica à esquerda, inimigo à direita.
    # Posição = canto superior-esquerdo do sprite (80×80).
    PLAYER_X = 50.0
    ENEMY_X  = SCREEN_WIDTH - 50.0 - CharacterObject.SIZE   # 370.0
    CHARS_Y  = SCREEN_HEIGHT // 2 - CharacterObject.SIZE // 2   # 210.0

    def __init__(self, manager, battle, bg_color=(20, 20, 50), bg_image=None):
        super().__init__(manager)
        self.battle   = battle
        self.bg_color = bg_color
        self.bg_image = bg_image
        self.font     = pygame.font.SysFont(None, 24)
        self.message  = "Pressione  A  ou  ESPAÇO  para atacar"
        self.finished = False
        self._enemy_turn_pending = False
        self._enemy_turn_timer   = 0.0
        self._particles: list[dict] = []
        self.objects: list[GameObject] = []
        self._load_characters()

    # -----------------------------------------------------------------------
    def _load_characters(self):
        self.player_obj = CharacterObject(
            self.battle.player, self.PLAYER_X, self.CHARS_Y,
            fallback_color=(200, 80, 80), facing_right=True)
        self.enemy_obj  = CharacterObject(
            self.battle.enemy,  self.ENEMY_X,  self.CHARS_Y,
            fallback_color=(80, 80, 200),  facing_right=False)
        self.objects = [self.player_obj, self.enemy_obj]

    # -----------------------------------------------------------------------
    def _launch_projectile(self, attacker_obj, defender_obj):
        # Projétil parte do centro do atacante
        origin = attacker_obj.position + pygame.Vector2(
            CharacterObject.SIZE // 2, CharacterObject.SIZE // 2)

        def on_hit():
            result = AttackAction().execute(
                attacker_obj.character, defender_obj.character)
            defender_obj.take_hit()
            self._spawn_impact(defender_obj.position,
                               attacker_obj.character.element)
            self.message = (
                f"{result['attacker']} causou  {result['damage']}  de dano!")

        self.objects.append(
            Projectile(origin, defender_obj,
                       attacker_obj.character.element, on_hit))

    def _spawn_impact(self, pos: pygame.Vector2, element: str):
        color = ELEMENT_COLORS.get(element, WHITE)
        for _ in range(14):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(60, 180)
            self._particles.append({
                "pos":   pygame.Vector2(pos.x + CharacterObject.SIZE // 2,
                                        pos.y + CharacterObject.SIZE // 2),
                "vel":   pygame.Vector2(math.cos(angle) * speed,
                                        math.sin(angle) * speed),
                "life":  random.uniform(0.3, 0.7),
                "color": color,
                "r":     random.randint(3, 7),
            })

    # -----------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event):
        if event.type != pygame.KEYDOWN:
            return
        if not self.finished and not self.battle.is_over():
            if event.key in (pygame.K_a, pygame.K_SPACE) and not self._enemy_turn_pending:
                self._launch_projectile(self.player_obj, self.enemy_obj)
                self._enemy_turn_pending = True
                self._enemy_turn_timer   = 1.0
        if self.finished and event.key == pygame.K_RETURN:
            player = self.manager.game.player
            if not player.is_alive():
                player.hp = player.max_hp
            from meu_jogo.cenas.campo_de_treino import CampoDeTreinoScene
            self.manager.scene_manager.change_scene(
                CampoDeTreinoScene(self.manager))

    def update(self, dt: float):
        for obj in list(self.objects):
            obj.update(dt)
        self.objects = [o for o in self.objects if o.alive]

        for p in self._particles:
            p["pos"]  += p["vel"] * dt
            p["life"] -= dt
        self._particles = [p for p in self._particles if p["life"] > 0]

        if self._enemy_turn_pending:
            self._enemy_turn_timer -= dt
            if self._enemy_turn_timer <= 0:
                if not self.battle.is_over():
                    self._launch_projectile(self.enemy_obj, self.player_obj)
                self._enemy_turn_pending = False

        if self.battle.is_over() and not self.finished:
            self._handle_battle_end()

    # -----------------------------------------------------------------------
    def draw(self, screen: pygame.Surface):
        # Fundo
        if self.bg_image:
            scaled  = pygame.transform.scale(
                self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(scaled, (0, 0))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((*self.bg_color, 175))
            screen.blit(overlay, (0, 0))
        else:
            screen.fill(self.bg_color)

        self._draw_arena(screen)

        # GameObjects (polimorfismo — Projectile e CharacterObject)
        for obj in self.objects:
            obj.draw(screen)

        # Partículas de impacto
        for p in self._particles:
            alpha = int(255 * max(p["life"], 0) / 0.7)
            surf  = pygame.Surface((p["r"] * 2, p["r"] * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*p["color"], alpha),
                               (p["r"], p["r"]), p["r"])
            screen.blit(surf,
                (int(p["pos"].x) - p["r"], int(p["pos"].y) - p["r"]))

        # HUDs
        self.player_obj.draw_hud(screen, 16, 16)
        self.enemy_obj.draw_hud(screen, SCREEN_WIDTH - 174, 16)

        self._draw_message_box(screen)

    def render(self, screen: pygame.Surface):
        self.draw(screen)

    # -----------------------------------------------------------------------
    def _draw_arena(self, screen):
        SIZE = CharacterObject.SIZE
        for cx in (self.PLAYER_X, self.ENEMY_X):
            plat = pygame.Rect(int(cx) - 4, int(self.CHARS_Y) + SIZE + 2,
                               SIZE + 8, 10)
            pygame.draw.rect(screen, (60, 55, 80),  plat, border_radius=6)
            pygame.draw.rect(screen, (120, 110, 160), plat, 2, border_radius=6)
        mid  = SCREEN_WIDTH // 2
        div  = pygame.Surface((2, 300), pygame.SRCALPHA)
        div.fill((255, 255, 255, 40))
        screen.blit(div, (mid, 80))

    def _draw_message_box(self, screen):
        box    = pygame.Rect(20, SCREEN_HEIGHT - 110, SCREEN_WIDTH - 40, 88)
        bg_s   = pygame.Surface((box.w, box.h), pygame.SRCALPHA)
        bg_s.fill((0, 0, 0, 180))
        screen.blit(bg_s, (box.x, box.y))
        pygame.draw.rect(screen, (180, 180, 220), box, 2, border_radius=8)

        font_big = pygame.font.SysFont(None, 26)
        font_sm  = pygame.font.SysFont(None, 22)
        msg  = font_big.render(self.message, True, WHITE)
        tip  = font_sm.render("A / ESPAÇO = atacar", True, (160, 160, 200))
        back = font_sm.render("ENTER = voltar ao mapa", True, (160, 200, 160))
        screen.blit(msg,  (box.x + 14, box.y + 14))
        if not self.finished:
            screen.blit(tip,  (box.x + 14, box.y + 52))
        else:
            screen.blit(back, (box.x + 14, box.y + 52))

    # -----------------------------------------------------------------------
    def _handle_battle_end(self):
        winner = self.battle.get_winner()
        if winner == self.manager.game.player:
            self.manager.game.handle_victory(self.battle.enemy)
            if self.manager.game.state == GameState.GAME_COMPLETE:
                self.message = "Voce venceu o jogo!  ENTER para voltar."
            else:
                self.message = "Vitoria!  ENTER para voltar ao mapa."
        else:
            self.manager.game.state = GameState.GAME_OVER
            self.manager.game.player.hp = self.manager.game.player.max_hp
            self.message = "Derrota...  ENTER para voltar ao mapa."
        self.finished = True