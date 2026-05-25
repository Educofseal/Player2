# Player2 🎮

> *Encontre seu player 2 — o app de matchmaking geek feito com grafos.*

Interface estilo Tinder para conectar pessoas por interesses em comum — anime, RPG, jogos, k-pop, programação e muito mais. Por baixo dos cards e dos likes, roda um sistema de grafos com Dijkstra, BFS e DFS determinando quem você deveria conhecer.

---

## Como funciona

O app modela os usuários como **nós de um grafo ponderado**. Cada aresta conecta dois usuários e tem peso inversamente proporcional ao número de interesses em comum — quanto mais afinidade, menor o custo da aresta.

A partir desse grafo, três algoritmos entram em cena:

- **Dijkstra** — ordena os perfis no feed pelo menor custo de caminho até você. Os mais compatíveis aparecem primeiro.
- **BFS** — calcula o grau de separação entre usuários (distância em níveis no grafo).
- **DFS** — explora componentes conectados e descobre grupos de afinidade.

O card de cada perfil mostra o **caminho Dijkstra** percorrido até aquela pessoa e o custo da conexão — transparência total sobre por que o app recomendou aquele match.

---

## Sistema de segurança — Triagem de Perfil 🛡️

O público geek tende a ser mais aberto, confiante e acessível socialmente — qualidades ótimas para formar comunidades, mas que também podem atrair usuários oportunistas. Para mitigar isso, o Player2 inclui um sistema silencioso de triagem comportamental integrado ao cadastro.

### Como funciona

Durante o cadastro, após escolher nome, bio e interesses, o usuário responde **12 perguntas** apresentadas como *"Seu Estilo — como você se comporta nas comunidades geek"*. As perguntas parecem uma curadoria de preferências de jogo e convivência. O usuário não sabe que está sendo avaliado.

Por baixo, cada resposta é mapeada para uma das quatro dimensões do **Short Dark Tetrad (SD4)**, escala psicométrica desenvolvida por Paulhus et al. (2021):

| Dimensão | O que avalia |
|---|---|
| **Maquiavelismo** | Tendência à manipulação planejada para ganho próprio |
| **Narcisismo** | Senso de superioridade e merecimento excessivo |
| **Psicopatia** | Frieza emocional, falta de empatia |
| **Sadismo** | Prazer com o sofrimento ou humilhação alheia |

Cada resposta tem um score de 1 a 5. A média normalizada das quatro dimensões gera um `score_risco` entre 0.0 e 1.0 salvo no perfil do usuário.

### Como o score afeta o feed

O `score_risco` é usado diretamente na construção do grafo. A fórmula de peso das arestas foi estendida:

```
peso_final = 1 / (1 + interesses_em_comum) + |risco_A - risco_B| × 0.5
```

Quanto maior a diferença de risco entre dois usuários, **mais pesada fica a aresta** entre eles. Como o Dijkstra ordena o feed pelo menor custo, perfis com scores de risco muito diferentes do seu aparecem naturalmente no final da fila — sem banimento, sem aviso, sem exposição do score.

```
risco_A = 0.05  │  risco_B = 0.08  →  peso = 0.35  ✓ aparecem cedo um para o outro
risco_A = 0.05  │  risco_C = 0.90  →  peso = 0.76  ✗ aparecem tarde um para o outro
```

### O que o usuário vê

Nada relacionado ao score. A triagem é completamente silenciosa:

- As perguntas têm linguagem neutra e geek, sem termos psicológicos.
- As opções de cada pergunta estão em ordem embaralhada, dificultando identificar a "resposta certa".
- O `score_risco` nunca é exibido na interface.
- Não há bloqueio ou rejeição de cadastro por score alto — apenas reordenação do feed.

### Referência

> Paulhus, D. L., Buckels, E. E., Trapnell, P. D., & Jones, D. N. (2021).
> *Screening for dark personalities: The Short Dark Tetrad (SD4).*
> European Journal of Psychological Assessment.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Interface | [Flet](https://flet.dev) (Flutter via Python) |
| Linguagem | Python 3.9+ |
| Algoritmos | Dijkstra, BFS, DFS — implementados do zero |
| Triagem | Short Dark Tetrad (SD4) adaptado |
| Persistência | JSON flat-file |
| Dependências | `flet >= 0.21.0` |

---

## Estrutura

```
player2/
├── usuarios.json                   ← base de dados de usuários
└── src/
    ├── main.py                     ← entry point + router Flet
    ├── core/
    │   ├── user.py                 ← entidade User (dataclass + score_risco)
    │   ├── edge.py                 ← aresta ponderada
    │   └── graph.py                ← grafo com penalidade de risco nas arestas
    ├── algorithms/
    │   ├── dijkstra.py             ← menor caminho = maior afinidade
    │   ├── bfs.py                  ← graus de separação
    │   └── dfs.py                  ← exploração + componentes
    ├── services/
    │   ├── recommendation_service.py  ← orquestra os algoritmos
    │   ├── registration_service.py    ← cadastro, validação e score de risco
    │   └── risk_service.py            ← perguntas SD4 + cálculo do score_risco
    ├── io/
    │   └── file_reader.py          ← parsing e persistência JSON
    └── ui/
        ├── theme.py                ← design system (cores, fontes, helpers)
        ├── register_view.py        ← cadastro em 15 passos (wizard step-by-step)
        ├── swipe_view.py           ← feed de cards + ações
        └── matches_view.py         ← lista de matches
```

---

## Fluxo da interface

```
/register  ──►  /swipe  ──►  /matches
                  ▲               │
                  └───────────────┘
```

1. **/register** — Wizard de 15 passos: nome → bio → interesses → 12 perguntas de perfil. Cada etapa ocupa a tela inteira. Ao responder a última pergunta, o cadastro é finalizado automaticamente.

2. **/swipe** — Feed de perfis ordenado pelo Dijkstra (com penalidade de risco). Cada card mostra afinidade em %, interesses em comum (verde) e únicos do outro usuário (roxo), além do caminho no grafo até aquela pessoa.
   - 💜 **Like** — registra o match
   - ✕ **Pass** — próximo perfil
   - ↩ **Undo** — desfaz o último swipe
   - ⭐ **Super** — like especial

3. **/matches** — Lista todos os perfis curtidos com bio, interesses em comum e custo Dijkstra. O estado persiste ao navegar entre as telas.

---

## Como rodar

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar (desktop)
python -m src.main

# Rodar no browser
flet run --web src/main.py
```

A janela abre em **430 × 820 px** (proporção mobile).

---

## Modelo de dados

Usuários são armazenados em `usuarios.json`:

```json
{
  "usuarios": [
    {
      "id": 1,
      "nome": "João",
      "interesses": ["anime", "jogos", "rpg", "mangá"],
      "bio": "Mestre de RPG nas noites de sexta 🧙",
      "score_risco": 0.10
    }
  ]
}
```

O peso de cada aresta é calculado como `1 / (1 + interesses_em_comum) + penalidade_de_risco`, garantindo que maior afinidade = menor custo no Dijkstra, e que perfis com scores de risco muito diferentes fiquem mais distantes no grafo.

---

## Contexto acadêmico

Projeto desenvolvido para a disciplina de **Teoria dos grafos**, com o objetivo de aplicar algoritmos clássicos de grafos em um produto com interface real. A escolha do Flet permitiu entregar uma UI mobile-first sem sair do ecossistema Python.
