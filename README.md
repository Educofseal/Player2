# Player2 🎮

> *Encontre seu player 2: o app de matchmaking geek feito com grafos.*

Interface estilo Tinder para conectar pessoas por interesses em comum, como anime, RPG, jogos, k-pop e programação. Por baixo dos cards e dos likes, roda um sistema de grafos com Dijkstra, BFS e DFS que decide quem você deveria conhecer.

<!-- Coloque aqui um GIF ou print do feed de swipe -->

---

## Como funciona

O app modela os usuários como **nós de um grafo ponderado**. Cada aresta conecta dois usuários e tem peso inversamente proporcional ao número de interesses em comum: quanto mais afinidade, menor o custo da aresta.

```
peso = 1 / (1 + interesses_em_comum)
```

A partir desse grafo, três algoritmos entram em cena:

- **Dijkstra** ordena os perfis no feed pelo menor custo de caminho até você. Os mais compatíveis aparecem primeiro.
- **BFS** calcula o grau de separação (1º grau, 2º grau...) mostrado em cada card e no painel da sua rede.
- **DFS** encontra a sua comunidade (o componente conexo em que você está) e os interesses em alta nela.

O card de cada perfil mostra o **caminho Dijkstra** percorrido até aquela pessoa e o custo da conexão, para o usuário entender por que o app recomendou aquele match.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Interface | [Flet 1.0](https://flet.dev) (Flutter via Python), desktop ou navegador |
| Linguagem | Python 3.10+ |
| Algoritmos | Dijkstra, BFS e DFS implementados do zero |
| Persistência | JSON flat-file com escrita atômica |
| Testes | pytest |
| Fontes | Rajdhani, Space Mono e Inter, empacotadas em `assets/fonts` (licença OFL) |

---

## Estrutura

```
player2/
├── usuarios.json                   ← base de dados de usuários
├── assets/fonts/                   ← fontes locais (não dependem de internet)
├── tests/                          ← testes do backend (pytest)
└── src/
    ├── main.py                     ← entry point + rotas Flet
    ├── core/
    │   ├── user.py                 ← entidade User (dataclass)
    │   ├── edge.py                 ← aresta ponderada
    │   └── graph.py                ← grafo ponderado por afinidade
    ├── algorithms/
    │   ├── dijkstra.py             ← menor caminho = maior afinidade
    │   ├── bfs.py                  ← graus de separação
    │   └── dfs.py                  ← exploração + componentes
    ├── services/
    │   ├── recommendation_service.py  ← recomendações e insights da rede
    │   ├── registration_service.py    ← cadastro e validação
    │   └── swipe_session.py           ← fila, curtidas, desfazer e matches
    ├── io/
    │   └── user_store.py           ← leitura e gravação da base JSON
    └── ui/
        ├── theme.py                ← design system (cores, fontes, componentes)
        ├── register_view.py        ← cadastro passo a passo
        ├── swipe_view.py           ← feed de cards + gestos e atalhos
        └── matches_view.py         ← matches + painel da sua rede
```

---

## Fluxo da interface

```
/register  ──►  /swipe  ──►  /matches
                  ▲               │
                  └───────────────┘
```

1. **/register**: wizard de 3 passos (nome, bio e interesses), com botão de voltar e Enter para avançar. Se o nome digitado já tiver perfil, aparece **Entrar como ...** para continuar de onde parou.

2. **/swipe**: feed de perfis ordenado pelo Dijkstra. Cada card mostra afinidade em %, grau de separação, interesses em comum (verde) e novos para você (roxo), além do caminho no grafo até aquela pessoa.
   - Arraste o card para a direita para curtir ou para a esquerda para passar
   - 💜 **Like** (→): registra o match
   - ✕ **Pass** (←): próximo perfil
   - ⭐ **Super** (↑): like especial, aparece primeiro nos matches
   - ↩ **Undo** (Backspace): desfaz o último swipe
   - Quando a fila acaba, dá para rever os perfis pulados

3. **/matches**: painel "Sua rede no grafo" (comunidade via DFS, conexões de 1º e 2º grau via BFS, interesses em alta) e a lista de perfis curtidos, com super likes primeiro.

As curtidas ficam salvas no `usuarios.json`: ao entrar de novo com o mesmo nome, seus matches continuam lá e quem você já curtiu não volta para o feed.

> É um projeto de demonstração: não há senha, então qualquer pessoa pode entrar com um nome já cadastrado.

---

## Como rodar

Dentro da pasta `player2/`:

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar (desktop)
python -m src.main

# Rodar no navegador
flet run --web src/main.py
```

A janela abre em **430 × 820 px** (proporção mobile). Em janelas largas o conteúdo fica centralizado.

Para testar sem mexer na base original, aponte para outro arquivo (ele é criado com dados de exemplo se não existir):

```bash
PLAYER2_DATA=/tmp/usuarios_teste.json python -m src.main
```

### Testes

```bash
pip install -r requirements-dev.txt
python -m pytest
```

---

## Modelo de dados

Usuários são armazenados em `usuarios.json`, um por linha:

```json
{
  "usuarios": [
    {
      "id": 1,
      "nome": "João",
      "interesses": ["anime", "jogos", "rpg", "mangá"],
      "bio": "Mestre de RPG nas noites de sexta 🧙",
      "curtidas": [{"id": 3, "super": false}]
    }
  ]
}
```

`curtidas` é opcional e só aparece depois que o usuário curte alguém. A gravação é atômica (arquivo temporário + troca), então uma falha no meio nunca corrompe a base.

O peso de cada aresta é `1 / (1 + interesses_em_comum)`, garantindo que maior afinidade signifique menor custo no Dijkstra.

---

## Contexto acadêmico

Projeto desenvolvido para a disciplina de **Estruturas de Dados e Algoritmos em Grafos**, com o objetivo de aplicar algoritmos clássicos de grafos em um produto com interface real. A escolha do Flet permitiu entregar uma UI mobile-first sem sair do ecossistema Python.
