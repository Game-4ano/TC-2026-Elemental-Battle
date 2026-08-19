# PROMPT_VETORES_INTERFACES — Agrupar x/y em Vector2 nas interfaces

> **Projeto:** Elemental Battle (TC-2026-ELEMENTAL-BATTLE) — Python + Pygame
> **Tipo de tarefa:** Refatoração arquitetural (OO / clareza de interfaces)
> **Executor:** Claude Code
> Leia o `CLAUDE.md` da raiz antes de começar. Respostas curtas (3–8 linhas).

---

## 0. Exigência do professor (motivo desta tarefa)

Citação literal do enunciado (`0jogo.pdf`):

> "Para unidades geométricas como ponto e vetores (exemplo posição e velocidade
> de um objeto), **não trabalhar com variáveis independentes para os eixos x e y.
> Criem uma estrutura que agrupe essas duas variáveis x e y em um único objeto.**"
>
> "Não usar números inteiros para armazenar posição (velocidade, etc). Usem
> pontos flutuantes."

**Decisão de projeto:** a "estrutura que agrupa x e y" será o **`pygame.Vector2`**
(já usado internamente, componentes float, sem dependência nova). Nenhuma classe
`Vec2` própria é necessária. Padronizamos `pygame.Vector2` em **todas as
interfaces públicas** que hoje recebem/expõem um par geométrico (posição,
velocidade, offset de câmera, coordenada de grid, delta de movimento, spawn).

**O que NÃO muda:** física (`apply_physics` já faz `position += velocity * dt`),
lógica de score/HP/níveis, áudio, save, SmartAI, fluxo de cenas. Isto é só
troca de *assinaturas* + os pontos de chamada correspondentes.

---

## 1. Regras invioláveis

1. **Apenas `str_replace` cirúrgico** — sem reescrever arquivos inteiros.
2. **Sem novas bibliotecas** — só `pygame` + stdlib.
3. **Comentários em português preservados.**
4. **Polimorfismo intacto:** ao mudar a assinatura de um método da base (ex.
   `Tile.draw`), **todos os overrides das subclasses e o(s) ponto(s) de chamada
   mudam na MESMA fase.** Nunca deixar base e filha com assinaturas divergentes
   (isso quebra LSP e o professor penaliza).
5. **Nada de shim/compat pela metade** dentro de uma mesma fase: ou migra o
   método e todos os seus usos, ou não toca.
6. **Cada fase termina com STOP** e aguarda a confirmação do Artur antes de
   seguir. As fases são independentes — dá pra parar em qualquer uma.
7. Coordenadas de grid podem viajar como `Vector2` (float) na interface e ser
   convertidas com `int(...)` **apenas no acesso à matriz** — não reintroduzir
   `grid_x`/`grid_y` como campos separados.

---

## FASE 0 — AUDITORIA (somente leitura, NÃO edite nada)

Mapeie e **liste** todas as assinaturas e atributos que hoje separam um par
geométrico em x/y. Para cada ocorrência informe: arquivo, linha, assinatura
atual e todos os pontos de chamada. Cubra no mínimo:

- `core/game_object.py` → `GameObject.__init__(self, x, y)`.
- Subclasses de `GameObject` e seus construtores (ex. `Projectile`,
  `CharacterObject` em `cenas/battle_scene.py`) e como chamam `super().__init__`.
- `core/map.py` → `Tile.draw(self, surface, x, y, size, offset_x=0, offset_y=0)`
  e **quantas subclasses** sobrescrevem `draw` (conte-as).
- `core/map.py` → `Map.get_tile_at(grid_x, grid_y)`, `Map.is_walkable(grid_x, grid_y)`,
  `Map.update_camera(player_pixel_x, player_pixel_y, dt)`, campos
  `camera_offset_x` / `camera_offset_y`, e a chamada `tile.draw(...)` em `Map.draw`.
- `PortalTile` → campos `spawn_x` / `spawn_y` (par de spawn) e onde são lidos.
- `cenas/campo_de_treino.py` → `player_grid_x` / `player_grid_y`, `_try_move(dx, dy)`,
  `_detect_region`, uso de `cmap.camera_offset_x/y`, e a montagem de `px, py`
  antes de `update_camera`.
- `data/maps_data.py` → onde `spawn_x/spawn_y` de portais são definidos (se houver).

**Entregue como saída da Fase 0:** uma tabela/lista com contagem total de
assinaturas afetadas e um plano confirmando (ou ajustando) as fases 1–5 abaixo.
Sinalize qualquer surpresa (outros pares x/y não previstos aqui). **STOP.**

---

## FASE 1 — Núcleo: `GameObject` recebe `Vector2`

**Arquivo:** `core/game_object.py` (+ construtores das subclasses)

Alvo:
```python
# ANTES
def __init__(self, x: float, y: float):
    self.position = pygame.Vector2(x, y)
    self.velocity = pygame.Vector2(0.0, 0.0)
    self.alive = True

# DEPOIS
def __init__(self, position: pygame.Vector2):
    self.position = pygame.Vector2(position)   # cópia defensiva
    self.velocity = pygame.Vector2(0.0, 0.0)
    self.alive = True
```

Atualizar **na mesma fase** todos os construtores de subclasses de `GameObject`
e suas chamadas a `super().__init__`. Ex. em `battle_scene.py`:
```python
# ANTES
super().__init__(origin.x, origin.y)
# DEPOIS
super().__init__(pygame.Vector2(origin))
```
Faça o mesmo para `CharacterObject` e qualquer outra subclasse (use a lista da
Fase 0). Se algum chamador tiver x/y soltos, monte `pygame.Vector2(x, y)` na
chamada — a *interface* passa a ser vetorial.

**Verificação:** o jogo inicia, entra em batalha, projétil voa e acerta.
**STOP.**

---

## FASE 2 — `Tile.draw` vetorial + helper reaproveitável

**Arquivo:** `core/map.py`

### 2.1 Nova interface da base + helper (reduz repetição = ponto de reuso)
```python
class Tile:
    def draw(self, surface, grid_pos: pygame.Vector2, size: int,
             camera_offset: pygame.Vector2):
        rect = self._screen_rect(grid_pos, size, camera_offset)
        ...

    def _screen_rect(self, grid_pos: pygame.Vector2, size: int,
                     camera_offset: pygame.Vector2) -> pygame.Rect:
        """Converte posição de grid (lógica) para retângulo em pixels (render)."""
        return pygame.Rect(
            int(grid_pos.x * size - camera_offset.x),
            int(grid_pos.y * size - camera_offset.y),
            size, size,
        )
```

### 2.2 Migrar TODAS as subclasses que sobrescrevem `draw`
Para cada override (a lista veio da Fase 0):
- Trocar a assinatura para
  `def draw(self, surface, grid_pos, size, camera_offset):`
- Trocar a primeira linha
  `rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)`
  por `rect = self._screen_rect(grid_pos, size, camera_offset)`.
- Onde o corpo usa `x`/`y` na matemática de animação
  (ex. `math.sin(t + x*0.6 + y*0.4)`), passar a usar
  `grid_pos.x` / `grid_pos.y`.

> A interface **pública** tem de ser vetorial. Dentro do corpo, se ajudar a
> legibilidade da matemática de animação, é permitido um unpack local
> (`gx, gy = grid_pos.x, grid_pos.y`) — mas **o rect sempre via `_screen_rect`**.

### 2.3 Atualizar o ponto de chamada em `Map.draw`
```python
# ANTES
tile.draw(surface, x, y, ts, self.camera_offset_x, self.camera_offset_y)
# DEPOIS
tile.draw(surface, pygame.Vector2(x, y), ts, self._camera_offset)
```
(O campo `_camera_offset` é criado na Fase 3; se rodar a Fase 2 isolada,
monte `pygame.Vector2(self.camera_offset_x, self.camera_offset_y)` aqui e ajuste
na Fase 3.)

**Verificação:** overworld e salas renderizam idênticos ao atual; tiles
animados (lava, gelo, cristal) continuam animando. **STOP.**

---

## FASE 3 — `Map`: offset e coordenadas como `Vector2`

**Arquivo:** `core/map.py`

### 3.1 Offset de câmera vira um vetor
Substituir os campos `camera_offset_x` / `camera_offset_y` por um único
`self._camera_offset = pygame.Vector2(0.0, 0.0)`. Onde forem lidos hoje
(`Map.draw`, `campo_de_treino`), usar `.x` / `.y`.

### 3.2 `update_camera` recebe posição em pixels como vetor
```python
# ANTES
def update_camera(self, player_pixel_x, player_pixel_y, dt=0.016):
# DEPOIS
def update_camera(self, player_pixel: pygame.Vector2, dt=0.016):
```
Reescrever o corpo usando `player_pixel.x/.y` e atualizar `self._camera_offset`
com o mesmo lerp atual (`alpha = min(1.0, 8.0 * dt)`).

### 3.3 `get_tile_at` / `is_walkable` recebem grid como vetor
```python
def get_tile_at(self, grid_pos: pygame.Vector2):
    gx, gy = int(grid_pos.x), int(grid_pos.y)
    if 0 <= gy < self.height and 0 <= gx < self.width:
        return self.tile_types.get(self.matrix[gy][gx])
    return None

def is_walkable(self, grid_pos: pygame.Vector2):
    tile = self.get_tile_at(grid_pos)
    return tile.is_walkable if tile else False
```
Atualizar **todos** os chamadores (loop de tiles em `Map.draw`, indicadores de
portal e `_try_move` em `campo_de_treino`) para passar `pygame.Vector2(...)`.

### 3.4 (Opcional, se houver) `PortalTile.spawn_x/spawn_y` → `spawn_pos: Vector2`
Se a Fase 0 confirmar spawns em x/y soltos, agrupe em `spawn_pos` e ajuste
`maps_data.py` e o `request_map_change`.

**Verificação:** câmera segue o herói suavemente; pisar em tiles funciona;
portais teleportam. **STOP.**

---

## FASE 4 — `CampoDeTreinoScene`: posição e delta como `Vector2`

**Arquivo:** `cenas/campo_de_treino.py`

- `player_grid_x` / `player_grid_y` → um único `self.player_grid = pygame.Vector2(14, 14)`.
- `_try_move(self, dx, dy)` → `_try_move(self, delta: pygame.Vector2)`; internamente
  `nova = self.player_grid + delta` e checar `is_walkable(nova)`.
- No `update`, os `if keys[...]` montam um `delta = pygame.Vector2(...)` em vez de
  `dx, dy` soltos.
- `_detect_region` usa `(int(self.player_grid.x), int(self.player_grid.y))` na
  lookup `_REGION_LOOKUP`.
- Antes de `update_camera`, montar
  `pixel = self.player_grid * TILE_SIZE + pygame.Vector2(TILE_SIZE/2, TILE_SIZE/2)`
  e chamar `update_camera(pixel, dt)`.
- Indicadores de portal: usar `self.player_grid.x/.y` e `cmap._camera_offset`.

**Verificação:** movimento nas 4 direções, animação/flip do herói, notificação de
região e indicador de portal — tudo igual ao atual. **STOP.**

---

## FASE 5 — Varredura final e conformidade

- `grep` por `offset_x`, `offset_y`, `grid_x`, `grid_y`, `player_pixel_x`,
  `_x,` `_y` remanescentes em interfaces públicas. Não deve sobrar par
  geométrico separado em assinatura.
- Confirmar que nenhum método base ficou com assinatura diferente das filhas.
- Rodar o fluxo completo: Menu → Overworld → cada um dos 4 portais → Batalha →
  Vitória/GameOver. Sem regressões.
- Resumo final (curto) do que mudou, por arquivo, para eu colar no relatório do
  professor mostrando conformidade com o quesito de vetores. **STOP.**

---

## Nota de conformidade (para o relatório)

Após esta refatoração, o projeto atende ao quesito do enunciado em dois pontos:
1. **Agrupamento x/y:** toda interface geométrica usa `pygame.Vector2` (posição,
   velocidade, offset de câmera, grid, delta, spawn) — nenhum par x/y solto.
2. **Ponto flutuante:** `Vector2` armazena componentes float; inteiros só no
   acesso à matriz (índice), não no armazenamento de posição.
E a física já seguia `posição += velocidade * dt` em `GameObject.apply_physics`.