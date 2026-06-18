import math
import random
import pygame

from meu_jogo.core.game_scene import GameScene
from meu_jogo.core.game_object import GameObject
from meu_jogo.core.config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GREEN, GRAY, RED
from meu_jogo.core.game_state import GameState
from meu_jogo.core.elements import element_advantage
from meu_jogo.entidades.acoes import (
    Action, AttackAction, SpecialAttackAction, DefendAction, HealAction
)
from meu_jogo.midia.sprites.sprite_factory import get_sprite, get_animation, get_scene_image
from meu_jogo.midia.sprites.animated_sprite import AnimatedSprite, AnimationController

# Fundos de batalha por elemento do inimigo (PNG real; senao usa procedural)
_BATTLE_BG_FILES = {
    "Water": "batalhaagua.png",
    "Fire":  "batalhafogo.png",
    "Grass": "batalhaterra.png",
    "Dark":  "batalhabossfinal.png",
}

ELEMENT_COLORS = {
    "Fire":     (255, 110,  30),
    "Water":    ( 40, 160, 255),
    "Grass":    ( 70, 210,  70),
    "Electric": (255, 235,  30),
    "Dark":     (150,  40, 220),
    "Air":      (190, 230, 255),
}

ELEMENT_NAMES_PT = {
    "Fire": "Fogo", "Water": "Agua", "Grass": "Planta",
    "Electric": "Eletrico", "Dark": "Sombra", "Air": "Vento",
}


def _to_rgb(color):
    """Converte diferentes formatos de cor para uma tupla (r,g,b) com ints 0-255.
    Fallback para branco se inválido."""
    if isinstance(color, pygame.Color):
        return (color.r, color.g, color.b)
    try:
        # aceita listas/tuplas de números (possivelmente floats)
        seq = tuple(int(max(0, min(255, round(c)))) for c in color)
        if len(seq) >= 3:
            return (seq[0], seq[1], seq[2])
    except Exception:
        pass
    return (255, 255, 255)

# Escala do sprite na tela de batalha.
# 16x16 x 5 = 80x80 px
_SPRITE_SCALE = 5

# Rotulos do menu de batalha
_MENU_LABELS = ["Atacar", "Especial", "Defender", "Curar"]


# ---------------------------------------------------------------------------
# Projetil
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
            _rgb = _to_rgb(self.color)
            pygame.draw.circle(surf, (_rgb[0], _rgb[1], _rgb[2], alpha), (radius, radius), radius)
            screen.blit(surf, (int(pos.x) - radius, int(pos.y) - radius))
        _rgb = _to_rgb(self.color)
        pygame.draw.circle(screen, _rgb,
            (int(self.position.x), int(self.position.y)), self.RADIUS)
        bright = tuple(min(c + 100, 255) for c in _rgb)
        pygame.draw.circle(screen, bright,
            (int(self.position.x), int(self.position.y)), self.RADIUS - 4)


# ---------------------------------------------------------------------------
# CharacterObject  —  sprite animado com maquina de estados
# ---------------------------------------------------------------------------
class CharacterObject(GameObject):
    """
    Representa visualmente um personagem na tela de batalha.
    Suporta animacoes de idle, ataque, dano e morte via AnimatedSprite.
    Fallback: retangulo colorido se sprite_key nao existir.
    """

    SIZE = 16 * _SPRITE_SCALE   # 80 px

    # Estados de animacao
    IDLE   = "idle"
    ATTACK = "attack"
    HURT   = "hurt"
    DYING  = "dying"

    def __init__(self, character, x, y, fallback_color, facing_right):
        super().__init__(x, y)
        self.character      = character
        self.fallback_color = fallback_color
        self.facing_right   = facing_right
        self._shake_timer   = 0.0
        self._shake_off     = pygame.Vector2(0, 0)
        self._flash_timer   = 0.0
        self._flash_color   = (255, 255, 255)

        # HP animado: interpola suavemente em direcao ao HP real
        self._hp_display: float = float(character.hp)

        # Sprite estático (fallback quando AnimationController não tem frames)
        self._sprite: pygame.Surface | None = self._load_sprite()
        self._sprite_flipped: pygame.Surface | None = (
            pygame.transform.flip(self._sprite, True, False)
            if self._sprite and not facing_right else None
        )

        skey = getattr(character, "sprite_key", "") or ""
        if facing_right:
            states = {
                "idle":   {"anim_key": "hero_idle_breath", "fps": 1.8,  "loop": True},
                "attack": {"anim_key": "hero_attack",       "fps": 8.0,  "loop": False},
                "hurt":   {"anim_key": "hero_hurt",         "fps": 6.0,  "loop": False},
                "dying":  {"anim_key": "hero_idle_breath",  "fps": 1.8,  "loop": False},
            }
        else:
            states = {
                "idle":   {"anim_key": f"{skey}_idle",   "fps": 1.8,  "loop": True},
                "attack": {"anim_key": f"{skey}_attack", "fps": 8.0,  "loop": False},
                "hurt":   {"anim_key": f"{skey}_hurt",   "fps": 6.0,  "loop": False},
                "dying":  {"anim_key": f"{skey}_death",  "fps": 3.5,  "loop": False},
            }
        self._ctrl = AnimationController(
            states, scale=_SPRITE_SCALE, flipped=not facing_right)

        self._state          = self.IDLE
        self._state_timer    = 0.0
        self._state_duration = 0.0

    # ── Carregamento ──────────────────────────────────────────────────────────

    def _load_sprite(self) -> pygame.Surface | None:
        key = getattr(self.character, "sprite_key", None)
        if not key:
            return None
        return get_sprite(key, scale=_SPRITE_SCALE)

    # ── Triggers de estado ────────────────────────────────────────────────────

    def play_attack(self):
        """Inicia animacao de ataque (0.35s, nao-loop)."""
        self._ctrl.play("attack", force_restart=True)
        self._state          = self.ATTACK
        self._state_timer    = 0.0
        self._state_duration = 0.35

    def take_hit(self, flash_color=(255, 255, 255)):
        """Flash + shake + animacao de hurt."""
        self._shake_timer = 0.3
        self._flash_timer = 0.2
        self._flash_color = flash_color
        self._ctrl.play("hurt", force_restart=True)
        self._state          = self.HURT
        self._state_timer    = 0.0
        self._state_duration = 0.3

    def start_death_anim(self):
        """Inicia dissolucao (0.9s)."""
        self._ctrl.play("dying", force_restart=True)
        self._state          = self.DYING
        self._state_timer    = 0.0
        self._state_duration = 0.9

    @property
    def death_anim_done(self) -> bool:
        return self._state == self.DYING and self._state_timer >= self._state_duration

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt: float):
        if self._shake_timer > 0:
            self._shake_timer -= dt
            self._shake_off = pygame.Vector2(
                random.uniform(-5, 5), random.uniform(-3, 3))
        else:
            self._shake_off = pygame.Vector2(0, 0)
        if self._flash_timer > 0:
            self._flash_timer -= dt

        target = float(max(self.character.hp, 0))
        diff   = target - self._hp_display
        if abs(diff) > 0.5:
            self._hp_display += diff * min(7.0 * dt, 1.0)
        else:
            self._hp_display = target

        if self._state != self.IDLE:
            self._state_timer += dt
            if self._state != self.DYING and self._state_timer >= self._state_duration:
                self._state = self.IDLE
                self._ctrl.play("idle")

        self._ctrl.update(dt)

    # ── Draw ──────────────────────────────────────────────────────────────────

    def _current_surf(self) -> pygame.Surface | None:
        frame = self._ctrl.current_frame
        if frame:
            return frame
        return self._sprite_flipped if self._sprite_flipped else self._sprite

    def draw(self, screen: pygame.Surface):
        dp = self.position + self._shake_off
        cx, cy = int(dp.x), int(dp.y)

        dying    = self._state == self.DYING
        progress = (self._state_timer / max(self._state_duration, 0.01)) if dying else 0.0

        # Sombra (desaparece durante morte)
        if not dying or progress < 0.7:
            pygame.draw.ellipse(screen, (0, 0, 0),
                (cx + 6, cy + self.SIZE - 6, self.SIZE - 12, 10))

        surf = self._current_surf()

        if surf:
            if dying:
                surf = surf.copy()
                surf.set_alpha(max(0, int(255 * (1.0 - progress))))
            elif self._flash_timer > 0:
                surf = surf.copy()
                surf.fill((*self._flash_color, 160), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(surf, (cx, cy))

            if not dying:
                elem_c = ELEMENT_COLORS.get(self.character.element, WHITE)
                pygame.draw.rect(screen, elem_c,
                    (cx - 2, cy - 2, self.SIZE + 4, self.SIZE + 4), 2)
        else:
            color = (255, 255, 255) if self._flash_timer > 0 else self.fallback_color
            body  = pygame.Rect(cx, cy, self.SIZE, self.SIZE)
            pygame.draw.rect(screen, color, body, border_radius=14)
            elem_c = ELEMENT_COLORS.get(self.character.element, WHITE)
            pygame.draw.rect(screen, elem_c, body, 3, border_radius=14)

        if not dying:
            font = pygame.font.SysFont(None, 19)
            elem_c = ELEMENT_COLORS.get(self.character.element, WHITE)
            lbl = font.render(
                f"[{ELEMENT_NAMES_PT.get(self.character.element, self.character.element)}]",
                True, elem_c)
            screen.blit(lbl, (cx, cy + self.SIZE + 2))
            if self.character.is_boss:
                tag = pygame.font.SysFont(None, 20).render("BOSS", True, (220, 180, 0))
                screen.blit(tag, (cx, cy - 18))

    def draw_hud(self, screen, hud_x, hud_y):
        font   = pygame.font.SysFont(None, 22)
        bfont  = pygame.font.SysFont(None, 23)
        sfont  = pygame.font.SysFont(None, 17)
        elem_c = ELEMENT_COLORS.get(self.character.element, WHITE)

        panel = pygame.Rect(hud_x, hud_y, 180, 64)
        bg    = pygame.Surface((panel.w, panel.h), pygame.SRCALPHA)
        bg.fill((8, 6, 18, 215))
        screen.blit(bg, panel.topleft)
        pygame.draw.rect(screen, elem_c, panel, 2, border_radius=6)
        pygame.draw.rect(screen, tuple(max(0, c - 80) for c in elem_c),
                         panel.inflate(-5, -5), 1, border_radius=4)

        pygame.draw.circle(screen, elem_c, (hud_x + 13, hud_y + 13), 8)
        pygame.draw.circle(screen, WHITE,  (hud_x + 13, hud_y + 13), 8, 1)

        name_s = bfont.render(
            f"{self.character.name}  Lv.{self.character.level}", True, WHITE)
        screen.blit(name_s, (hud_x + 26, hud_y + 5))

        if self.character.is_boss:
            tbg = pygame.Surface((40, 14), pygame.SRCALPHA)
            tbg.fill((140, 90, 0, 220))
            screen.blit(tbg, (panel.right - 46, hud_y + 3))
            screen.blit(sfont.render("BOSS", True, (255, 215, 0)),
                        (panel.right - 44, hud_y + 4))

        bar_w, bar_h = 160, 12
        bx, by = hud_x + 10, hud_y + 28
        ratio  = max(self._hp_display, 0) / max(self.character.max_hp, 1)
        filled = int(bar_w * ratio)
        pygame.draw.rect(screen, (40, 12, 12), (bx, by, bar_w, bar_h), border_radius=5)
        if filled > 0:
            hp_c = ((60, 200, 60) if ratio > 0.5 else
                    (220, 180, 0) if ratio > 0.25 else (220, 40, 40))
            pygame.draw.rect(screen, hp_c, (bx, by, filled, bar_h), border_radius=5)
        pygame.draw.rect(screen, (130, 130, 130), (bx, by, bar_w, bar_h), 1, border_radius=5)
        screen.blit(font.render(
            f"{max(0, int(self._hp_display))}/{self.character.max_hp}", True, WHITE),
            (bx + 2, by - 1))

        screen.blit(sfont.render(
            ELEMENT_NAMES_PT.get(self.character.element, self.character.element),
            True, elem_c), (hud_x + 26, hud_y + 46))


# ---------------------------------------------------------------------------
# BattleScene
# ---------------------------------------------------------------------------
class BattleScene(GameScene):
    # Personagem do jogador fica a esquerda, inimigo a direita.
    # Posicao = canto superior-esquerdo do sprite (80x80).
    PLAYER_X = 50.0
    ENEMY_X  = SCREEN_WIDTH - 50.0 - CharacterObject.SIZE   # 370.0
    CHARS_Y  = SCREEN_HEIGHT // 2 - CharacterObject.SIZE // 2   # 210.0

    def __init__(self, manager, battle, bg_color=(20, 20, 50), bg_image=None):
        super().__init__(manager)
        self.battle   = battle
        self.bg_color = bg_color
        self.bg_image = bg_image
        self.font     = pygame.font.SysFont(None, 24)
        self.message  = "Escolha uma acao!"
        self.finished = False
        self._enemy_turn_pending = False
        self._enemy_turn_timer   = 0.0
        self._particles: list[dict] = []
        self.objects: list[GameObject] = []
        self._last_summary: dict = {}
        self._death_started  = False
        self._damage_texts:  list[dict] = []
        self._screen_shake   = 0.0   # timer
        self._shake_amount   = 0.0
        self._super_flash    = 0     # alpha 0-255

        # Digitação de mensagem (estilo Pokémon)
        self._prev_message   = ""
        self._type_index     = 0
        self._type_timer     = 0.0
        # Indicador de turno
        self._turn_alpha     = 0.0
        # Partículas de morte
        self._death_particles: list[dict] = []

        # Menu de batalha
        self._menu_index = 0

        # Instancias de acao do jogador (usos persistem durante a batalha)
        self._special_action = SpecialAttackAction()
        self._defend_action  = DefendAction()
        self._heal_action    = HealAction()

        # Particulas ambientes de fundo (atmosfera elemental)
        self._ambient: list[dict] = []
        self._ambient_timer = 0.0

        self._load_characters()

        self.manager.audio.play_music("battle_theme", volume=0.50)
        self.manager.score.iniciar_batalha()

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
    def _launch_projectile(self, attacker_obj, defender_obj,
                           action: Action, is_player_attack: bool = False):
        origin = attacker_obj.position + pygame.Vector2(
            CharacterObject.SIZE // 2, CharacterObject.SIZE // 2)

        atk_elem      = attacker_obj.character.element
        def_elem      = defender_obj.character.element
        super_efetivo = element_advantage.get(atk_elem) == def_elem

        self.manager.audio.play_sfx(f"attack_{atk_elem.lower()}")
        attacker_obj.play_attack()

        def on_hit():
            result    = action.execute(attacker_obj.character, defender_obj.character)
            dano      = result["damage"]
            flash_col = ELEMENT_COLORS.get(atk_elem, WHITE)
            defender_obj.take_hit(flash_color=flash_col)
            self._spawn_impact(defender_obj.position, atk_elem)
            self.manager.audio.play_sfx("hit")
            self._screen_shake = 0.18
            self._shake_amount = min(dano / 12.0, 4.0)

            # Texto flutuante de dano
            is_special  = result.get("type") == "special"
            cor_dano    = (180, 80, 255) if is_special else (
                          (255, 220, 0) if super_efetivo else (255, 80, 80))
            self._damage_texts.append({
                "txt":   str(dano),
                "pos":   pygame.Vector2(
                    defender_obj.position.x + CharacterObject.SIZE // 2,
                    defender_obj.position.y),
                "vel":   pygame.Vector2(0, -70),
                "life":  0.9,
                "color": cor_dano,
            })

            if is_player_attack:
                nivel_combo = self.manager.score.increment_combo()
                if nivel_combo >= 2:
                    self.manager.notificacoes.adicionar(
                        f"Combo x{nivel_combo}! +{nivel_combo * 25} pts",
                        cor=(255, 200, 60), duracao=1.2)
                if super_efetivo:
                    self.manager.score.registrar_elemental()
                    self.manager.audio.play_sfx("super_effective")
                    self._super_flash  = 200
                    self._screen_shake = 0.30
                    self._shake_amount = min(dano / 10.0, 8.0)
                    self.manager.notificacoes.adicionar(
                        "Super efetivo! x1.5  +50 pts",
                        cor=(255, 230, 50), duracao=1.5)
            else:
                self.manager.score.registrar_dano_recebido(
                    dano, self.battle.player.max_hp)

            self.message = f"{result['attacker']} causou  {dano}  de dano!"

        self.objects.append(
            Projectile(origin, defender_obj, atk_elem, on_hit))

    def _spawn_ambient(self):
        """Spawna particula ambiente faint subindo da plataforma de cada personagem."""
        for char_x, elem in (
            (self.PLAYER_X, self.battle.player.element),
            (self.ENEMY_X,  self.battle.enemy.element),
        ):
            color = ELEMENT_COLORS.get(elem, (200, 200, 200))
            cx    = char_x + CharacterObject.SIZE // 2
            self._ambient.append({
                "pos":   pygame.Vector2(
                    cx + random.uniform(-28, 28),
                    self.CHARS_Y + CharacterObject.SIZE + 2),
                "vel":   pygame.Vector2(
                    random.uniform(-12, 12),
                    -random.uniform(18, 55)),
                "life":  random.uniform(1.8, 3.2),
                "total": 3.2,
                "color": color,
                "r":     random.randint(2, 4),
            })

    def _draw_ambient(self, surface: pygame.Surface):
        """Desenha particulas ambientes com curva de alpha em sino."""
        for p in self._ambient:
            t     = 1.0 - p["life"] / p["total"]   # 0 → 1 com o tempo
            alpha = int(110 * 4 * t * (1 - t))     # sobe e some suavemente
            r     = p["r"]
            s     = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            _rgb = _to_rgb(p["color"])
            pygame.draw.circle(s, (_rgb[0], _rgb[1], _rgb[2], alpha), (r, r), r)
            surface.blit(s, (int(p["pos"].x) - r, int(p["pos"].y) - r))

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

        # Voltar ao mapa ao terminar a batalha
        if self.finished and event.key == pygame.K_RETURN:
            self._voltar_ao_mapa()
            return

        # Navegacao no menu (so quando e turno do jogador)
        if not self.finished and not self.battle.is_over() and not self._enemy_turn_pending:
            if event.key in (pygame.K_LEFT,  pygame.K_a):
                self._menu_index ^= 1   # toggle coluna
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self._menu_index ^= 1
            elif event.key in (pygame.K_UP,   pygame.K_w):
                self._menu_index ^= 2   # toggle linha
            elif event.key in (pygame.K_DOWN,  pygame.K_s):
                self._menu_index ^= 2
            elif event.key == pygame.K_RETURN:
                self._confirmar_acao()

    def _confirmar_acao(self):
        """Executa a acao selecionada no menu."""
        idx = self._menu_index

        if idx == 0:   # Atacar
            self._launch_projectile(
                self.player_obj, self.enemy_obj,
                AttackAction(), is_player_attack=True)
            self._iniciar_turno_inimigo(delay=1.0)

        elif idx == 1:   # Especial
            if self._special_action.can_use():
                self._launch_projectile(
                    self.player_obj, self.enemy_obj,
                    self._special_action, is_player_attack=True)
                self._iniciar_turno_inimigo(delay=1.0)
                self.manager.notificacoes.adicionar(
                    f"Ataque Especial! ({self._special_action.uses_left} usos restantes)",
                    cor=(180, 80, 255), duracao=1.2)
            else:
                self.message = "Sem usos de Especial restantes!"

        elif idx == 2:   # Defender
            if self._defend_action.can_use():
                self._defend_action.execute(self.battle.player, self.battle.enemy)
                self.message = f"{self.battle.player.name} adotou postura defensiva!"
                self.manager.notificacoes.adicionar(
                    f"Defendendo! ({self._defend_action.uses_left} usos restantes)",
                    cor=(100, 180, 255), duracao=1.2)
                self._iniciar_turno_inimigo(delay=1.2)
            else:
                self.message = "Sem usos de Defender restantes!"

        elif idx == 3:   # Curar
            if self._heal_action.can_use():
                result = self._heal_action.execute(self.battle.player, self.battle.enemy)
                heal   = result["heal"]
                self.message = f"{self.battle.player.name} se curou em {heal} HP!"
                # Texto flutuante verde de cura
                self._damage_texts.append({
                    "txt":   f"+{heal}",
                    "pos":   pygame.Vector2(
                        self.player_obj.position.x + CharacterObject.SIZE // 2,
                        self.player_obj.position.y),
                    "vel":   pygame.Vector2(0, -60),
                    "life":  1.0,
                    "color": (80, 255, 120),
                })
                self.manager.notificacoes.adicionar(
                    f"Curado! ({self._heal_action.uses_left} usos restantes)",
                    cor=(80, 255, 120), duracao=1.2)
                self.manager.score.reset_combo()
                self._iniciar_turno_inimigo(delay=1.2)
            else:
                self.message = "Sem usos de Curar restantes!"

    def _iniciar_turno_inimigo(self, delay: float = 1.0):
        self._enemy_turn_pending = True
        self._enemy_turn_timer   = delay

    def _executar_turno_inimigo(self):
        """Pergunta a IA qual acao usar e a executa."""
        if self.battle.is_over():
            return
        action = self.battle.enemy_ai.choose_action(self.battle)

        if isinstance(action, (AttackAction, SpecialAttackAction)):
            self._launch_projectile(
                self.enemy_obj, self.player_obj,
                action, is_player_attack=False)

        elif isinstance(action, HealAction):
            result = action.execute(self.battle.enemy, self.battle.player)
            heal   = result["heal"]
            self.message = f"{self.battle.enemy.name} se recuperou em {heal} HP!"
            self._damage_texts.append({
                "txt":   f"+{heal}",
                "pos":   pygame.Vector2(
                    self.enemy_obj.position.x + CharacterObject.SIZE // 2,
                    self.enemy_obj.position.y),
                "vel":   pygame.Vector2(0, -60),
                "life":  1.0,
                "color": (80, 255, 120),
            })

        elif isinstance(action, DefendAction):
            result = action.execute(self.battle.enemy, self.battle.player)
            self.message = f"{self.battle.enemy.name} adotou postura defensiva!"

    # -----------------------------------------------------------------------
    def update(self, dt: float):
        if self.message != self._prev_message:
            self._prev_message = self.message
            self._type_index   = 0
            self._type_timer   = 0.0
        self._type_timer += dt
        self._type_index  = min(int(self._type_timer * 30), len(self.message))

        for obj in list(self.objects):
            obj.update(dt)
        self.objects = [o for o in self.objects if o.alive]

        for p in self._particles:
            p["pos"]  += p["vel"] * dt
            p["life"] -= dt
        self._particles = [p for p in self._particles if p["life"] > 0]

        # Textos flutuantes de dano / cura
        for t in self._damage_texts:
            t["pos"] += t["vel"] * dt
            t["life"] -= dt
        self._damage_texts = [t for t in self._damage_texts if t["life"] > 0]

        # Particulas ambientes
        self._ambient_timer += dt
        if self._ambient_timer >= 0.18:   # spawn a cada ~0.18s
            self._ambient_timer = 0.0
            self._spawn_ambient()
        for p in self._ambient:
            p["pos"] += p["vel"] * dt
            p["vel"].x *= 0.97
            p["life"]  -= dt
        self._ambient = [p for p in self._ambient if p["life"] > 0]

        # Partículas de morte
        for p in self._death_particles:
            p["pos"] += p["vel"] * dt
            p["life"] -= dt
        self._death_particles = [p for p in self._death_particles if p["life"] > 0]

        # VFX temporais
        if self._screen_shake > 0:
            self._screen_shake = max(0.0, self._screen_shake - dt)
        if self._super_flash > 0:
            self._super_flash = max(0, self._super_flash - int(dt * 500))

        if self._enemy_turn_pending:
            self._enemy_turn_timer -= dt
            if self._enemy_turn_timer <= 0:
                self._enemy_turn_pending = False
                self._executar_turno_inimigo()

        # Animacao de morte antes de finalizar batalha
        if self.battle.is_over() and not self.finished:
            if not self._death_started:
                self._death_started = True
                winner = self.battle.get_winner()
                if winner == self.manager.game.player:
                    self.enemy_obj.start_death_anim()
            elif self.enemy_obj.death_anim_done or not (
                    self.battle.get_winner() == self.manager.game.player):
                self._handle_battle_end()

    # -----------------------------------------------------------------------
    def draw(self, screen: pygame.Surface):
        if self._screen_shake > 0:
            tmp = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self._render(tmp)
            ox = random.randint(-int(self._shake_amount), int(self._shake_amount))
            oy = random.randint(-int(self._shake_amount) // 2,
                                 int(self._shake_amount) // 2)
            screen.fill((0, 0, 0))
            screen.blit(tmp, (ox, oy))
        else:
            self._render(screen)

    def _render(self, surface: pygame.Surface):
        self._draw_themed_background(surface)

        self._draw_arena(surface)
        self._draw_ambient(surface)

        for obj in self.objects:
            obj.draw(surface)

        # Partículas de impacto
        for p in self._particles:
            alpha = int(255 * max(p["life"], 0) / 0.7)
            alpha = max(0, min(255, alpha))
            s = pygame.Surface((p["r"] * 2, p["r"] * 2), pygame.SRCALPHA)
            _rgb = _to_rgb(p["color"])
            pygame.draw.circle(s, (_rgb[0], _rgb[1], _rgb[2], alpha), (p["r"], p["r"]), p["r"])
            surface.blit(s, (int(p["pos"].x) - p["r"], int(p["pos"].y) - p["r"]))

        # Partículas de morte
        for p in self._death_particles:
            alpha = int(255 * max(p["life"], 0) / 1.5)
            alpha = max(0, min(255, alpha))
            s = pygame.Surface((p["r"] * 2, p["r"] * 2), pygame.SRCALPHA)
            _rgb = _to_rgb(p["color"])
            pygame.draw.circle(s, (_rgb[0], _rgb[1], _rgb[2], alpha), (p["r"], p["r"]), p["r"])
            surface.blit(s, (int(p["pos"].x) - p["r"], int(p["pos"].y) - p["r"]))

        # Flash de super efetivo
        if self._super_flash > 0:
            fs = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            fs.fill((255, 255, 255, self._super_flash))
            surface.blit(fs, (0, 0))

        # Textos flutuantes de dano / cura
        f_dmg = pygame.font.SysFont(None, 34)
        for t in self._damage_texts:
            alpha = int(255 * (t["life"] / 0.9))
            s = f_dmg.render(t["txt"], True, t["color"])
            s.set_alpha(alpha)
            surface.blit(s, (int(t["pos"].x) - s.get_width() // 2,
                              int(t["pos"].y)))

        # HUDs
        self.player_obj.draw_hud(surface, 8, 8)
        self.enemy_obj.draw_hud(surface, SCREEN_WIDTH - 192, 8)
        self._draw_score_hud(surface)
        self._draw_turn_indicator(surface)
        self._draw_message_box(surface)

    def render(self, screen: pygame.Surface):
        self.draw(screen)

    # -----------------------------------------------------------------------
    def _draw_arena(self, screen):
        SIZE = CharacterObject.SIZE
        t    = pygame.time.get_ticks() / 1000.0

        for char_obj in (self.player_obj, self.enemy_obj):
            cx   = int(char_obj.position.x)
            ec   = ELEMENT_COLORS.get(char_obj.character.element, (120, 110, 160))

            # Sombra elíptica
            sh = pygame.Surface((SIZE + 16, 16), pygame.SRCALPHA)
            pygame.draw.ellipse(sh, (0, 0, 0, 70), sh.get_rect())
            screen.blit(sh, (cx - 8, int(self.CHARS_Y) + SIZE + 8))

            # Plataforma elíptica
            plat_r = pygame.Rect(cx - 4, int(self.CHARS_Y) + SIZE + 4, SIZE + 8, 12)
            pygame.draw.ellipse(screen, (45, 40, 65), plat_r)
            pulse = abs(math.sin(t * 1.8))
            glow_c = tuple(min(c + int(50 * pulse), 255) for c in ec)
            pygame.draw.ellipse(screen, glow_c, plat_r, 2)

        mid = SCREEN_WIDTH // 2
        div = pygame.Surface((2, SCREEN_HEIGHT - 120), pygame.SRCALPHA)
        div.fill((255, 255, 255, 25))
        screen.blit(div, (mid, 80))

    def _draw_score_hud(self, screen):
        """Exibe pontuacao atual da batalha e combo no centro-topo."""
        score = self.manager.score.get_battle_score()
        combo = self.manager.score.get_combo()
        f     = pygame.font.SysFont(None, 22)

        score_txt = f.render(f"Pts: {score}", True, (220, 220, 100))
        cx  = SCREEN_WIDTH // 2
        bg  = pygame.Surface((score_txt.get_width() + 12, 18), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 140))
        screen.blit(bg, (cx - score_txt.get_width() // 2 - 6, 80))
        screen.blit(score_txt, (cx - score_txt.get_width() // 2, 81))

        if combo >= 2:
            combo_txt = f.render(f"Combo x{combo}!", True, (255, 180, 40))
            screen.blit(combo_txt, (cx - combo_txt.get_width() // 2, 100))

    def _draw_themed_background(self, surface: pygame.Surface):
        elem = self.battle.enemy.element

        bg_file = _BATTLE_BG_FILES.get(elem)
        if bg_file:
            img = get_scene_image(bg_file, SCREEN_WIDTH, SCREEN_HEIGHT)
            if img:
                surface.blit(img, (0, 0))
                veil = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                veil.fill((0, 0, 0, 50))
                surface.blit(veil, (0, 0))
                return

        t    = pygame.time.get_ticks() / 1000.0
        w, h = SCREEN_WIDTH, SCREEN_HEIGHT

        _BASE = {
            "Water":    ((5,  15, 60),  (15, 50, 130)),
            "Fire":     ((55,  8,  0),  (100, 28,   5)),
            "Air":      ((22, 18, 55),  (45,  75, 130)),
            "Electric": ((8,   8, 45),  (50,  45,   8)),
            "Dark":     ((3,   2, 14),  (18,   4,  36)),
            "Grass":    ((4,  22,  4),  (15,  65,  15)),
        }
        c1, c2 = _BASE.get(elem, ((15, 15, 30), (30, 30, 60)))
        surface.fill(c1)

        for i in range(5):
            ratio = (i + 1) / 5
            mc    = tuple(int(c1[j] + (c2[j] - c1[j]) * ratio) for j in range(3))
            bnd   = pygame.Surface((w, h // 5), pygame.SRCALPHA)
            bnd.fill((*mc, 50 + i * 10))
            surface.blit(bnd, (0, h - (h // 5) * (i + 1)))

        if elem == "Water":
            for i in range(3):
                pts = [(x, int(h * 0.55 + 10 * math.sin(t * 1.2 + x * 0.018 + i * 2) + i * 28))
                       for x in range(0, w + 12, 10)]
                if len(pts) >= 2:
                    pygame.draw.lines(surface, (30 + i * 10, 110 + i * 20, 200), False, pts, 1)

        elif elem == "Fire":
            for i in range(6):
                bx2 = int((i * w / 6 + t * 30) % w)
                by2 = int(h * 0.85 - abs(math.sin(t * 1.5 + i)) * h * 0.22)
                cv  = int(160 + 95 * abs(math.sin(t * 2 + i)))
                s   = pygame.Surface((4, 4), pygame.SRCALPHA)
                pygame.draw.circle(s, (cv, cv // 3, 0, 150), (2, 2), 2)
                surface.blit(s, (bx2, by2))

        elif elem == "Electric":
            for gx in range(0, w, 50):
                a = int(18 + 12 * abs(math.sin(t * 3 + gx * 0.04)))
                ls = pygame.Surface((1, h), pygame.SRCALPHA)
                ls.fill((0, 200, 0, a))
                surface.blit(ls, (gx, 0))
            for gy in range(0, h, 50):
                a = int(18 + 12 * abs(math.sin(t * 3 + gy * 0.04)))
                ls = pygame.Surface((w, 1), pygame.SRCALPHA)
                ls.fill((0, 200, 0, a))
                surface.blit(ls, (0, gy))

        elif elem == "Dark":
            for i in range(6):
                px2 = int(w * (i / 6) + 20 * math.sin(t * 0.7 + i))
                py2 = int(h * 0.4 + 30 * math.cos(t * 0.5 + i * 1.3))
                a   = int(50 + 60 * abs(math.sin(t * 1.2 + i)))
                s   = pygame.Surface((8, 8), pygame.SRCALPHA)
                pygame.draw.circle(s, (160, 0, 220, a), (4, 4), 4)
                surface.blit(s, (px2, py2))

        elif elem == "Air":
            for i in range(3):
                cx2 = int((t * 35 + i * 220) % (w + 120)) - 60
                cy2 = 60 + i * 55
                cs  = pygame.Surface((140, 44), pygame.SRCALPHA)
                pygame.draw.ellipse(cs, (200, 215, 240, 18), (0, 10, 140, 24))
                pygame.draw.ellipse(cs, (210, 225, 250, 14), (20, 0, 100, 30))
                surface.blit(cs, (cx2, cy2))

        elif elem == "Grass":
            for i in range(4):
                lx = int((t * 22 + i * 160) % (w + 40))
                ly = int(h * 0.3 + i * 35 + 15 * math.sin(t * 0.8 + i))
                ls = pygame.Surface((6, 18), pygame.SRCALPHA)
                pygame.draw.polygon(ls, (30, 110, 30, 160), [(3, 0), (6, 18), (0, 18)])
                surface.blit(ls, (lx, ly))

    def _draw_turn_indicator(self, surface: pygame.Surface):
        if self.finished or self.battle.is_over():
            return
        t     = pygame.time.get_ticks() / 1000.0
        alpha = int(160 + 95 * abs(math.sin(t * 2.2)))
        if self._enemy_turn_pending:
            label, col = "TURNO INIMIGO", (220, 80,  80)
        else:
            label, col = "SEU TURNO",     (80,  210, 80)
        f   = pygame.font.SysFont(None, 22)
        txt = f.render(label, True, col)
        txt.set_alpha(alpha)
        surface.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, 6))

    def _spawn_death_particles(self, pos: pygame.Vector2, element: str):
        color = ELEMENT_COLORS.get(element, WHITE)
        for i in range(4):
            angle = i * math.tau / 4 - math.pi / 2
            speed = random.uniform(40, 110)
            self._death_particles.append({
                "pos":   pygame.Vector2(pos),
                "vel":   pygame.Vector2(math.cos(angle) * speed,
                                        math.sin(angle) * speed - 35),
                "life":  random.uniform(1.0, 1.8),
                "color": color,
                "r":     random.randint(4, 9),
            })

    def _draw_message_box(self, screen):
        if self.finished and self._last_summary:
            self._draw_summary_panel(screen)
            return

        box  = pygame.Rect(10, SCREEN_HEIGHT - 106, SCREEN_WIDTH - 20, 96)
        bg_s = pygame.Surface((box.w, box.h), pygame.SRCALPHA)
        bg_s.fill((0, 0, 0, 190))
        screen.blit(bg_s, (box.x, box.y))
        pygame.draw.rect(screen, (220, 220, 255), box, 2, border_radius=8)
        pygame.draw.rect(screen, (100, 100, 150),
                         box.inflate(-6, -6), 1, border_radius=6)

        font_big = pygame.font.SysFont(None, 26)
        typed    = self.message[:self._type_index]
        screen.blit(font_big.render(typed, True, WHITE), (box.x + 14, box.y + 10))

        # Triângulo ▼ piscante quando texto completo
        if self._type_index >= len(self.message) and self.message:
            tv = pygame.time.get_ticks() / 1000.0
            if math.sin(tv * 6) > 0:
                tri = pygame.font.SysFont(None, 22).render("▼", True, (200, 200, 255))
                screen.blit(tri, (box.right - 22, box.bottom - 22))

        if not self.finished and not self._enemy_turn_pending and not self.battle.is_over():
            self._draw_battle_menu(screen, box)
        elif self.finished:
            tip = pygame.font.SysFont(None, 22).render(
                "ENTER = voltar ao mapa", True, (160, 200, 160))
            screen.blit(tip, (box.x + 14, box.y + 70))

    def _draw_battle_menu(self, screen, box: pygame.Rect):
        """Grade 2×2 no lado direito da caixa de mensagem."""
        f    = pygame.font.SysFont(None, 20)
        sf   = pygame.font.SysFont(None, 16)
        t    = pygame.time.get_ticks() / 1000.0
        ec   = ELEMENT_COLORS.get(self.battle.player.element, (180, 180, 255))

        usos_info = [
            None,
            (self._special_action.uses_left, SpecialAttackAction.MAX_USES),
            (self._defend_action.uses_left,  DefendAction.MAX_USES),
            (self._heal_action.uses_left,    HealAction.MAX_USES),
        ]
        _ICONS = ["Atq", "Esp", "Def", "Cur"]

        btn_w, btn_h = 148, 32
        col_x = [box.x + box.w - 312, box.x + box.w - 156]
        row_y = [box.y + 30, box.y + 64]

        # Dica elemental acima da grade
        if self._menu_index in (0, 1):
            atk = self.battle.player.element
            dfn = self.battle.enemy.element
            if element_advantage.get(atk) == dfn:
                ht, hc = "Super Efetivo!", (60, 220, 60)
            elif element_advantage.get(dfn) == atk:
                ht, hc = "Pouco Efetivo...", (160, 160, 160)
            else:
                ht, hc = "", WHITE
            if ht:
                screen.blit(sf.render(ht, True, hc), (col_x[0], box.y + 14))

        for i, label in enumerate(_MENU_LABELS):
            col_i, row_i = i % 2, i // 2
            bx2 = col_x[col_i]
            by2 = row_y[row_i]
            sel = (i == self._menu_index)

            info    = usos_info[i]
            sem_uso = info is not None and info[0] == 0

            scale = 1.0 + 0.04 * abs(math.sin(t * 4)) if sel else 1.0
            sw    = int(btn_w * scale)
            sh    = int(btn_h * scale)
            bx3   = bx2 - (sw - btn_w) // 2
            by3   = by2 - (sh - btn_h) // 2

            if sel:
                gs = pygame.Surface((sw + 6, sh + 6), pygame.SRCALPHA)
                pygame.draw.rect(gs, (*ec, 40), (0, 0, sw + 6, sh + 6), border_radius=6)
                screen.blit(gs, (bx3 - 3, by3 - 3))
                pygame.draw.rect(screen, (60, 60, 130), (bx3, by3, sw, sh), border_radius=5)
                pygame.draw.rect(screen, ec,            (bx3, by3, sw, sh), 2, border_radius=5)
                cor_txt = tuple(min(c + 60, 255) for c in ec)
                cx4, cy4 = bx3 + sw // 2, by3 + 7
            else:
                pygame.draw.rect(screen, (25, 25, 55), (bx2, by2, btn_w, btn_h), border_radius=5)
                pygame.draw.rect(screen, (70, 70, 100), (bx2, by2, btn_w, btn_h), 1, border_radius=5)
                cor_txt = (120, 120, 120) if sem_uso else (200, 200, 200)
                cx4, cy4 = bx2 + btn_w // 2, by2 + 7

            icon_s = f.render(_ICONS[i], True, cor_txt)
            lbl_s  = f.render(label,     True, cor_txt)
            screen.blit(icon_s, (cx4 - icon_s.get_width() // 2 - 26, cy4))
            screen.blit(lbl_s,  (cx4 - lbl_s.get_width()  // 2 +  8, cy4))

            if info is not None:
                tu = sf.render(f"{info[0]}/{info[1]}", True,
                               (200, 200, 200) if sel else (140, 140, 140))
                screen.blit(tu, (cx4 - tu.get_width() // 2, cy4 + 14))

    def _draw_summary_panel(self, screen):
        """Painel de resultado exibido ao fim da batalha antes de voltar ao mapa."""
        s   = self._last_summary
        box = pygame.Rect(20, SCREEN_HEIGHT - 200, SCREEN_WIDTH - 40, 178)
        bg  = pygame.Surface((box.w, box.h), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 210))
        screen.blit(bg, (box.x, box.y))
        cor_borda = (255, 215, 0) if "Vitoria" in self.message else (200, 80, 80)
        pygame.draw.rect(screen, cor_borda, box, 2, border_radius=8)

        fb  = pygame.font.SysFont(None, 26)
        fsm = pygame.font.SysFont(None, 21)
        x, y = box.x + 14, box.y + 10

        screen.blit(fb.render(self.message, True, WHITE), (x, y));  y += 24

        pygame.draw.line(screen, (100, 100, 130),
                         (x, y), (box.right - 14, y));  y += 6

        col_esq = [
            (f"Inimigo derrotado:  +{s.get('base_inimigo', 0)}", (200, 220, 255)),
            (f"Bonus elemental:    +{s.get('bonus_elemental', 0)}", (255, 230, 80)),
            (f"Bonus combo:        +{s.get('bonus_combo', 0)}", (255, 180, 40)),
            (f"Penalidades:        -{s.get('penalidades', 0)}", (255, 100, 100)),
        ]
        col_dir = [
            (f"Combo max: x{s.get('max_combo', 0)}", (200, 200, 200)),
            (f"Tempo:     {s.get('tempo_s', 0)}s  x{s.get('mult_tempo', 1)}", (200, 200, 200)),
            (f"HP final:  {s.get('hp_final', '?')}  x{s.get('mult_hp', 1)}", (200, 200, 200)),
        ]
        for i, (txt, cor) in enumerate(col_esq):
            screen.blit(fsm.render(txt, True, cor), (x, y + i * 18))
        for i, (txt, cor) in enumerate(col_dir):
            screen.blit(fsm.render(txt, True, cor),
                        (box.x + box.w // 2 + 10, y + i * 18))

        y += max(len(col_esq), len(col_dir)) * 18 + 4
        pygame.draw.line(screen, (100, 100, 130),
                         (x, y), (box.right - 14, y));  y += 6

        total_txt = fb.render(
            f"Pontos nesta batalha: {s.get('score_batalha', 0)}    "
            f"Total: {s.get('total', 0)}",
            True, (255, 215, 0))
        screen.blit(total_txt, (x, y));  y += 24

        back = fsm.render("ENTER = voltar ao mapa", True, (160, 200, 160))
        screen.blit(back, (x, y))

    # -----------------------------------------------------------------------
    def _handle_battle_end(self):
        self.manager.audio.stop_music(fade_ms=800)
        winner = self.battle.get_winner()
        player = self.manager.game.player

        if winner == player:
            self.manager.audio.play_sfx("victory")
            self.manager.audio.play_sfx("defeat")
            self._spawn_death_particles(
                self.enemy_obj.position + pygame.Vector2(
                    CharacterObject.SIZE // 2, CharacterObject.SIZE // 2),
                self.battle.enemy.element)
            self._last_summary = self.manager.score.finalizar_batalha(
                self.battle.enemy, player.hp, player.max_hp)
            self.manager.game.handle_victory(self.battle.enemy)

            if self.manager.game.state == GameState.GAME_COMPLETE:
                self.message = "Vitoria! Voce venceu o jogo!"
                self.manager.notificacoes.adicionar(
                    f"+{self._last_summary['score_batalha']} pontos!",
                    cor=(255, 215, 0), duracao=3.0, destaque=True)
                self.finished = True
                # Vai para a VictoryScene apos o jogador pressionar ENTER
                self._pending_victory = True
            else:
                self.message = "Vitoria!"
                self.manager.notificacoes.adicionar(
                    f"+{self._last_summary['score_batalha']} pontos!",
                    cor=(255, 215, 0), duracao=3.0, destaque=True)
                self.finished = True
        else:
            self.manager.audio.play_sfx("defeat")
            self.manager.game.state = GameState.GAME_OVER
            # Va direto para GameOverScene
            from meu_jogo.cenas.game_over_scene import GameOverScene
            total = self.manager.score.get_total_score()
            self.manager.scene_manager.change_scene(
                GameOverScene(self.manager, total_score=total))

    def _voltar_ao_mapa(self):
        """Chamado quando o jogador pressiona ENTER apos a batalha."""
        if getattr(self, "_pending_victory", False):
            from meu_jogo.cenas.victory_scene import VictoryScene
            summ = {
                "total":    self.manager.score.get_total_score(),
                "batalhas": "todos",
            }
            self.manager.scene_manager.change_scene(
                VictoryScene(self.manager, summary=summ))
            return

        player = self.manager.game.player
        if not player.is_alive():
            player.hp = player.max_hp
        # Volta ao overworld (não à arena de onde a batalha começou)
        self.manager.map_manager.request_map_change("MUNDO_ABERTO", 20, 25)
        from meu_jogo.cenas.campo_de_treino import CampoDeTreinoScene
        self.manager.scene_manager.change_scene(
            CampoDeTreinoScene(self.manager))
