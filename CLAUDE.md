# PROMPT — MOVIMENTO SUAVE DO HERÓI NO OVERWORLD (Elemental Battle)

Projeto: **TC-2026-ELEMENTAL-BATTLE** — Python + Pygame.
Arquivo-alvo principal: `meu_jogo/cenas/campo_de_treino.py`.
Arquivos secundários: `meu_jogo/core/config.py`, `meu_jogo/core/map.py`,
`meu_jogo/midia/sprites/animated_sprite.py`.

---

## PROBLEMA A RESOLVER

Hoje o herói **teleporta de tile em tile**. Na `CampoDeTreinoScene.update()` existe:

```python
if moving:
    self._move_timer -= dt
    if self._move_timer <= 0:
        self._try_move(dx, dy)          # muda player_grid_x/y de uma vez
        self._move_timer = self._move_cooldown
else:
    self._move_timer = 0.0
```

Resultado visual: o sprite pula 32px de uma vez, a cada `_move_cooldown` segundos.
Somando a isso, a animação de caminhada é **resetada** (`self._hero_anim.reset()`)
sempre que o jogador solta/troca de tecla, e a câmera segue a posição **em grid**,
o que amplifica o efeito de "salto".

**Objetivo:** movimento contínuo em pixels (tween tile-a-tile), mantendo toda a
lógica de grid que já existe (colisão via `is_walkable`, portais, `on_step`,
regiões). O jogo continua sendo grid-based — só a *apresentação* passa a ser
interpolada, no estilo Pokémon GBA.

---

## REGRAS OBRIGATÓRIAS (não negociáveis)

1. **NÃO** adicionar dependências externas — apenas `pygame` + stdlib.
2. **NÃO** quebrar sistemas existentes: `AudioManager`, `ScoreSystem`,
   `SaveSystem`, `SmartAI`, `BattleScene`, `MapManager`.
3. Manter OO com herança/polimorfismo (requisito da disciplina).
4. Toda animação/movimento baseado em `dt` — nada de `pygame.time.wait` ou
   contagem de frames.
5. **Edições cirúrgicas com `str_replace`** — não reescrever arquivos inteiros.
6. Comentários de código em **português**.
7. Constantes de tuning vão para `core/config.py` — zero números mágicos
   espalhados pela cena.
8. **NÃO** mexer em lógica de dano, XP, níveis, pontuação ou fluxo de batalha.
9. `player_grid_x` / `player_grid_y` continuam sendo a **fonte da verdade** da
   posição lógica. A posição em pixels é derivada, nunca o contrário.

---

## FASE 0 — AUDITORIA (SOMENTE LEITURA — GATE OBRIGATÓRIO)

**Não edite nada nesta fase.** Leia e me reporte:

1. `meu_jogo/cenas/campo_de_treino.py` completo — em especial:
   - `__init__` (onde `player_grid_x/y`, `_move_timer`, `_move_cooldown`,
     `_hero_anim`, `_facing_left` são criados)
   - `update()`
   - `_try_move()`
   - `_enter_portal()`
   - `render()` / `draw()` — onde exatamente o herói é blitado e com quais
     coordenadas
   - `_draw_hero_shadow()`
   - `_draw_portal_indicators()`
2. `Map.update_camera` em `meu_jogo/core/map.py` — assinatura atual e se já tem
   lerp.
3. `MapManager.process_map_change` / `request_map_change` — **como a cena
   descobre que o mapa mudou** e quem escreve `player_grid_x/y` no spawn novo.
4. `meu_jogo/core/config.py` — quais constantes já existem (`TILE_SIZE`, `FPS`,
   `SCREEN_WIDTH/HEIGHT`).
5. Liste **todos** os pontos do código que leem `player_grid_x` / `player_grid_y`
   (grep no projeto inteiro). Isso é crítico: qualquer lugar que assuma que o
   herói está sempre alinhado ao grid precisa ser revisado.

**Entregue um relatório curto (máx. 40 linhas) e PARE. Aguarde meu "ok" para a
Fase 1.**

---

## FASE 1 — CONSTANTES + MÁQUINA DE ESTADO DO MOVIMENTO

### 1.1. `core/config.py`

Adicionar (com comentários em português):

```python
# --- Movimento do herói no overworld ---
HERO_MOVE_SPEED   = 110.0   # pixels por segundo (≈0.29s por tile de 32px)
HERO_WALK_FPS     = 8.0     # fps da animação de caminhada
HERO_BOB_AMPLITUDE = 1.5    # oscilação vertical sutil ao andar (px)
```

Não remover nem alterar constantes existentes.

### 1.2. Novo estado em `CampoDeTreinoScene.__init__`

Substituir `_move_timer` / `_move_cooldown` por um tween:

```python
# Posição visual em pixels (canto superior-esquerdo do tile atual)
self._pixel_x = float(self.player_grid_x * TILE_SIZE)
self._pixel_y = float(self.player_grid_y * TILE_SIZE)

# Tween de movimento entre tiles
self._is_moving   = False
self._origin_x    = self._pixel_x   # pixel de onde saiu
self._origin_y    = self._pixel_y
self._target_gx   = self.player_grid_x   # tile de destino
self._target_gy   = self.player_grid_y
self._move_progress = 0.0   # 0.0 → 1.0
self._move_duration = TILE_SIZE / HERO_MOVE_SPEED
```

### 1.3. Reescrever `update()` — máquina de estado de 2 fases

Lógica exata:

**A) Se `self._is_moving` é True → só avança o tween:**

```python
self._move_progress += dt / self._move_duration
if self._move_progress >= 1.0:
    self._move_progress = 1.0
    self._finish_move()      # chega no tile: commit + on_step + portal
```

E a cada frame recalcula a posição interpolada:

```python
t = self._move_progress
self._pixel_x = self._origin_x + (self._target_gx * TILE_SIZE - self._origin_x) * t
self._pixel_y = self._origin_y + (self._target_gy * TILE_SIZE - self._origin_y) * t
```

Use **interpolação linear**, não easing. Easing em movimento tile-a-tile contínuo
cria uma pulsação de velocidade que fica pior que o problema original.

**B) Se `self._is_moving` é False → lê o input e tenta iniciar um novo passo:**

Mantenha a leitura atual (`pygame.key.get_pressed()`, eixo único, sem diagonal,
`elif` encadeado). Se houver direção, chame `self._start_move(dx, dy)`.

### 1.4. Novos métodos

```python
def _start_move(self, dx: int, dy: int) -> bool:
    """Inicia o deslizamento para o tile vizinho, se for caminhável."""
```
- Atualiza `_facing_left` / direção (para a animação).
- `nx, ny = self.player_grid_x + dx, self.player_grid_y + dy`
- Se `not cmap.is_walkable(nx, ny)`: **não inicia o tween**, mas ainda assim
  atualiza a direção do sprite (o herói "encara" a parede). Retorna `False`.
- Se caminhável: seta `_origin_x/_origin_y` com o pixel **atual**,
  `_target_gx/_target_gy = nx, ny`, `_move_progress = 0.0`,
  `_is_moving = True`, toca `self.manager.audio.play_sfx("step", volume=0.35)`.
  Retorna `True`.

```python
def _finish_move(self):
    """Chegou no tile de destino: efetiva o grid e dispara os efeitos."""
```
- `self.player_grid_x, self.player_grid_y = self._target_gx, self._target_gy`
- `self._pixel_x = float(self.player_grid_x * TILE_SIZE)` (snap exato, mata
  acúmulo de erro de float)
- `self._is_moving = False`
- Pega o tile e dispara, **nesta ordem**: `PortalTile → self._enter_portal(tile)`,
  senão `tile.on_step(...)`.
  **Isso é uma mudança de comportamento importante:** hoje o portal dispara no
  instante do commit; agora dispara só na chegada, evitando entrar em batalha com
  o sprite no meio do caminho.
- **Encadeamento fluido:** logo depois, se ainda houver tecla de direção
  pressionada, chame `_start_move` de novo **no mesmo frame**. Sem isso, o herói
  dá uma micro-pausa a cada tile e o problema visual continua.

```python
def _sync_pixel_to_grid(self):
    """Realinha a posição em pixels ao grid (usar após troca de mapa/spawn)."""
```
- Zera o tween e coloca `_pixel_x/_pixel_y` exatamente sobre `player_grid_x/y`.
- **Chame isso sempre que `player_grid_x/y` for escrito de fora** (spawn ao
  entrar/sair de sala, retorno da batalha). Use a auditoria da Fase 0 para achar
  esses pontos. Se a cena é recriada a cada troca de mapa, basta o `__init__`
  cobrir — mas **confirme comigo antes de assumir isso**.

**PARE ao final da Fase 1 e me mostre o diff. Aguarde confirmação.**

---

## FASE 2 — RENDERIZAÇÃO NA POSIÇÃO INTERPOLADA

### 2.1. Desenho do herói

Onde hoje o herói é desenhado a partir de `player_grid_x * TILE_SIZE`, passar a
usar `self._pixel_x / self._pixel_y`:

```python
sx = int(self._pixel_x - cmap.camera_offset_x)
sy = int(self._pixel_y - cmap.camera_offset_y)
```

Use `int(...)` só no blit final — os cálculos internos permanecem em float.

### 2.2. Câmera

`update_camera` deve receber o **centro em pixels interpolado**, não o grid:

```python
px = self._pixel_x + TILE_SIZE // 2
py = self._pixel_y + TILE_SIZE // 2
self.manager.map_manager.current_map.update_camera(px, py, dt)
```

**Atenção ao double-smoothing:** com o herói já interpolado, um lerp de câmera
muito lento gera sensação de atraso/borracha. Se `update_camera` já tem lerp,
suba o fator para ~`12.0 * dt` (clampado em 1.0) ou deixe a câmera travada no
alvo. Me mostre as duas opções e eu decido.

### 2.3. Bob vertical e sombra

Substituir o pulso da sombra baseado em `pygame.time.get_ticks()` por algo
sincronizado com o passo real:

```python
# Oscilação vertical: 2 ciclos por tile (um por perna)
bob = 0.0
if self._is_moving:
    bob = -abs(math.sin(self._move_progress * math.pi * 2)) * HERO_BOB_AMPLITUDE
```

- Aplicar `bob` no `sy` do sprite (não na sombra).
- A sombra encolhe levemente quando `bob` está no pico (pé no ar) e volta ao
  tamanho normal no contato. Mantenha sutil — 2–3px de variação, no máximo.

### 2.4. Indicador de portal

`_draw_portal_indicators` usa `player_grid_x/y` para medir distância. Mantenha em
grid (a lógica de proximidade não precisa de precisão sub-tile), mas confirme que
durante o tween o indicador não pisca — se piscar, use o tile de destino
(`_target_gx/_target_gy`) quando `_is_moving` for True.

**PARE ao final da Fase 2 e me mostre o resultado. Aguarde confirmação.**

---

## FASE 3 — CONTINUIDADE DA ANIMAÇÃO

Esta fase resolve a metade do problema que **não** é o teleporte.

1. **Nunca chamar `reset()` enquanto o jogador estiver andando.** Hoje o
   `else: self._hero_anim.reset()` zera o ciclo assim que há um frame sem input.
   Nova regra:
   - Se `_is_moving` **ou** há tecla de direção pressionada → `update(dt)`.
   - Só chamar `reset()` quando o herói **parou de fato** (`not _is_moving` e sem
     input), e mesmo assim voltando para o frame de idle, não para o frame 0 da
     caminhada.
2. **Trocar de direção não reinicia o ciclo.** Ir de esquerda para direita deve
   apenas trocar `flipped` / a animação direcional, preservando `_index` e
   `_timer` da animação atual. Se `AnimatedSprite` não permitir isso hoje,
   adicione um método:
   ```python
   def copy_timing_from(self, other: "AnimatedSprite"):
       """Herda índice e timer de outra animação (troca de direção sem reset)."""
   ```
3. **Sincronizar o fps do passo com a velocidade real:** com 4 frames de
   caminhada e `HERO_MOVE_SPEED = 110`, um ciclo completo deve durar ~2 tiles.
   Calcule `fps = 4 / (2 * self._move_duration)` em vez de deixar `8.0` fixo, e
   documente a fórmula em comentário.
4. Se as animações direcionais (`hero_walk_back` / `hero_walk_front`) ainda não
   existirem na `sprite_factory`, **não as crie agora** — apenas deixe o código
   preparado com fallback para `hero_walk` + flip horizontal. Criar sprites novos
   é escopo de outro prompt.

**PARE ao final da Fase 3. Aguarde confirmação.**

---

## FASE 4 — CASOS DE BORDA

Verifique e corrija:

1. **Colisão com parede:** segurar a tecla contra uma parede não pode travar o
   jogo nem spammar o SFX de passo. O herói fica parado, encarando a direção, sem
   som repetido.
2. **Troca de mapa durante o tween:** entrar num portal só acontece em
   `_finish_move`, então o herói nunca deve trocar de cena no meio do
   deslizamento. Confirme.
3. **Volta da batalha:** ao retornar de `BattleScene` para o overworld, o herói
   precisa aparecer alinhado ao tile. Garanta `_sync_pixel_to_grid()` no caminho
   de retorno.
4. **FPS baixo / dt grande:** se `dt` for maior que `_move_duration` (freeze,
   janela arrastada), o tween deve completar sem "pular" dois tiles. Clampe
   `_move_progress` em 1.0 e processe **um** tile por frame.
5. **Regiões:** `_detect_region()` deve usar `player_grid_x/y` (grid efetivado),
   não o destino — a notificação de região dispara na chegada.

---

## FASE 5 — CHECKLIST DE TESTE (me entregue preenchido)

- [ ] Segurando uma direção, o herói desliza continuamente, sem micro-pausas
      entre tiles
- [ ] Soltar a tecla para o herói exatamente sobre um tile (nunca no meio)
- [ ] Trocar de direção não causa "engasgo" na animação
- [ ] Câmera acompanha sem tremor nem sensação de atraso
- [ ] Andar contra parede: sem travar, sem som repetido, direção correta
- [ ] Portal: entra na batalha só ao chegar no tile do portal
- [ ] Retorno da batalha: herói alinhado ao grid
- [ ] Notificação de região dispara uma única vez ao cruzar a fronteira
- [ ] Áudio, pontuação, save e batalha continuam funcionando

---

## FORMATO DAS RESPOSTAS

- Uma fase por vez. **Sempre pare no gate e espere meu "ok".**
- Máx. ~60 linhas de resposta por fase, fora o diff.
- Mostre apenas os trechos alterados, não arquivos inteiros.
- Não releia arquivos que já leu na Fase 0 dentro da mesma sessão.
- Se encontrar algo na auditoria que contradiga este prompt (ex.: a cena não é
  recriada na troca de mapa), **pare e me avise antes de improvisar**.