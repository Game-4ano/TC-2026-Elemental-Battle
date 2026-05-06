# CLAUDE.md — Elemental Battle (TC-2026)

> **Este arquivo é a fonte única de verdade do projeto para o Claude Code.**
> Leia-o por completo na primeira mensagem de cada sessão. **NUNCA** o ignore.
> Atualize-o **somente** quando o usuário pedir explicitamente "atualize o CLAUDE.md".

---

## 1. Contexto do projeto (não pesquisar de novo)

- **Nome:** Elemental Battle
- **Disciplina:** Tópicos em Computação — TC-2026
- **Stack:** Python 3.10+, Pygame, (box2d-py opcional), stdlib. **NENHUMA outra dependência pode ser adicionada.**
- **Resolução:** 800x500 (definida em `meu_jogo/core/config.py` — `SCREEN_WIDTH=800`, `SCREEN_HEIGHT=500`, `FPS=144`, `TILE_SIZE=32`).
- **Execução:** `python -m meu_jogo.main`
- **Estilo do jogo:** Pokémon-like — overworld 2D top-down + batalhas por turno contra 4 chefes elementais.
- **Estado atual:** trimestre 2 finalizado. Sistemas que **JÁ FUNCIONAM** e **NÃO** devem ser tocados sem motivo:
  - `AudioManager` (música/SFX gerados em runtime)
  - `ScoreSystem` (combos, multiplicadores, highscore)
  - `SaveSystem` (JSON)
  - `SmartAI` (IA dos bosses)
  - `NotificationSystem` (`manager.notificacoes.adicionar(...)`)
  - Câmera com lerp em `Map.update_camera`
  - Fluxo `MenuScene → CampoDeTreinoScene → BattleScene → GameOverScene/VictoryScene`

---

## 2. Princípios de operação do Claude Code (CUSTO)

> O usuário paga pelo Claude Code por token consumido. **Eficiência é parte da entrega.**

### 2.1. Antes de qualquer mudança
1. **Sempre** liste primeiro **quais arquivos pretende ler** e **quais pretende modificar**, em uma única mensagem curta.
2. Aguarde "ok" do usuário **se a tarefa for grande** (mais de 3 arquivos novos, ou refatoração estrutural). Para ajustes pequenos, prossiga direto.
3. **NUNCA** leia o projeto inteiro. Use `grep`/`Glob` com termos específicos. Ex.: `grep -rn "ROOM_BOSS" meu_jogo/` em vez de abrir 10 arquivos "para entender".

### 2.2. Leitura de arquivos
- Leia **um arquivo por vez** e **somente as seções relevantes** (use `view` com `view_range` quando o arquivo passar de ~300 linhas).
- **NUNCA** releia um arquivo na mesma sessão se já o leu — referencie pelo nome.
- Se já leu `battle_scene.py` uma vez, não leia de novo na mesma tarefa.

### 2.3. Edições
- **Prefira `str_replace`** (edição cirúrgica) sobre reescrever o arquivo inteiro com `create_file`. Reescrever só é aceitável quando >70% do arquivo muda.
- Faça **edições pequenas e verificáveis**, não blocos gigantes.
- **NUNCA** adicione comentários óbvios estilo `# imprime na tela` — o código deve falar por si. Comentários só para o que **não** é óbvio (decisões de design, hacks, fórmulas matemáticas).

### 2.4. Respostas ao usuário
- Resposta padrão = **3 a 8 linhas**. Sem floreios, sem "Ótima pergunta!", sem repetir o que o usuário pediu.
- **Não cole o código modificado de volta na resposta.** Diga "editei `arquivo.py:linhaX` — fiz Y" e pronto. O usuário lê o diff no editor.
- Sem emojis. Sem markdown decorativo desnecessário.
- **NUNCA** rode o jogo (`python -m meu_jogo.main`) para "testar" — o usuário roda. Você não tem display.
- Se precisar testar lógica isolada (ex.: cálculo de dano), use `python -c "..."`.

### 2.5. Stop conditions (pare de trabalhar imediatamente se):
- O usuário disser "para", "stop", "chega", "espera".
- Você for fazer a mesma edição pela 3ª vez (= está em loop, peça ajuda).
- Você precisar adicionar uma dependência nova (= peça permissão antes).
- Um arquivo passar de 800 linhas após sua edição (= peça para dividir em vez de inflar).

---

## 3. Estrutura do projeto (decoreba — não precisa explorar)

```
meu_jogo/
├── main.py                          # entrypoint, só chama GameManager
├── core/
│   ├── config.py                    # constantes (SCREEN_WIDTH=800, etc)
│   ├── game_manager.py              # loop principal
│   ├── scene_manager.py             # troca de cenas
│   ├── game_scene.py                # base abstrata de cena
│   ├── game_object.py               # base de entidade visual
│   ├── game_state.py                # enum de estados
│   ├── battle.py                    # turn loop
│   ├── elements.py                  # tabela de vantagens
│   ├── map.py                       # Tile, Map, MapManager, PortalTile
│   ├── notificacao.py               # NotificationSystem
│   ├── score_system.py              # pontuação
│   ├── save_system.py               # highscore JSON
│   └── audio_manager.py             # música/SFX
├── cenas/
│   ├── menu_scene.py                # tela inicial + escolha de elemento
│   ├── campo_de_treino.py           # overworld
│   ├── battle_scene.py              # tela de batalha (CharacterObject, Projectile, etc)
│   ├── game_over_scene.py
│   └── victory_scene.py
├── entidades/
│   ├── character.py                 # Character (hp, damage, etc) — take_damage AQUI
│   ├── acoes.py                     # Action, AttackAction, SpecialAttackAction, DefendAction, HealAction
│   ├── ai_entidade.py               # BasicAI
│   └── smart_ai.py                  # SmartAI dos bosses
├── data/
│   ├── characters_data.py           # hydra, thunder_beast, storm_eagle, magma_titan, ROOM_BOSS
│   └── maps_data.py                 # MUNDO_ABERTO_MATRIX, SALA_BATALHA_*_MATRIX, ALL_MAP_DATA
├── midia/
│   ├── sprites/
│   │   ├── sprite_factory.py        # pixel art programática (matrizes 16x16 + palette)
│   │   └── animated_sprite.py       # AnimatedSprite (frame-a-frame)
│   ├── sfx/
│   ├── music/
│   └── gerar_audio_placeholder.py
└── utils/
```

> Se um arquivo não está nessa árvore, ele provavelmente **não existe ainda** — não invente caminhos.

---

## 4. Convenções obrigatórias (estilo)

- **OO com herança/polimorfismo é REQUISITO da disciplina.** Toda nova entidade visual herda de `GameObject`. Toda nova cena herda de `GameScene`. Todo novo tile herda de `Tile`. Toda nova ação herda de `Action`.
- **dt-based:** todo `update(self, dt)` recebe delta-time em segundos. Movimentos e timers usam `dt`, **nunca** contadores de frame.
- **Sem novas libs.** Só `pygame`, `stdlib`, e `box2d-py` se já estiver lá.
- **Pixel art programática:** novos sprites seguem o padrão de `sprite_factory.py` — matriz 16x16 de strings, dict `palette` com chaves de 1 caractere, `'.'` = transparente. Não invente outro formato.
- **Animações cíclicas em tiles:** use `pygame.time.get_ticks()` para fase. Padrão:
  ```python
  phase = (pygame.time.get_ticks() % 1000) / 1000.0  # 0..1 a cada segundo
  ```
- **Cores nomeadas:** se a cor já existe em `config.py` (WHITE, BLACK, RED, etc.), use a constante.
- **Nomes em PT-BR para o usuário** (mensagens, notificações), **EN para código** (classes, funções, variáveis). Mantenha o padrão atual do projeto.

---

## 5. Bugs conhecidos a corrigir (PRIORIDADE)

### BUG-01: HP fica negativo ao morrer
**Onde:** `meu_jogo/entidades/character.py`, método `take_damage`.

**Sintoma:** Após o golpe que mata, `character.hp` vira `-12`, `-30`, etc. O HUD mostra "−12/100 HP".

**Correção esperada:**
```python
def take_damage(self, amount):
    if self.is_defending:
        amount = amount // 2
        self.is_defending = False
    real_damage = max(amount - self.defense, 0)
    self.hp = max(self.hp - real_damage, 0)   # <-- clamp em 0
    return real_damage
```

**Verificar também:**
- `battle_scene.py` → `_hp_display` (interpolação visual da barra) também deve usar `max(..., 0)`. Já tem `max(self._hp_display, 0)` na ratio mas confirme que o display textual (`self.character.hp`) também não fica negativo.
- Em `acoes.py → HealAction`, o `min(attacker.hp + heal, max_hp)` já é seguro — não mexer.

---

## 6. Roadmap completo das melhorias (ordem de execução)

> Faça **uma fase por vez**. Ao terminar cada fase, escreva uma mensagem **curta** (≤5 linhas) listando o que mudou e qual o próximo passo, e **espere o "ok"** do usuário antes de seguir.

### FASE 0 — Bugfix crítico
- [ ] BUG-01 (HP negativo) — `character.py`. Teste mental: simular dano > hp restante e confirmar que o resultado fica em 0.

### FASE 1 — Elemento SOMBRA jogável (boss + sala)
**Problema atual:** o jogador pode escolher Sombra no menu, mas não há boss de Sombra para enfrentar.

**Entregáveis:**
1. Criar `shadow_lord` em `characters_data.py`:
   ```python
   shadow_lord = Character(
       name="Shadow Lord",
       hp=140, damage=24, defense=7,
       element="Dark", weakness="Electric",  # já consistente com VANTAGENS do menu
       is_boss=True,
       sprite_key="void_emperor",  # já existe em sprite_factory!
   )
   ```
2. Adicionar em `ROOM_BOSS`:
   ```python
   "SALA_BATALHA_SOMBRA": shadow_lord,
   ```
3. Criar **portal de Sombra** no mundo aberto. Sugestão de posição: **clareira no canto NOROESTE** (linhas 2-5, colunas 2-5) — região atualmente sem portal. Símbolo da matriz: `"H"` já está em uso (HotRockTile), use `"^"` para o portal de Sombra.
4. Em `maps_data.py`, adicionar:
   ```python
   "^": PortalTile("Portal Sombra", (140, 50, 200), "SALA_BATALHA_SOMBRA", 1, 1),
   ```
5. Criar a **sala temática** `SALA_BATALHA_SOMBRA_MATRIX` 12×10 com tiles novos:
   - Novo tile `VoidFloorTile` (chão escuro com partículas roxas pulsando matematicamente)
   - Novo tile `ShadowCrystalTile` (cristal roxo, não-caminhável)
   - Novo tile `DarkMistTile` (névoa decorativa que pulsa em opacidade)
   - Saída via `"O"` apontando de volta para a posição perto do portal de Sombra no mundo aberto.
6. Adicionar `SALA_BATALHA_SOMBRA` em `ALL_MAP_DATA`.
7. **Cor de fundo da batalha** em `ROOM_BG` (campo_de_treino.py): `(20, 5, 35)` — roxo muito escuro.
8. Atualizar a tabela de elementos para que o jogador veja que "Sombra existe e tem boss" — isso é só visual no menu, sem mudar lógica.

### FASE 2 — Tela de batalha **redesenhada (PRIORIDADE MÁXIMA do usuário)**

**Problema atual:** A `BattleScene` tem fundo simples (cor sólida ou imagem com overlay), arena = retângulo + linha divisória, HUD básico.

**Entregáveis (TUDO em `cenas/battle_scene.py`, sem quebrar APIs):**

#### 2.1. Fundo temático por elemento do boss
Criar um método `_draw_themed_background(self, surface)` que desenha um fundo procedural baseado em `self.battle.enemy.element`:
- **Water (Hydra):** gradiente azul-marinho → ciano, ondas senoidais animadas no fundo, bolhas subindo
- **Fire (Magma Titan):** gradiente vermelho-escuro → laranja, brasas subindo, silhuetas de rochas no horizonte
- **Air (Storm Eagle):** gradiente roxo-noturno → azul, nuvens passando, raios distantes
- **Electric (Thunder Beast):** gradiente índigo → amarelo, grade de circuito ao fundo, pulsos elétricos
- **Dark (Shadow Lord):** gradiente preto → roxo, partículas roxas flutuando, "olhos" piscando ao fundo
- **Grass (Forest Guardian):** gradiente verde-escuro → verde-claro, folhas caindo

#### 2.2. Plataformas de combate **estilizadas** (não retângulos)
- Plataforma do jogador (esquerda) e do inimigo (direita) **com forma elíptica em perspectiva**, sombra projetada, borda iluminada na cor do elemento de quem está em cima.
- Plataforma deve ter um **glow pulsante sutil** (alpha animado).

#### 2.3. HUD **redesenhado** (caixa em estilo RPG retro)
Substituir o painel preto reto por:
- Painel com **bordas decorativas** (cantos arredondados + borda dupla na cor do elemento)
- Barra de HP **gradiente** (verde→amarelo→vermelho conforme percentual)
- **Mini-ícone elemental** ao lado do nome
- Tag "BOSS" mais chamativa (com fundo dourado)
- Painel **maior**: 180×64 px

#### 2.4. Caixa de mensagem inferior estilo "diálogo Pokémon"
Substituir a impressão simples da `self.message` por:
- Caixa retangular na parte de baixo da tela (largura total – margens), altura ~70px
- Borda dupla, fundo preto translúcido
- Texto com **animação de digitação** (caracteres aparecendo em sequência, ~30 char/s)
- Pequeno triângulo piscante "▼" no canto direito quando a mensagem termina

#### 2.5. Menu de ações **redesenhado**
O menu atual (4 botões "Atacar/Especial/Defender/Curar") deve virar:
- **Grade 2×2** de botões grandes na metade inferior direita
- Cada botão com **ícone**: ⚔️ (espada simples desenhada), ✨ (estrela), 🛡️ (escudo), 💚 (cruz médica)
- **Hover/seleção** com glow elemental + pulso de escala (1.0 → 1.05)
- **Contador de usos restantes** visível em Especial/Defender/Curar (ex: "Curar 2/2")

#### 2.6. Indicador de turno
Texto pequeno no centro-topo: **"SEU TURNO"** ou **"TURNO INIMIGO"**, com animação de fade in/out.

#### 2.7. Vantagem elemental visual
Quando o jogador seleciona uma ação, mostrar um pequeno indicador acima do menu:
- **"Super Efetivo!"** (verde) se atacante tem vantagem
- **"Pouco Efetivo..."** (cinza) se defensor é resistente
- Nada se neutro

#### 2.8. Animações de ataque mais ricas
- O projétil já existe (`Projectile`). Adicione **partículas de rastro** mais densas com cores específicas do elemento (já parcialmente existe — incremente).
- Quando bate, **screen shake escala com dano** (atualmente shake fixo). Fórmula: `shake = min(dano / 10.0, 8.0)`.
- Adicionar **flash colorido** no defensor por 0.2s (cor do elemento atacante).

#### 2.9. Animação de morte refinada
A morte atual é fade-out. Adicionar:
- 3-4 partículas elementais saindo do corpo
- Som específico de derrota (use `play_sfx("defeat")` — se não existir o áudio, o AudioManager faz fallback silencioso, então é seguro)

### FASE 3 — Mapa principal: salas de batalha **totalmente customizadas**

> Já existem 4 salas (Água, Fogo, Vento, Elétrica) + a nova de Sombra (Fase 1). O usuário quer que **cada uma seja MUITO mais distinta visualmente**.

**Para cada sala, melhorar:**

#### 3.1. SALA_BATALHA_AGUA (Hydra) — "Caverna Submersa"
- Layout em **forma de gota d'água** (não retangular padrão) usando paredes irregulares
- Bolhas decorativas ANIMADAS na borda
- Stalactites de gelo no topo (`IceStalactiteTile` novo, decorativo)
- Reflexo no chão (overlay alpha azul que desliza)

#### 3.2. SALA_BATALHA_FOGO (Magma Titan) — "Cratera Vulcânica"
- Layout circular com lava transbordando nas bordas
- **Pingos de lava** caindo do teto (partículas de cima para baixo)
- Pequena **erupção** decorativa no canto
- Overlay laranja pulsante de calor

#### 3.3. SALA_BATALHA_VENTO (Storm Eagle) — "Arena nas Nuvens"
- **Plataforma flutuante circular** no centro com vazio celeste ao redor
- Nuvens passando atrás (procedural)
- Penas caindo lentamente (já existe partícula, intensifique)
- Pequenos relâmpagos distantes ao fundo

#### 3.4. SALA_BATALHA_ELETRICA (Thunder Beast) — "Arena Eletro-Industrial"
- Padrão de placa de circuito no chão (linhas verdes em padrão grid)
- **Raios horizontais cruzando o cenário** esporadicamente (linha branca por 0.1s)
- Tubos de neon nas bordas pulsando

#### 3.5. SALA_BATALHA_SOMBRA (Shadow Lord) — "Vazio Sombrio" (NOVA)
- Chão de cristal escuro com partículas roxas flutuando
- "Olhos" desenhados nas paredes que abrem/fecham aleatoriamente
- Névoa roxa pulsando em opacidade
- Cristais roxos pontiagudos nos cantos

**Implementação:** estender o sistema `_build_themed_room` em `maps_data.py`. Se necessário, criar `_build_circular_room`, `_build_drop_room`, etc. **Reaproveite o máximo** — não crie 5 funções inteiras se uma só + parâmetro resolve.

### FASE 4 — Mapa principal (overworld): polimento

#### 4.1. Tornar cada região visualmente mais distinta
- Adicionar **decorações ambientais** que **não existem hoje**: cogumelos perto da água, ossos perto do fogo, plumas grandes perto do vento, parafusos perto do elétrico, cristais sombrios perto da sombra (Fase 1).
- Cada decoração é um tile decorativo (não-caminhável OU caminhável mas com sprite específico).

#### 4.2. Indicador visual de portal próximo
Quando o jogador estiver a ≤2 tiles de qualquer portal:
- Setas piscantes apontando para o portal
- Texto sutil acima do portal: "Pressione ↑/↓/←/→ para entrar"
- Já existe `_draw_portal_indicators` — verifique e melhore se necessário.

#### 4.3. Tinta de iluminação por região (já parcialmente existe)
Verifique `REGION_TINTS` e ajuste para que cada região tenha um tint **claramente perceptível** (mas não obtrusivo — alpha 25-40).

### FASE 5 — Tela inicial (MenuScene)

**Problema atual:** o menu funciona mas tem visual relativamente simples (estrelas + título + pentágono de elementos).

**Melhorias:**

#### 5.1. Background animado mais rico
- **Camada parallax**: 3 camadas de partículas com velocidades diferentes
- Silhuetas dos 5 bosses **passando lentamente atrás** do título (alpha baixo, 30-50)

#### 5.2. Título "ELEMENTAL BATTLE" com efeito
- **Cores dos elementos rotacionando** nas letras (Fogo→Água→Planta→Elétrico→Sombra ciclando)
- Pequeno **brilho lente** passando pela letra periodicamente

#### 5.3. Pentágono de elementos
- Quando hover, mostrar **descrição do elemento** abaixo: "Dark — Sombra. Forte contra Fogo. Fraco contra Elétrico."
- Ícone do elemento **maior** e **animado** (Fogo crepita, Água ondula, etc.)

#### 5.4. Botão "Como jogar?" e "Créditos"
Adicionar dois botões pequenos abaixo do pentágono:
- "Como jogar?" → modal com controles (setas, ENTER, ESC)
- "Créditos" → modal com nomes dos integrantes

### FASE 6 — Sprite & Animation polish

#### 6.1. Criar sprite **dedicado** para `magma_titan`
Hoje reusa `flame_hound`. Criar matriz 16×16 nova representando uma criatura **maior, de pedra ardente**, no padrão da factory.

#### 6.2. Criar sprite **dedicado** para `storm_eagle`
Hoje reusa `storm_raven`. Criar nova matriz 16×16 — pássaro grande de raios, asas mais abertas.

#### 6.3. Criar sprite **dedicado** para `shadow_lord`
Pode reusar `void_emperor` (que já é Dark) ou criar novo. **Decisão:** comece reusando `void_emperor`. Só crie novo se sobrar tempo.

#### 6.4. AnimationController (opcional — só se sobrar tempo)
Sistema centralizado de máquina de estados para sprites animados. **Não fazer** se atrasar a entrega visual.

---

## 7. Critérios de aceitação por fase

Antes de declarar uma fase pronta, **mentalmente valide:**

- ✅ O código roda sem `ImportError`, `AttributeError`, `KeyError`?
- ✅ A interface OO foi mantida (herança, polimorfismo)?
- ✅ Nenhuma dependência nova foi adicionada?
- ✅ Nenhum sistema existente foi quebrado (audio, score, save, IA)?
- ✅ Os sprites antigos continuam como fallback se algo der errado?
- ✅ O HP não vai negativo em nenhuma situação?

---

## 8. Anti-padrões PROIBIDOS

🚫 **Não fazer:**
- Renomear arquivos/classes existentes "para ficar mais bonito" — quebra imports.
- Mover funções de lugar sem necessidade técnica.
- Criar arquivos `helper.py`, `utils.py`, `common.py` genéricos — coloque a função no módulo onde ela é usada.
- Criar uma classe `Manager`, `Handler`, `Service` para encapsular 3 linhas. Se cabe em 3 linhas, é uma função.
- Adicionar `try/except: pass` para "esconder" erros. Se um erro pode acontecer, trate-o explicitamente OU deixe estourar.
- Adicionar `print` de debug no código final. Use `logging.debug` se realmente precisar.
- Reescrever um arquivo inteiro quando 5 linhas mudaram.
- "Modernizar" código que funciona (ex.: trocar `for i in range(len(x))` que está claro por list comprehension obscura).
- Implementar features que **não estão na roadmap**. Se tiver uma ideia, **sugira** ao usuário em 1 linha, não implemente.

---

## 9. Como reportar progresso

Após cada fase concluída, responda neste formato:

```
Fase X concluída.
Mudanças:
- arquivo.py: <o que mudou em 1 linha>
- arquivo2.py: <o que mudou em 1 linha>
Pendências da fase: <"nenhuma" ou lista>
Próximo: Fase X+1 — <título>. Posso prosseguir?
```

Sem screenshots. Sem narrativa longa. Sem celebração ("ficou incrível!"). Sem perguntar 3 coisas — pergunte **uma** se necessário.

---

## 10. Comandos úteis para o usuário rodar (não você)

```bash
# Rodar o jogo
python -m meu_jogo.main

# Gerar áudio placeholder (uma vez só)
python meu_jogo/midia/gerar_audio_placeholder.py

# Limpar saves
rm -f meu_jogo/save.json
```

---

## 11. Nota final ao Claude Code

Você é um **engenheiro sênior contratado para finalizar um projeto de faculdade**. O usuário tem prazo, tem orçamento de tokens limitado, e já fez 70% do trabalho. Sua função é **complementar com cirurgia**, não reescrever a tese de outra pessoa.

Quando em dúvida: **faça menos, pergunte mais (uma vez), entregue bem**.
