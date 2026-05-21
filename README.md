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

## Stack

| Camada | Tecnologia |
|---|---|
| Interface | [Flet](https://flet.dev) (Flutter via Python) |
| Linguagem | Python 3.9+ |
| Algoritmos | Dijkstra, BFS, DFS — implementados do zero |
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
    │   ├── user.py                 ← entidade User (dataclass)
    │   ├── edge.py                 ← aresta ponderada
    │   └── graph.py                ← grafo lista de adjacência
    ├── algorithms/
    │   ├── dijkstra.py             ← menor caminho = maior afinidade
    │   ├── bfs.py                  ← graus de separação
    │   └── dfs.py                  ← exploração + componentes
    ├── services/
    │   ├── recommendation_service.py  ← orquestra os algoritmos
    │   └── registration_service.py    ← cadastro e validação
    ├── io/
    │   └── file_reader.py          ← parsing e persistência JSON
    └── ui/
        ├── theme.py                ← design system (cores, fontes, helpers)
        ├── register_view.py        ← tela de cadastro
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

1. **/register** — Você escolhe seu nome, escreve uma bio e seleciona seus interesses. O `RegistrationService` valida, cria o `User` e reconstrói as arestas do grafo.

2. **/swipe** — Feed de perfis ordenado pelo Dijkstra. Cada card mostra afinidade em %, interesses em comum (verde) e únicos do outro usuário (roxo), além do caminho no grafo até aquela pessoa.
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
      "bio": "Mestre de RPG nas noites de sexta 🧙"
    }
  ]
}
```

O peso de cada aresta é calculado como `1 / (1 + interesses_em_comum)`, garantindo que maior afinidade = menor custo no Dijkstra.

---

## Contexto acadêmico

Projeto desenvolvido para a disciplina de **Estruturas de Dados e Algoritmos em Grafos**, com o objetivo de aplicar algoritmos clássicos de grafos em um produto com interface real. A escolha do Flet permitiu entregar uma UI mobile-first sem sair do ecossistema Python.
