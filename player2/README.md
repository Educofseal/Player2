# Player2 — Interface Flet

Interface estilo Tinder para o sistema de recomendação Player2,
construída com [Flet](https://flet.dev).

## Estrutura do projeto

```
player2/
├── requirements.txt
├── usuarios.json                        ← base de dados de usuários
└── src/
    ├── main.py                          ← entry point (Flet app + router)
    ├── core/
    │   ├── user.py                      ← entidade User
    │   ├── edge.py                      ← aresta ponderada
    │   └── graph.py                     ← grafo lista de adjacência
    ├── algorithms/
    │   ├── dijkstra.py                  ← menor caminho (maior afinidade)
    │   ├── bfs.py                       ← níveis de separação
    │   └── dfs.py                       ← exploração + componentes
    ├── services/
    │   ├── recommendation_service.py    ← orquestra algoritmos
    │   └── registration_service.py      ← cadastro de novo usuário ✨ NOVO
    ├── io/
    │   └── file_reader.py               ← parsing JSON
    └── ui/                              ← ✨ NOVO — interface Flet
        ├── theme.py                     ← cores, fontes, helpers visuais
        ├── register_view.py             ← tela de cadastro
        ├── swipe_view.py                ← tela de swipe (cards + like/pass)
        └── matches_view.py              ← tela de matches
```

## Fluxo da interface

```
/register  →  /swipe  →  /matches
   ↑               ↓
   └───────────────┘  (voltar)
```

1. **/register** — Novo usuário digita nome e seleciona interesses.
   O `RegistrationService` valida, cria o `User`, insere no grafo e reconstrói arestas.

2. **/swipe** — Cards ordenados pelo **Dijkstra** (menor custo = maior afinidade).
   - 💜 Like → registra match + exibe dialog de match
   - ✕ Pass → próximo perfil
   - ↩ Undo → desfaz último swipe
   - ⭐ Super → Like especial

3. **/matches** — Lista de todos os usuários curtidos, com interesses em comum e custo Dijkstra.

## Como rodar

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Executar
cd src
python main.py
```

A janela abre em modo desktop (430×820 px).
Para rodar no browser: `flet run --web src/main.py`

## Requisitos

- Python 3.9+
- flet >= 0.21.0
