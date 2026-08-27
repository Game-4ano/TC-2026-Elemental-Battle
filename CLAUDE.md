# PROMPT — TRIMESTRE 3: MENU, HISTÓRICO DE PONTUAÇÃO, NOME DO JOGADOR E SAIR

> Workstream de **correção de requisitos obrigatórios do Trimestre 3** (do `0jogo.pdf`).
> Não é polimento visual — são requisitos binários que o professor cobra explicitamente.
> Trabalhe **uma fase por vez** e **PARE** ao final de cada uma para eu confirmar.

---

## CONTEXTO

Projeto: **Elemental Battle** (Python + Pygame, disciplina Tópicos em Computação).
Cenas existentes: `MenuScene`, `CampoDeTreinoScene`, `BattleScene`, `GameOverScene`, `VictoryScene`.
`GameScene` é a classe-base polimórfica (`handle_event`, `update(dt)`, `draw(screen)`, `render(screen)`).

APIs conhecidas do `manager` (confirmar exatas na Fase 0):
- `self.manager.save` → instância de `SaveSystem` (`save_highscore(score)`, `load_highscore()`)
- `self.manager.scene_manager.change_scene(SceneClass(self.manager))`
- `self.manager.audio.play_sfx(chave)` / `play_music(chave, volume=...)`
- `self.manager.notificacoes.adicionar(texto, cor=..., duracao=...)`
- `self.manager.game.player` (tem `.element`, `.weakness`)
- `config`: `SCREEN_WIDTH`, `SCREEN_HEIGHT`, `WHITE`, `BLACK`

### Lacunas identificadas (o que este prompt resolve)
1. **`SaveSystem` guarda só um inteiro** (`{"highscore": N}`) — não salva o **nome** do jogador (requisito explícito do T3).
2. **Não há tela de histórico/ranking** — o menu só mostra "Recorde: N" (um número), não uma lista de jogadores.
3. **Não há item "Sair"** no menu de título (o professor lista "sair" ao lado de "iniciar").
4. **Retorno ao menu após o fim** — a confirmar se `VictoryScene`/`GameOverScene` voltam ao `MenuScene`.

Já está OK (não mexer): item de **Créditos** (existe modal + rodapé no `MenuScene`), iniciar o jogo, seleção de elemento.

---

## REGRAS GLOBAIS (valem para TODAS as fases)

1. **Somente edições cirúrgicas com `str_replace`.** Nada de reescrever arquivo inteiro (exceto `save_system.py`, que é pequeno e será substituído por versão nova compatível — ainda assim, mantenha assinaturas públicas antigas).
2. **Zero novas dependências.** Só `pygame` + stdlib (`json`, `os`, `datetime`).
3. **OO/herança/polimorfismo obrigatórios.** Toda tela nova herda de `GameScene`. A captura de nome deve ser uma **classe reutilizável** (usada por Victory e GameOver — não duplicar).
4. **Comentários em português**, no mesmo estilo do código atual.
5. **Constantes de ajuste** (nº de entradas no ranking, tamanho máx. do nome, etc.) vão em `core/config.py` — em nenhum outro lugar.
6. **Não quebrar nada existente**: menu, batalha, áudio, score, save, SmartAI, fluxo Menu → Overworld → Batalha → GameOver/Victory.
7. **`load_highscore()` deve continuar funcionando** exatamente como hoje (o `MenuScene._draw_titulo` chama `self.manager.save.load_highscore()` e espera um `int`).
8. Ao final de cada fase, escreva um resumo curto (3–8 linhas) e **PARE** com `>>> AGUARDANDO CONFIRMAÇÃO <<<`.

---

## FASE 0 — AUDITORIA (NÃO EDITAR NADA)

Objetivo: mapear o que existe antes de tocar no código. **Somente leitura + relatório.**

Leia e reporte (com nº de linha quando útil):

1. **`meu_jogo/core/save_system.py`** — formato atual do JSON e todos os métodos. (Já sei que é `{"highscore": N}`; confirme.)
2. **Onde `SaveSystem` é instanciado** e ligado a `self.manager.save` (provavelmente no `GameManager`/`core/game.py`). Confirme o atributo exato.
3. **`meu_jogo/cenas/gameover_scene.py`** e **`meu_jogo/cenas/victory_scene.py`**:
   - Elas **voltam ao `MenuScene`** ao final? Como (tecla? timer? `change_scene`?)?
   - Onde está a **pontuação final** da partida? (nome do atributo/objeto — `ScoreSystem`? `player.score`?)
   - Elas **chamam `save_highscore`** hoje? Onde?
   - Estrutura de `handle_event`/`update`/`draw` de cada uma.
4. **Quem chama `save_highscore`** em todo o projeto (grep). Preciso saber todos os call sites antes de mudar a assinatura.
5. **Como o jogo é encerrado** no main loop (`core/game.py` ou `game_manager`): existe flag tipo `self.running = False`? O loop já trata `pygame.QUIT`? (Isso define como implementar o "Sair".)
6. **Convenção de pastas para UI/helpers** — existe algo tipo `meu_jogo/ui/` ou `meu_jogo/cenas/widgets/`? (Define onde criar o widget de entrada de nome.)
7. Confirme se há **`ScoreSystem`** e como pegar o **score final** de uma run.

**PARE.** Entregue o relatório e um plano de 1 linha por fase confirmando os pontos de ancoragem. Não edite nada.

`>>> AGUARDANDO CONFIRMAÇÃO <<<`

---

## FASE 1 — `SaveSystem`: ranking com nome + migração do formato antigo

Substituir o `save_system.py` por uma versão que guarda uma **lista de entradas** com nome, mantendo 100% de compatibilidade com `load_highscore()`.

Novo formato do JSON (`~/.elemental_battle/highscore.json`):
```json
{ "scores": [ {"nome": "ART", "pontos": 1286, "data": "2026-08-26"}, ... ] }
```

Métodos da classe `SaveSystem` (manter o nome da classe):
- `save_score(self, nome: str, pontos: int) -> int` — insere a entrada, ordena por `pontos` desc, corta em `MAX_HISCORES` (config), grava, e retorna a **posição (rank, 1-based)** da entrada, ou `0` se não entrou no ranking.
- `load_scores(self) -> list[dict]` — retorna a lista ordenada (desc), já migrando o formato antigo se necessário (ver abaixo). Lista vazia se não houver arquivo.
- `load_highscore(self) -> int` — **manter assinatura**; retorna `max(pontos)` das entradas, ou `0`. (É o que o menu usa.)
- `save_highscore(self, score: int) -> bool` — **manter como shim de compatibilidade**: chama internamente `save_score("---", score)` (ou o que a Fase 0 indicar) e retorna `True` se entrou no ranking. NÃO remover, porque a Fase 0 pode ter achado call sites que dependem dele — só substituiremos esses call sites na Fase 2.
- `qualifica(self, pontos: int) -> bool` — retorna `True` se `pontos` entraria no top `MAX_HISCORES` (usado para decidir se pede nome).

Migração (dentro de `load_scores`): se o JSON tiver a chave antiga `"highscore"` e **não** tiver `"scores"`, converter para `[{"nome": "---", "pontos": <N>, "data": <hoje>}]` e regravar. Nunca perder o recorde antigo.

Robustez: `try/except` em torno de leitura (arquivo inexistente, JSON corrompido) retornando lista vazia — igual ao estilo atual.

Adicionar em `core/config.py`:
```python
MAX_HISCORES = 10          # nº de entradas guardadas/exibidas no ranking
MAX_NOME_LEN = 12          # tamanho máximo do nome do jogador
```

**PARE.** Mostre o `save_system.py` novo e as 2 constantes. Confirme que `load_highscore()` segue idêntico em comportamento.

`>>> AGUARDANDO CONFIRMAÇÃO <<<`

---

## FASE 2 — Widget reutilizável de entrada de nome + captura no fim da partida

### 2.1 Widget `CaixaDeNome` (classe reutilizável — evita duplicar em Victory/GameOver)
Criar em `meu_jogo/cenas/widgets/caixa_nome.py` (ou no caminho que a Fase 0 indicar). Classe simples, **não** herda de `GameScene` (é um componente, não uma cena):

```python
class CaixaDeNome:
    def __init__(self, max_len: int, on_confirm):
        """on_confirm(nome: str) é chamado quando o jogador aperta ENTER."""
    def handle_event(self, event): ...   # KEYDOWN: event.unicode imprimível -> append;
                                         # BACKSPACE -> remove; ENTER -> on_confirm(nome)
    def update(self, dt): ...            # cursor piscando
    def draw(self, screen, cx, cy): ...  # caixa + texto digitado + cursor
    @property
    def texto(self) -> str: ...
```
Detalhes: filtrar `event.unicode` para caracteres imprimíveis, respeitar `MAX_NOME_LEN`, cursor piscando via `dt`. Se o jogador confirmar vazio, usar `"---"` (ou bloquear ENTER até ter ≥1 char — escolha e comente).

### 2.2 Integração em `GameOverScene` **e** `VictoryScene`
Em ambas, ao **entrar** na cena com a pontuação final:
1. Se `self.manager.save.qualifica(pontos)` → estado `PEDINDO_NOME`: instanciar `CaixaDeNome(MAX_NOME_LEN, on_confirm=self._salvar)`, onde `_salvar(nome)` chama `self.manager.save.save_score(nome, pontos)`, guarda o rank retornado para exibir ("Novo recorde! #3"), e passa ao estado normal da tela.
2. Se **não** qualifica → segue o fluxo atual sem pedir nome.
3. Encaminhar `handle_event`/`update`/`draw` para a `CaixaDeNome` enquanto estiver em `PEDINDO_NOME` (e **não** deixar a tecla que fecha a cena disparar durante a digitação).

**Substituir** os antigos `save_highscore(...)` dessas telas (achados na Fase 0) por este novo fluxo. O shim `save_highscore` continua existindo, mas essas telas não o usam mais.

**PARE.** Mostre o widget e os diffs cirúrgicos nas duas telas. Não avance para a Fase 3.

`>>> AGUARDANDO CONFIRMAÇÃO <<<`

---

## FASE 3 — `HistoricoScene` (ranking) + item no menu

### 3.1 Nova cena `HistoricoScene(GameScene)`
Criar `meu_jogo/cenas/historico_scene.py`. Herda de `GameScene` (reforça o eixo polimórfico `GameScene`). Deve:
- No `__init__`, carregar `self.entradas = self.manager.save.load_scores()`.
- `draw`: título "Histórico de Pontuação", tabela com **posição · nome · pontos** (e data, se couber), no estilo visual do projeto (fundo gradiente + fonte `SysFont`, coerente com `MenuScene`). Mensagem "Nenhuma pontuação registrada" se vazio.
- `handle_event`: `ESC` ou ENTER volta ao menu → `change_scene(MenuScene(self.manager))`.
- Reaproveitar helpers de desenho já existentes se possível (não duplicar gradiente/estrelas à toa; se for fácil extrair, comente).

### 3.2 Item no menu de título
No `MenuScene._draw_titulo`, adicionar um botão **"Histórico"** ao lado dos já existentes ("Como jogar?", "Créditos"). Em `handle_event` (fase título), clicar nele → `change_scene(HistoricoScene(self.manager))`.

> ⚠️ O clique hoje é hardcoded com `btn1`/`btn2` (rects fixos). Para não fragmentar a lógica (o professor critica isso), **generalize** os botões da tela de título para uma **lista de `(rect, acao)`** construída uma vez, e trate o clique iterando essa lista. Isso já deixa o "Sair" da Fase 4 trivial de encaixar.

**PARE.** Mostre a `HistoricoScene` e o diff do menu.

`>>> AGUARDANDO CONFIRMAÇÃO <<<`

---

## FASE 4 — Item "Sair" no menu

Adicionar um botão/opção **"Sair"** na tela de título (usando a lista de botões criada na Fase 3).

Encerramento limpo, conforme o que a Fase 0 achou:
- Se o main loop usa uma flag (ex.: `self.manager.running = False`) → setar a flag (adicionar `manager.quit()` se fizer sentido).
- Se não houver flag acessível → `pygame.event.post(pygame.event.Event(pygame.QUIT))` (o loop já trata `QUIT`). Escolha a opção mais limpa segundo a Fase 0 e comente o motivo.

Tocar `play_sfx("menu_select")` (ou equivalente) antes de sair, se não travar o encerramento.

**PARE.** Mostre o diff.

`>>> AGUARDANDO CONFIRMAÇÃO <<<`

---

## FASE 5 — Garantir retorno ao menu após o encerramento

Com base na Fase 0:
- Se `VictoryScene`/`GameOverScene` **já** voltam ao `MenuScene`, apenas confirme (nenhuma edição) e reporte como/quando.
- Se **não** voltam (fecham o jogo ou travam), adicionar o retorno: após exibir a tela de encerramento (e depois da eventual captura de nome), em ENTER/ESC ou após um timer → `change_scene(MenuScene(self.manager))`.

Garantir que reinstanciar `MenuScene(self.manager)` é seguro (ele reinicia música de menu no `__init__` — verificar se não duplica áudio).

**PARE.** Reporte o comportamento final do fluxo Menu → … → Encerramento → Menu.

`>>> AGUARDANDO CONFIRMAÇÃO <<<`

---

## CHECKLIST FINAL (mapeado aos requisitos do T3)

Ao terminar todas as fases, valide item a item:

- [ ] **Menu iniciar/sair** — botão "Sair" funciona e encerra limpo. *(Fase 4)*
- [ ] **Tela de encerramento → volta ao menu** — Victory e GameOver retornam ao `MenuScene`. *(Fase 5)*
- [ ] **Histórico de pontuação no menu** — item "Histórico" abre `HistoricoScene` com nomes + pontos. *(Fase 3)*
- [ ] **Salvar nome do jogador no score** — `save_score(nome, pontos)` persiste nome no JSON; capturado ao fim da run. *(Fases 1–2)*
- [ ] **Créditos** — já existia (não mexer). ✔
- [ ] `load_highscore()` intacto; menu ainda mostra "Recorde: N". *(Fase 1)*
- [ ] Nenhuma dependência nova; tudo OO; comentários em PT; constantes só em `config.py`.

> Itens **SETIF / IFTECH / Mostra de Curso / "acabamentos finais"** são entregas/apresentações fora do código — não fazem parte deste workstream.