import math
import random
import pygame

from meu_jogo.core.game_scene import GameScene
from meu_jogo.core.game_object import GameObject
from meu_jogo.core.config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GREEN, GRAY, RED
from meu_jogo.core.game_state import GameState
from meu_jogo.entidades.acoes import AttackAction

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
        if self.position.distance_to(self.target_obj.position) < 32:
            self._hit  = True
            self.alive = False
            self.on_hit()

    def draw(self, screen: pygame.Surface):
        if self._hit:
            return
        # Rastro
        for i, pos in enumerate(self._trail):
            alpha  = int(180 * (i / len(self._trail)))
            radius = max(2, int(self.RADIUS * (i / len(self._trail))))
            surf   = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (radius, radius), radius)
            screen.blit(surf, (int(pos.x) - radius, int(pos.y) - radius))
        # Núcleo
        pygame.draw.circle(screen, self.color,
            (int(self.position.x), int(self.position.y)), self.RADIUS)
        bright = tuple(min(c + 100, 255) for c in self.color)
        pygame.draw.circle(screen, bright,
            (int(self.position.x), int(self.position.y)), self.RADIUS - 4)


# ---------------------------------------------------------------------------
# CharacterObject
# ---------------------------------------------------------------------------
class CharacterObject(GameObject):
    SIZE = 64

    def __init__(self, character, x, y, color, facing_right):
        super().__init__(x, y)
        self.character    = character
        self.color        = color
        self.facing_right = facing_right
        self._shake_timer = 0.0
        self._shake_off   = pygame.Vector2(0, 0)
        self._flash_timer = 0.0

    def take_hit(self):
        self._shake_timer = 0.3
        self._flash_timer = 0.2

    def update(self, dt: float):
        if self._shake_timer > 0:
            self._shake_timer -= dt
            self._shake_off = pygame.Vector2(random.uniform(-5, 5), random.uniform(-3, 3))
        else:
            self._shake_off = pygame.Vector2(0, 0)
        if self._flash_timer > 0:
            self._flash_timer -= dt

    def draw(self, screen: pygame.Surface):
        dp   = self.position + self._shake_off
        color = (255, 255, 255) if self._flash_timer > 0 else self.color

        # Sombra
        pygame.draw.ellipse(screen, (0, 0, 0),
            (int(dp.x) + 4, int(dp.y) + self.SIZE - 4, self.SIZE - 8, 10))
        # Corpo
        body = pygame.Rect(int(dp.x), int(dp.y), self.SIZE, self.SIZE)
        pygame.draw.rect(screen, color, body, border_radius=14)
        # Borda brilhante
        elem_c = ELEMENT_COLORS.get(self.character.element, WHITE)
        pygame.draw.rect(screen, elem_c, body, 3, border_radius=14)

        # Ícone de elemento
        font = pygame.font.SysFont(None, 19)
        elem_name = ELEMENT_NAMES_PT.get(self.character.element, self.character.element)
        lbl = font.render(f"[{elem_name}]", True, elem_c)
        screen.blit(lbl, (int(dp.x), int(dp.y) + self.SIZE + 2))

    def draw_hud(self, screen, hud_x, hud_y):
        font  = pygame.font.SysFont(None, 22)
        bfont = pygame.font.SysFont(None, 26)

        # Painel de fundo
        panel = pygame.Rect(hud_x - 6, hud_y - 4, 160, 58)
        pygame.draw.rect(screen, (0, 0, 0), panel, border_radius=6)
        pygame.draw.rect(screen, ELEMENT_COLORS.get(self.character.element, WHITE),
            panel, 2, border_radius=6)

        name_s = bfont.render(
            f"{self.character.name}  Lv.{self.character.level}", True, WHITE)
        screen.blit(name_s, (hud_x, hud_y))

        bar_w, bar_h = 148, 11
        ratio = max(self.character.hp, 0) / self.character.max_hp
        # Fundo da barra
        pygame.draw.rect(screen, (60, 60, 60),   (hud_x, hud_y + 22, bar_w, bar_h), border_radius=4)
        # Barra de HP colorida por estado
        hp_color = (60, 200, 60) if ratio > 0.5 else (220, 180, 0) if ratio > 0.25 else (220, 40, 40)
        pygame.draw.rect(screen, hp_color, (hud_x, hud_y + 22, int(bar_w * ratio), bar_h), border_radius=4)
        pygame.draw.rect(screen, WHITE,    (hud_x, hud_y + 22, bar_w, bar_h), 1, border_radius=4)

        hp_s = font.render(f"{self.character.hp}/{self.character.max_hp} HP", True, WHITE)
        screen.blit(hp_s, (hud_x, hud_y + 37))


# ---------------------------------------------------------------------------
# BattleScene
# ---------------------------------------------------------------------------
class BattleScene(GameScene):
    PLAYER_X = 70.0
    ENEMY_X  = SCREEN_WIDTH - 140.0
    CHARS_Y  = SCREEN_HEIGHT // 2 - 40.0

    def __init__(self, manager, battle, bg_color=(20, 20, 50), bg_image=None):
        super().__init__(manager)
        self.battle   = battle
        self.bg_color = bg_color
        self.bg_image = bg_image        # mapa.jpg como fundo
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
            (200, 80, 80), facing_right=True)
        self.enemy_obj  = CharacterObject(
            self.battle.enemy,  self.ENEMY_X,  self.CHARS_Y,
            (80, 80, 200), facing_right=False)
        self.objects = [self.player_obj, self.enemy_obj]

    def _reload_battle(self, battle):
        self.battle = battle
        self._load_characters()

    # -----------------------------------------------------------------------
    def _launch_projectile(self, attacker_obj, defender_obj):
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
                "pos":   pygame.Vector2(pos.x + 32, pos.y + 32),
                "vel":   pygame.Vector2(math.cos(angle)*speed, math.sin(angle)*speed),
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
            # Reseta HP do jogador se morreu
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

        # Partículas
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
        # Fundo: imagem ou cor sólida
        if self.bg_image:
            scaled = pygame.transform.scale(
                self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(scaled, (0, 0))
            # Overlay escuro para contraste
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((*self.bg_color, 175))
            screen.blit(overlay, (0, 0))
        else:
            screen.fill(self.bg_color)

        self._draw_arena(screen)

        # GameObjects (polimorfismo)
        for obj in self.objects:
            obj.draw(screen)

        # Partículas de impacto
        for p in self._particles:
            alpha = int(255 * max(p["life"], 0) / 0.7)
            surf  = pygame.Surface((p["r"]*2, p["r"]*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*p["color"], alpha),
                               (p["r"], p["r"]), p["r"])
            screen.blit(surf, (int(p["pos"].x)-p["r"], int(p["pos"].y)-p["r"]))

        # HUDs
        self.player_obj.draw_hud(screen, 16, 16)
        self.enemy_obj.draw_hud(screen, SCREEN_WIDTH - 174, 16)

        self._draw_message_box(screen)

    def render(self, screen: pygame.Surface):
        self.draw(screen)

    # -----------------------------------------------------------------------
    def _draw_arena(self, screen):
        # Plataformas
        for cx in (self.PLAYER_X, self.ENEMY_X):
            plat = pygame.Rect(int(cx) - 8, int(self.CHARS_Y) + CharacterObject.SIZE + 2, 80, 12)
            pygame.draw.rect(screen, (60, 55, 80), plat, border_radius=6)
            pygame.draw.rect(screen, (120, 110, 160), plat, 2, border_radius=6)
        # Linha divisória central suave
        mid = SCREEN_WIDTH // 2
        div = pygame.Surface((2, 300), pygame.SRCALPHA)
        div.fill((255, 255, 255, 40))
        screen.blit(div, (mid, 80))

    def _draw_message_box(self, screen):
        box = pygame.Rect(20, SCREEN_HEIGHT - 110, SCREEN_WIDTH - 40, 88)
        # Fundo semitransparente
        bg_surf = pygame.Surface((box.w, box.h), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 180))
        screen.blit(bg_surf, (box.x, box.y))
        pygame.draw.rect(screen, (180, 180, 220), box, 2, border_radius=8)

        font_big = pygame.font.SysFont(None, 26)
        font_sm  = pygame.font.SysFont(None, 22)
        msg  = font_big.render(self.message, True, WHITE)
        tip  = font_sm.render("A / ESPAÇO = atacar", True, (160, 160, 200))
        back = font_sm.render("ENTER = voltar ao mapa", True, (160, 200, 160))
        screen.blit(msg, (box.x + 14, box.y + 14))
        if not self.finished:
            screen.blit(tip, (box.x + 14, box.y + 52))
        else:
            screen.blit(back, (box.x + 14, box.y + 52))

    # -----------------------------------------------------------------------
    def _handle_battle_end(self):
        winner = self.battle.get_winner()
        if winner == self.manager.game.player:
            self.manager.game.handle_victory(self.battle.enemy)
            state = self.manager.game.state
            if state == GameState.GAME_COMPLETE:
                self.message = "🏆 Você venceu o jogo!  ENTER para voltar."
            else:
                self.message = "✅ Vitória!  ENTER para voltar ao mapa."
        else:
            self.manager.game.state = GameState.GAME_OVER
            # Reseta HP do jogador para a próxima tentativa
            self.manager.game.player.hp = self.manager.game.player.max_hp
            self.message = "💀 Derrota...  ENTER para voltar ao mapa."
        self.finished = True